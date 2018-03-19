import operator
from util import util
import question_processing as QP


ANSWER_CANDIDATES_PARAMETERS_WEIGHT = {'doc_rank': -0.9, 'votes': 0.7}


def answer_candidates(questions, ir, model_ner, answer_type_filter=False, loading=True):
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

            if answer_type_filter:
                control = False
                for entity in passage['entitys']:
                    if '-' in entity:  # Se eh uma entidade mencionada
                        class_entity = entity[:entity.index('-')].lower()
                        if class_entity == QP.classPT(question['predict_class'].lower()).lower():
                            control = True
                            break
                if not control:
                    continue

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
                    if class_entity == QP.classPT(question['predict_class'].lower()).lower():
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
    #candidate_distance(question, candidate)


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
            if util.remove_acentts(candidate['full_answer'].lower()) in util.remove_acentts(question['question'].lower()):
                continue
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
    """Print o result geral dos candidates e o result para as question com answer_type corretas."""
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

        aux2 = False
        for answer in question['answers']:
            if answer['answer'] is None or answer['answer'] == '':
                continue
            stop = False
            aux2 = True
            for candidate in question['answer_candidates']:
                correct_answer = util.replace_ponctutation(answer['answer'].lower())
                system_answer = util.replace_ponctutation(candidate['full_answer'].lower())
                if correct_answer in system_answer or system_answer in correct_answer:
                    question['correct_answers_candidates'] = True
                    right += 1
                    stop = True
                    if aux:
                        cc_right += 1
                    break
            if stop:
                break
        if aux and not aux2:
            cc_total -= 1
    print(str(total) + ' / ' + str(right))
    print('Result: ' + '%.3f' % ((right/total)*100)+' %')
    print('\nCorrect answer type:\n' + str(cc_total) + ' / ' + str(cc_right))
    print('Result: ' + '%.3f' % ((cc_right/cc_total)*100)+' %')


def evaluate_questions(questions):
    """Verifica se a resposta final gerada pelo sistema esta correta."""
    for question in questions:
        question['correct_final_answer'] = False
        for answer in question['answers']:
            if answer is None or answer['answer'] is None:
                continue
            correct_answer = util.replace_ponctutation(answer['answer'].lower())
            system_answer = util.replace_ponctutation(question['final_answer'].lower())
            if correct_answer in system_answer or system_answer in correct_answer:
                question['correct_final_answer'] = True
