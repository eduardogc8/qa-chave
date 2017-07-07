# -*- coding: utf-8 -*-

import os.path
from terminaltables import AsciiTable
import time
import sys
import question_process
reload(sys)
sys.setdefaultencoding('utf-8')

# Local onde será salvo os arquivo de saída
path_result_file = "results/"

#Define o nome do arquivo de saída
def file_name():
	count = 1
	while os.path.isfile(path_result_file+'result_'+str(count)) :
		count += 1
	return 'result_'+str(count)

#Produz os resultados de saida em console e arquivo
def produce(pairs, train_pairs = None):
	
	if len(pairs) > 0 :

		#Cria um novo arquivo de resultados
		file = open(path_result_file+file_name(), 'w')

		#Momento dos resultados
		p = time.strftime("%D %H:%M:%S")
		file.write(p+'\n')
		print '\nResults\n'+p

		count = 0

		#Detalhes de cada par
		pairs_details = [['#', 'Question', 'Correct Type', 'Classified Type']]

		#Question Processing
		types_question = []

		for pair in pairs :
			count += 1
			
			#Detalhes do par
			details = []
			details.append(count)
			details.append(pair.question.replace('\n','').decode('utf-8'))
			#if len(pair.correct_answers) > 0 :
			#	#print type(pair.correct_answers[0].replace('\n',''))
			#	details.append(pair.correct_answers[0].replace('\n','').decode('utf-8'))
			#else :
			#	details.append('')
			details.append(pair.correct_type)
			details.append(pair.question_type)
			pairs_details.append(details)

			#Type question
			new = True
			for t in types_question :
				if t[0] == pair.correct_type :
					new = False
					t[1] += 1
					if pair.correct_type == pair.question_type :
						t[2] += 1
					break
			if new:
				types_question.append([pair.correct_type,0,0,0])
				t = types_question[-1]
				t[1] += 1
				if pair.correct_type == pair.question_type :
					t[2] += 1

		#Detalhes dos pares
		tb = AsciiTable(pairs_details)
		tb.inner_footing_row_border = False
		file.write('\nPairs\n'+tb.table+'\n')
		#print('\nPairs\n'+tb.table)

		#Type question
		total = 0
		correct = 0
		for t in types_question :
			t[3] = round(float(t[2])/float(t[1]) ,4)
			total += t[1]
			correct += t[2]
		types_question = [['Type', 'Total', 'Correct', 'Rate']] + types_question + [['', total, correct, round(float(correct)/float(total),4)]]
		tb = AsciiTable(types_question)
		tb.inner_footing_row_border = True
		file.write('\nTypes Questions\n'+tb.table+'\n')
		print('\nTypes Questions\n'+tb.table)
		#Type question parameters
		dp = [['N-GRAMS', question_process.NGRAM],
		['STOPWORDS', question_process.STOPWORD],
		['STEMMER', question_process.STEMMER],
		['LOWER TEXT', question_process.LOWER],
		['FILTER PAIRS', question_process.FILTER]]
		tb = AsciiTable(dp)
		tb.inner_footing_row_border = False
		tb.inner_heading_row_border = False
		file.write('\nQuestion Type Parameters:\n'+tb.table+'\n')
		print ('\nQuestion Type Parameters:\n'+tb.table)

		file.close()

	else :
		print "No pairs for results!"