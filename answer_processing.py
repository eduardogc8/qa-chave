import operator
from util import util


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
        for doc_id in question['retrieval']:  # Para cada documento recuperado

            doc_text = ir.documentText(doc_id)
            doc_entities = NER.predict(model_ner, doc_text)[0]

            candidate = {'document_text': doc_text, 'words': [], 'full_answer': '', 'votes': 0}
            #            answer doc text retrieval, [(word, index)], 'w0 w1 w2 wn', num candiates with same answer

            last = False
            text_entities = zip(doc_text.split(), doc_entities)
            aux_list = list(text_entities)
            for index in range(len(aux_list)):
                word = util.replace_ponctutation(aux_list[index][0])
                entity = aux_list[index][1]

                if '-' in entity:  # Se eh uma entidade mencionada
                    class_entity = entity[:entity.index('-')].lower()
                    suffix = entity[entity.index('-') + 1:].lower()
                    if suffix == 'b':  # Inicio da entidade mencionada
                        if not candidate['full_answer'] == '':
                            insert_candidate(question['answer_candidates'], candidate)
                            candidate = {'document_text': doc_text, 'words': [], 'full_answer': '', 'votes': 0}
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
                            insert_candidate(question['answer_candidates'], candidate)
                            candidate = {'document_text': doc_text, 'words': [], 'full_answer': '', 'votes': 0}
                    last = False
            if not candidate['full_answer'] == '':
                insert_candidate(question['answer_candidates'], candidate)
                candidate = {'document_text': doc_text, 'words': [], 'full_answer': '', 'votes': 0}
    if loading:
        print('. ]')
    return questions


def insert_candidate(candidates, candidate):
    """
    Funcao auxiliar para inserir o candidate na lista candidates.

    Cada candidate com a mesma full answer ira receber +1 vote, inclusive a propria candidate.
    """
    candidates.append(candidate)
    for cand in candidates:
        if cand['full_answer'] == candidate['full_answer']:
            cand['votes'] += 1


def finals_answer(questions):
    """Define a resposta final."""
    for question in questions:
        print(str(len(questions))+'/'+str(questions.index(question)))
        question['final_answer'] = 'N/A'

        # Primeiro candidato
        '''
        if len(question['answer_candidates']) > 0:
            aux = question['answer_candidates'][0]
            answer = ''
            for w in aux:
                answer += ' ' + w[0]
            question['final_answer'] = answer.strip()
        '''

        # Mais votado
        '''
        votes = {}
        for candidate in question['answer_candidates']:
            if candidate['full_answer'].lower() not in question['question'].lower():
                if candidate['full_answer'] not in votes:
                    votes[candidate['full_answer']] = candidate['votes']
        if len(votes) > 0:
            question['final_answer'] = max(votes.items(), key=operator.itemgetter(1))[0]
        '''

        # Menor distancia
        for candidate in question['answer_candidates']:
            candidate['distance'] = 0
            for qw in util.replace_ponctutation(question['question']).lower().split():
                if util.is_stopword(qw):
                    continue
                else:
                    ret = util.shortSentenceDistance(candidate['document_text'], qw, candidate['full_answer'])
                    if ret is None:
                        ret = 30
                    candidate['distance'] += ret
            if candidate['distance'] == 0:
                candidate['distance'] = 200
        question['final_answer'] = sorted(question['answer_candidates'], key=lambda k: k['distance'])[0]['full_answer']
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
