# -*- coding: utf-8 -*-

import os.path
import unicodedata

path_result_file = "results/"

#Define o nome do arquivo de saída
def file_name():
	count = 1
	while os.path.isfile(path_result_file+'result_'+str(count)) :
		count += 1
	return 'result_'+str(count)

#Produz o arquivo de resultados
def produce(questions, answers):
	
	file = open(path_result_file+file_name(), 'w')

	if len(questions) != len(answers) :
		file.write('Total questions and total answers are different!\n')
		print 'Total questions and total answers are different!'
	else :
		file.write('Total valid questions and answers: '+str(len(questions)) + '\n')
		print 'Total valid questions and answers: '+str(len(questions)) + '\n'

		count_right_anwers = 0
		count_right_documents = 0
		count_right_documents_not_first = 0
		for i in range(len(questions)) :
			question = questions[i]
			answer = answers[i]
			
			if compare_answer(question, answer):
				count_right_anwers += 1

			for right_answer in question.right_answers :
				if right_answer is None or answer is None or right_answer.docid is None or answer.docid is None : continue
				if right_answer.docid == answer.docid :
					count_right_documents += 1
					break

			#print str(len(answer.docs))
			for qd in question.right_answers :
				b = False
				for ad in answer.docs :
					if qd.docid == ad :
						count_right_documents_not_first += 1
						b = True
						break
				if b :
					break
			
			

		#Taxa de acerto de respostas certas
		hit_hate = -1
		if float(len(questions)) > 0 :
			hit_hate = float(count_right_anwers)/float(len(questions))
		file.write('Hit rate answer:\t'+str(hit_hate) + '\n')
		print 'Hit rate answer:\t'+str(hit_hate)

		#Taxa de acerto de documento com a resposta
		hit_hate_document = -1
		if float(len(questions)) > 0 :
			hit_hate_document = float(count_right_documents)/float(len(questions))
		file.write('Hit rate 1 document:\t'+str(hit_hate_document) + '\n')
		print 'Hit rate 1 document:\t'+str(hit_hate_document)

		#Taxa de acerto de um do três primeiros documentos com a resposta
		hit_hate_document_3 = -1
		if float(len(questions)) > 0 :
			hit_hate_document_3 = float(count_right_documents_not_first)/float(len(questions))
		file.write('Hit rate 1-3 documents:\t'+str(hit_hate_document_3) + '\n')
		print 'Hit rate 1-3 documents:\t'+str(hit_hate_document_3)

	file.close()

def compare_answer(question, answer):
	if answer is None or question is None : return False
	for a in question.right_answers :
		if a is None or a.text is None or answer.text is None : return False
		if a.text.strip().lower() == answer.text.strip().lower() :
			return True
	return False