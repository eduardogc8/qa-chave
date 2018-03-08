import operator
from util import util


ANSWER_CANDIDATES_PARAMETERS_WEIGHT = {'doc_rank': -1, 'votes': 0.7, 'distance': -0.5, 'qw_in_passage': 1}


def answer_candidates(questions, QP, ir, NER, model_ner, loading=True):
    """Define para a lista de questoes suas respostas candidatas."""
    count = 0
    if loading:
        print('[', end=' ')
    for question in questions:

        if loading:
            if count < len(questions) / 10:
                count += 1
            else:
                print('.', end=' ')
                count = 0

        question['answer_candidates'] = []  # Lista de respostas candidatas da question
        for passage in question['passages']:  # Para cada passagem recuperado

            candidate = {'passage_text': passage['passage'], 'words': [], 'full_answer': '', 'votes': 0, 'doc_rank': passage['doc_rank']}
            #                         answer passage text, [(word, index)], 'w0 w1 w2 wn', num candiates with same answer

            last = False
            words = passage['passage'].split()
            for index in range(len(words)):
                word = util.replace_ponctutation(words[index])
                entity = passage['entitys'][index]

                if '-' in entity:  # Se eh uma entidade mencionada
                    class_entity = entity[:entity.index('-')].lower()
                    suffix = entity[entity.index('-') + 1:].lower()
                    if suffix == 'b':  # Inicio da entidade mencionada
                        if not candidate['full_answer'] == '':
                            insert_candidate(question, candidate)
                            candidate = {'passage_text': passage['passage'], 'words': [], 'full_answer': '', 'votes': 0, 'doc_rank': passage['doc_rank']}
                    if class_entity == QP.classPT(question['predict_class'].lower()):
                        candidate['words'].append((word, index))
                        candidate['full_answer'] += ' ' + word
                        candidate['full_answer'] = candidate['full_answer'].strip()
                        last = True
                    else:
                        last = False
                else:
                    if last:
                        if not candidate['full_answer'] == '':
                            insert_candidate(question, candidate)
                            candidate = {'passage_text': passage['passage'], 'words': [], 'full_answer': '', 'votes': 0, 'doc_rank': passage['doc_rank']}
                    last = False
            if not candidate['full_answer'] == '':
                insert_candidate(question, candidate)
                candidate = {'passage_text': passage['passage'], 'words': [], 'full_answer': '', 'votes': 0, 'doc_rank': passage['doc_rank']}
    if loading:
        print('. ]')
    return questions


def insert_candidate(question, candidate):
    """
    Funcao auxiliar para inserir o candidate na lista candidates da question.

    Cada candidate com a mesma full answer ira receber +1 vote, inclusive a propria candidate.
    Tambem eh calculado a distance entre as principais palavras da pergunta e a passage_text
    """
    question['answer_candidates'].append(candidate)
    for cand in question['answer_candidates']:  # Update votes
        if cand['full_answer'] == candidate['full_answer']:
            cand['votes'] += 1
    candidate_distance(question, candidate)


def candidate_distance(question, candidate):
    """
    Determina a distancia entre as principais palavras da pergunta e a resposta na passagem.

    Tambem determina o numero de palavras principais que estao no texto da passagem.
    """
    candidate['qw_in_passage'] = 0
    candidate['distance'] = 0

    count_qw = 0
    for qw in util.replace_ponctutation(question['question']).lower().split():
        if util.is_stopword(qw):  # Stopwords da questao sao desconsideradas
            continue
        else:
            ret = util.shortSentenceDistance(util.replace_ponctutation(candidate['passage_text']), qw, candidate['full_answer'])
            count_qw += 1
            if ret == -2:  # Caso a resposta nao esteja na passage eh sinal de algum problema no sistema
                print('Warning: No answer in candidate passage')
            else:
                if not ret == -1:  # Question word not in passage text
                    candidate['qw_in_passage'] += 1
                    candidate['distance'] += ret
                count_qw += 1

    if candidate['qw_in_passage'] > 0:
        candidate['distance'] = candidate['distance'] / candidate['qw_in_passage']
    if count_qw > 0:
        candidate['qw_in_passage'] = candidate['qw_in_passage'] / count_qw


def normalize_parameters(answer_candidates):
    """Normalizar parametros de cada candidato."""
    aux_dic = {}
    for parameter in ANSWER_CANDIDATES_PARAMETERS_WEIGHT:
        aux_dic[parameter] = [float('inf'), float('inf')*-1]  # [min, max]
        for candidate in answer_candidates:
            if candidate[parameter] < aux_dic[parameter][0]:
                aux_dic[parameter][0] = candidate[parameter]
            if candidate[parameter] > aux_dic[parameter][1]:
                aux_dic[parameter][1] = candidate[parameter]

    for candidate in answer_candidates:
        for parameter in ANSWER_CANDIDATES_PARAMETERS_WEIGHT:
            if aux_dic[parameter][1] - aux_dic[parameter][0] == 0:
                candidate[parameter] = 0
                continue
            candidate[parameter] = (candidate[parameter] - aux_dic[parameter][0]) / (aux_dic[parameter][1] - aux_dic[parameter][0])


def finals_answer(questions):
    """Define a resposta final."""
    interval_print = 0
    print('[', end=' ')

    for question in questions:
        if interval_print < len(questions) / 10:
            interval_print += 1
        else:
            print('.', end=' ')
            interval_print = 0
        question['final_answer'] = 'N/A'

        # Normalize os parametros de cada candidate
        normalize_parameters(question['answer_candidates'])

        # Determinar o score de cada answer candidate
        for candidate in question['answer_candidates']:
            candidate['score'] = 0
            for parameter in ANSWER_CANDIDATES_PARAMETERS_WEIGHT:
                candidate['score'] += candidate[parameter] * ANSWER_CANDIDATES_PARAMETERS_WEIGHT[parameter]

        if len(question['answer_candidates']) > 0:
            question['final_answer'] = sorted(question['answer_candidates'], key=lambda k: k['score'])[-1]['full_answer']

    print('. ]')
    return questions


def qaDistanceText(textWords, qWords, answer):
    if answer not in textWords:
        print('Answer is not in text')
        return -1, -1, -1

    distance = 0
    qWordsDistance = 0
    noMatch = 0
    for i in range(len(qWords)):
        qw = qWords[i]
        if qw in textWords:
            distance += util.shortSentenceDistance(textWords, qw, answer)
        else:
            noMatch += 1
        for j in range(i + 1, len(qWords)):
            qw2 = qWords[j]
            qWordsDistance += util.shortSentenceDistance(textWords, qw, qw2)
    return distance, qWordsDistance, noMatch


def test_answer_candidates(questions):
    """Print o recall geral dos candidates e o recall para as question com answer_type corretas."""
    total = len(questions)
    right = 0
    cc_total = 0  # Total of question with correct answer classifier
    cc_right = 0

    for question in questions:
        aux = False
        question['correct_answers_candidates'] = False
        if question['correct_answer_type']:
            cc_total += 1
            aux = True
        for answer in question['answers']:
            stop = False
            for candidate in question['answer_candidates']:
                if answer['answer'] is not None:
                    a1 = util.replace_ponctutation(answer['answer'].lower())
                    a2 = util.replace_ponctutation(candidate['full_answer'].lower())
                    if a1 in a2 or a2 in a1:
                        question['correct_answers_candidates'] = True
                        right += 1
                        stop = True
                        if aux:
                            cc_right += 1
                        break
            if stop:
                break
    print(str(total) + ' / ' + str(right))
    print('Total recall: ' + '%.3f' % ((right/total)*100)+' %')
    print('\nCorrect answer type:\n' + str(cc_total) + ' / ' + str(cc_right))
    print('Recall: ' + '%.3f' % ((cc_right/cc_total)*100)+' %')
