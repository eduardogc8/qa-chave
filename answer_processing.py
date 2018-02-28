import operator


# Retorna as lista de questoes com as respostas candidatas
def answer_candidates(questions, QP, ir, NER, model_ner, loading=True):
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
        answer_candidates = []
        for doc_id in question['retrieval']:
            doc_text = ir.documentText(doc_id)
            doc_entities = NER.predict(model_ner, doc_text)[0]
            answer = []
            last = False
            for word in zip(doc_text.split(), doc_entities):
                if '-' in word[1]:
                    class_entity = word[1][:word[1].index('-')].lower()
                    suffix = word[1][word[1].index('-')+1:].lower()
                    if suffix == 'b':
                        if len(answer) > 0:
                            answer_candidates.append(answer)
                            answer = []
                    if class_entity == QP.classPT(question['predict_class'].lower()):
                        answer.append(word)
                        last = True
                    else:
                        last = False
                else:
                    if last:
                        if len(answer) > 0:
                            answer_candidates.append(answer)
                            answer = []
                    last = False
            if len(answer) > 0:
                answer_candidates.append(answer)
                answer = []
        question['answer_candidates'] = answer_candidates
    if loading:
        print('. ]')
    return questions


# Define a resposta final
def finals_answer(questions):

    for question in questions:
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
        votes = {}
        for candidate in question['answer_candidates']:
            answer = ''
            for w in candidate:
                answer += ' ' + w[0]
            answer = answer.strip()

            if answer.lower() not in question['question'].lower():
                if answer not in votes:
                    votes[answer] = 0
                votes[answer] += 1
        if len(votes) > 0:
            question['final_answer'] = max(votes.items(), key=operator.itemgetter(1))[0]

    return questions


def test_answer_candidates(questions):
    total = len(questions)
    right = 0
    rc_total = 0  # Total of question with correct answer classifier
    rc_right = 0

    for question in questions:
        aux = False
        question['correct_answers_candidates'] = False
        if question['correct_answer_type']:
            rc_total += 1
            aux = True
        for answer in question['answers']:
            stop = False
            for candid in question['answer_candidates']:
                candidate = ''
                for c in candid:
                    candidate += ' ' + c[0]
                candidate = candidate.strip()
                if answer['answer'] is not None:
                    a1 = answer['answer'].lower().replace(',', '').replace('.', '').replace(';', '').strip()
                    a2 = candidate.lower().replace(',', '').replace('.', '').replace(';', '').strip()
                    if a1 in a2 or a2 in a1:
                        question['correct_answers_candidates'] = True
                        right += 1
                        stop = True
                        if aux:
                            rc_right += 1
                        break
            if stop: break
    print(str(total) + ' / ' + str(right))
    print('Total recall: '+ '%.3f' % ((right/total)*100)+' %')
    print('\nCorrect answer type:\n' + str(rc_total) + ' / ' + str(rc_right))
    print('Recall: '+ '%.3f' % ((rc_right/rc_total)*100)+' %')
