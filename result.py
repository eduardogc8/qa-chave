# -*- coding: utf-8 -*-

import os.path
from terminaltables import AsciiTable
import time
import sys
import question_process
from operator import itemgetter
reload(sys)
sys.setdefaultencoding('utf-8')

# Local onde será salvo os arquivo de saída
path_result_file = "results/"


# Define o nome do arquivo de saída
def file_name():
    count = 1
    while os.path.isfile(path_result_file+'result_'+str(count)):
        count += 1
    return 'result_'+str(count)


# cross-validation output
def qc_procude(results):
    # Cria um novo arquivo de resultados
    file = open(path_result_file+file_name(), 'w')

    # Momento dos resultados
    p = time.strftime("%D %H:%M:%S")
    file.write(p+'\n')
    print '\nResults - Question Classification\n'+p

    classifications = []
    t_questions = 0
    t_correct = 0

    for r in results:
        pairs = sorted(r, key=lambda x: x.correct_classification)
        if len(pairs) > 0:
            count = 0

            # Detalhes de cada par
            pairs_details = [['#', 'Question', 'Correct Classification', 'Classification']]

            # Question Processing
            question_classification = []

            for pair in pairs:
                count += 1

                # Detalhes do par
                details = []
                details.append(count)
                details.append(pair.question.replace('\n', '').decode('utf-8'))
                # if len(pair.correct_answers) > 0 :
                #    #print type(pair.correct_answers[0].replace('\n',''))
                #    details.append(pair.correct_answers[0].replace('\n','').decode('utf-8'))
                # else :
                #    details.append('')
                details.append(pair.correct_classification)
                details.append(pair.question_classification)
                pairs_details.append(details)

                # Type question
                new = True
                for t in question_classification:
                    if t[0] == pair.correct_classification:
                        new = False
                        t[1] += 1
                        if pair.correct_classification == pair.question_classification:
                            t[2] += 1
                        break
                if new:
                    question_classification.append([pair.correct_classification, 0, 0, 0])
                    t = question_classification[-1]
                    t[1] += 1
                    if pair.correct_classification == pair.question_classification:
                        t[2] += 1

            # Detalhes dos pares
            # pairs_details = sorted(pairs_details, key=itemgetter(1))
            # pairs_details = [pairs_details]
            tb = AsciiTable(pairs_details)
            tb.inner_footing_row_border = False
            file.write('\nPairs\n'+tb.table+'\n')
            # print('\nPairs\n'+tb.table)

            # Classification question
            total = 0
            correct = 0
            classifications.append(question_classification)
            for t in question_classification:
                t[3] = round(float(t[2])/float(t[1]), 4)
                total += t[1]
                correct += t[2]
            question_classification = sorted(question_classification, key=itemgetter(3), reverse=True)
            question_classification = [['Classification', 'Total', 'Correct', 'Rate']] + question_classification + [
                ['', total, correct, round(float(correct)/float(total), 4)]
            ]
            t_questions += total
            t_correct += correct
            tb = AsciiTable(question_classification)
            tb.inner_footing_row_border = True
            file.write('\n'+str(results.index(r)+1)+'/'+str(len(results))+'\n'+tb.table+'\n')
            print('\n'+str(results.index(r)+1)+'/'+str(len(results))+'\n'+tb.table)
        else:
            print "No pairs for results!"

        final_results = []

        for cs in classifications:
            for c in cs:
                if c[0] not in [f[0] for f in final_results]:
                    final_results.append([c[0], 0, 0, 0])
                if len(final_results) == 0:
                    print c
                find = False
                for f in final_results:
                    if f[0] == c[0]:
                        f[1] += c[1]
                        f[2] += c[2]
                        find = True
                        break
                if not find:
                    print 'Erro Aqui c0:'+c[0]
                    print final_results  # ToDo Remover
                    print [f[0] for f in final_results]
    for f in final_results:
        f[3] = round(float(f[2])/float(f[1]), 4)
    final_results = sorted(final_results, key=itemgetter(3), reverse=True)
    final_results = [['Class', 'Total', 'Correct', 'Rate']] + final_results + [['Total', t_questions, t_correct, round(float(t_correct)/float(t_questions), 4)]]
    tb = AsciiTable(final_results)
    tb.inner_footing_row_border = True
    tb.inner_heading_row_border = True
    file.write('\nFinal Results:\n'+tb.table+'\n')
    print ('\nFinal Results:\n'+tb.table)
    file.close()


# Avalia a saída de apensa um conjunto
def produce(pairs_in):
    pairs = sorted(pairs_in, key=lambda x: x.correct_classification)
    if len(pairs) > 0:

        # Cria um novo arquivo de resultados
        file = open(path_result_file+file_name(), 'w')

        # Momento dos resultados
        p = time.strftime("%D %H:%M:%S")
        file.write(p+'\n')
        print '\nResults\n'+p

        count = 0

        # Detalhes de cada par
        pairs_details = [['#', 'Question', 'Correct Classification', 'Classification']]

        # Question Processing
        question_classification = []

        for pair in pairs:
            count += 1

            # Detalhes do par
            details = []
            details.append(count)
            details.append(pair.question.replace('\n', '').decode('utf-8'))
            # if len(pair.correct_answers) > 0 :
            #    #print type(pair.correct_answers[0].replace('\n',''))
            #    details.append(pair.correct_answers[0].replace('\n','').decode('utf-8'))
            # else :
            #    details.append('')
            details.append(pair.correct_classification)
            details.append(pair.question_classification)
            pairs_details.append(details)

            # Type question
            new = True
            for t in question_classification:
                if t[0] == pair.correct_classification:
                    new = False
                    t[1] += 1
                    if pair.correct_classification == pair.question_classification:
                        t[2] += 1
                    break
            if new:
                question_classification.append([pair.correct_classification, 0, 0, 0])
                t = question_classification[-1]
                t[1] += 1
                if pair.correct_classification == pair.question_classification:
                    t[2] += 1

        # Detalhes dos pares
        # pairs_details = sorted(pairs_details, key=itemgetter(1))
        # pairs_details = [pairs_details]
        tb = AsciiTable(pairs_details)
        tb.inner_footing_row_border = False
        file.write('\nPairs\n'+tb.table+'\n')
        # print('\nPairs\n'+tb.table)

        # Classification question
        total = 0
        correct = 0
        for t in question_classification:
            t[3] = round(float(t[2])/float(t[1]), 4)
            total += t[1]
            correct += t[2]
        question_classification = sorted(question_classification, key=itemgetter(3), reverse=True)
        question_classification = [['Classification', 'Total', 'Correct', 'Rate']] + question_classification + [
            ['', total, correct, round(float(correct)/float(total), 4)]
        ]
        tb = AsciiTable(question_classification)
        tb.inner_footing_row_border = True
        file.write('\nTypes Questions\n'+tb.table+'\n')
        print('\nTypes Questions\n'+tb.table)
        '''
        # Type question parameters
        dp = [
            ['N-GRAMS', question_process.NGRAM],
            ['STOPWORDS', question_process.STOPWORD],
            ['STEMMER', question_process.STEMMER],
            ['LOWER TEXT', question_process.LOWER]
            ]
        tb = AsciiTable(dp)
        tb.inner_footing_row_border = False
        tb.inner_heading_row_border = False
        file.write('\nQuestion Type Parameters:\n'+tb.table+'\n')
        print ('\nQuestion Type Parameters:\n'+tb.table)
        '''
        file.close()

    else:
        print "No pairs for results!"
