# -*- coding: utf-8 -*-
import xml.etree.ElementTree as et
from xml.parsers import expat
from bs4 import BeautifulSoup
import util
import qa_system
import re
import os
import codecs
import ir_documents

path_data_file = "dataset/qaclef_pt.xml"
#path_data_file = "dataset/qaclef_pt_test.xml"
paths_documents = ['dataset/documents/folha94/', 'dataset/documents/folha95/', 'dataset/documents/publico94/', 'dataset/documents/publico95/']
#paths_documents = ['dataset/documents/test/']

#Abre o arquivo dataset e retorna uma lista de perguntas em formato tree
def dataset():
	file = open(path_data_file, 'r')
	tree = et.parse(file)
	return tree.getroot()

#Retorna todas as perguntas do dataset que tem ao menos uma resposta válida
#Válida significa: a pergunta contém resposta e a resposta tem um docid de origem válida (FolhaSP ou Público)
def with_valid_resposta():
	ret = []
	perguntas = dataset()
	for pergunta in perguntas :
		question = tree_to_question(pergunta)
		
		if question.text is None or len(question.right_answers) < 1 :
			continue

		valid_answers = []
		for answer in question.right_answers :
			new_docid = valid_docid(answer.docid)
			if not new_docid is None :
				answer.docid = new_docid
				valid_answers.append(answer)
		question.right_answers = valid_answers
		if len(question.right_answers) > 0 :
			ret.append(question)

	#print 'Total Questions:\t'+str(len(perguntas))
	#print 'Valid Questions:\t'+str(len(ret))
	return ret

#Se é um docid válido(FolhaSP ou Público) então retorna um docid no 
#formato do docid dos documentos se não retorna None
def valid_docid(docid):
	global aux
	if docid is None or len(docid.strip()) < 10 :
		return None
	else :
		docid = docid.strip()
		r = re.match(r'(?P<n1>.+)(?P<n2>\d{6,8})-(?P<n3>\d{1,3}$)', docid)
		if not r is None :
			if r.groupdict()['n1'][:1] == 'F':
				return 'FSP'+r.groupdict()['n2']+'-'+r.groupdict()['n3']
			else:
				#print r.groupdict()['n1']
				return 'PUBLICO-19'+r.groupdict()['n2']+'-'+r.groupdict()['n3']
		else :
			return None


#Passa a pergunta em formato tree para um objeto do tipo Question
def tree_to_question(tree_question):
	question = qa_system.Question()
	for t in tree_question :
		if t.tag == 'texto' :
			question.text = t.text
		elif t.tag == 'resposta':
			docid = None
			if 'docid' in t.attrib :
				docid = t.attrib['docid']
				if not t.text is None :
					question.right_answers.append(qa_system.Answer(text=t.text.encode('utf-8'), docid=docid))
	return question