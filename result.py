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
		file.write('Total questions and answers: '+str(len(questions)) + '\n')

		count_right_anwers = 0
		for i in range(len(questions)) :
			question = questions[i]
			answer = answers[i]
			
			if compare_answer(question, answer):
				count_right_anwers += 1

		#Taxa de acerto de respostas certas
		hit_hate = -1
		if float(len(questions)) > 0 :
			hit_hate = float(count_right_anwers)/float(len(questions))
		file.write('Hit rate: '+str(hit_hate) + '\n')
		print 'Hit rate: '+str(hit_hate)

	file.close()

def compare_answer(question, answer):
	if answer is None or question is None : return False
	for a in question.right_answers :
		if a is None or a.text is None : return False
		if (u''+a.text).strip().lower() == str(answer.text).strip().lower() :
			return True
	return False