# -*- coding: utf-8 -*-
import xml.etree.ElementTree as et
from xml.parsers import expat
from bs4 import BeautifulSoup
import qa_system
import re, os, codecs


path_questions = "dataset/questions.xml"
paths_documents = ['dataset/documents/folha94/', 'dataset/documents/folha95/', 'dataset/documents/publico94/', 'dataset/documents/publico95/']

#path_questions = "dataset/questions_test.xml"
#paths_documents = ['dataset/documents/test/']


#Verifica se os dados já estão indexados, se não estiverem é feito a indexação
def run_mananger(): pass

#Abre o arquivo dataset e retorna uma lista de perguntas em formato tree
def dataset():
	file = open(path_questions, 'r')
	tree = et.parse(file)
	return tree.getroot()

#Retorna todas os pares do dataset que tem ao menos uma resposta válida, também, é retornado os pares inválidos
#Válida significa: o par contém resposta e a resposta tem um docid de origem válida (FolhaSP ou Público)
def valid_invalid_pairs():
	ret = []
	ret2 = []
	pairs = dataset()

	for pair in pairs :
		pair = tree_to_pair(pair)
		
		if pair.question is None or pair.question == '':
			#print "Warning. Pair with None question"
			continue
		else : 
			valid_answers = []
			valid_docid = []
			for i in range(len(pair.correct_answers)) :
				answer = pair.correct_answers[i]
				docid = pair.correct_docs_id[i]
				new_docid = validate_docid(docid)
				if not new_docid is None :
					valid_docid.append(new_docid)
					valid_answers.append(answer)
			pair.correct_answers = valid_answers
			pair.correct_docs_id = valid_docid
			if len(pair.correct_answers) > 0 :
				ret.append(pair)
			else :
				ret2.append(pair)

	#print 'Total Questions:\t'+str(len(pairs))
	#print 'Valid Questions:\t'+str(len(ret))
	return ret, ret2

def statistical_numbers():
	valid, invalid = valid_invalid_pairs()

	print "Total valid questions: "+str(len(valid))
	print "Total invalid questions: "+str(len(invalid))

	types = {}
	for i in invalid:
		t = i.question_type
		if not t in types.keys() :
			types[t] = 0
		types[t] += 1
	print "\nTypes invalid questions: "
	print types

	types = {}
	for i in valid:
		t = i.question_type
		if not t in types.keys() :
			types[t] = 0
		types[t] += 1
	print "\nTypes valid questions: "
	print types

	types = {}
	for i in invalid:
		t = i.question_category
		if not t in types.keys() :
			types[t] = 0
		types[t] += 1
	print "\nCategory invalid questions: "
	print types

	types = {}
	for i in valid:
		t = i.question_category
		if not t in types.keys() :
			types[t] = 0
		types[t] += 1
	print "\nCategory valid questions: "
	print types

	types = {}
	for i in invalid:
		t = i.question_restriction
		if not t in types.keys() :
			types[t] = 0
		types[t] += 1
	print "\nRestriction invalid questions: "
	print types

	types = {}
	for i in valid:
		t = i.question_restriction
		if not t in types.keys() :
			types[t] = 0
		types[t] += 1
	print "\nRestriction valid questions: "
	print types


#Se é um docid válido(FolhaSP ou Público) então retorna um docid no 
#formato do docid dos documentos se não retorna None
def validate_docid(docid):
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
def tree_to_pair(tree_question):
	p = qa_system.Pair()

	if 'categoria' in tree_question.attrib :
		p.question_category = tree_question.attrib['categoria']
	if 'tipo' in tree_question.attrib :
		p.correct_type = tree_question.attrib['tipo']
	if u'restrição' in tree_question.attrib :
		p.question_restriction = tree_question.attrib[u'restrição']

	for t in tree_question :
		if t.tag == 'texto' :
			p.question = treat(t.text)

		elif t.tag == 'resposta':
			docid = None
			if 'docid' in t.attrib :
				docid = t.attrib['docid']
			if not t.text is None and not t.text.strip() == '':
				p.correct_answers.append(t.text.encode('utf-8'))
				p.correct_docs_id.append(docid)
			#else : print ('Warning. Text None in '+p.question)
		elif t.tag == 'extracto':
			if not t.text is None: 
				p.extractos.append(t.text)
			#else : print ('Warning. Extracto is None in '+p.question)
		#else: print ("Warning. Unknow tag: "+t.tag)
	return p

def treat(text):
	if text is None : return None
	ret = text.replace('«', '\"').replace('»', '\"').replace('?','')
	return ret