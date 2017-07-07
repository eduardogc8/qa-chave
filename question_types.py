# -*- coding: utf-8 -*-
#Retorna todos os tipo de questão do conjunto

import codecs

path_questions = 'dataset/questions.xml'

types = {}
no_type = 0

for line in open(path_questions, 'r').readlines() :
	if '<pergunta' in line :
		if 'tipo="' in line :
			aux = line[line.index('tipo=')+6:]
			t = aux[:aux.index('"')]
			if not t in types.keys() :
				types[t] = 1
			else :
				types[t] += 1
		else :
			no_type += 1

print types

print no_type

