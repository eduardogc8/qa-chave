

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
        if len(question['answer_candidates']) > 0:
            aux = question['answer_candidates'][0]
            answer = ''
            for w in aux:
                answer += ' ' + w[0]
            question['final_answer'] = answer.strip()
        else:
            question['final_answer'] = 'N/A'
    return questions


def test_answer_candidates(questions):
    total = len(questions)
    right = 0
    for question in questions:
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
                        right += 1
                        stop = True
                        break
            if stop: break
    print(str(total) + ' / ' + str(right))
    print('Accuracy: '+ '%.3f' % ((right/total)*100)+' %')
