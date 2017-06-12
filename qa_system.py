# -*- coding: utf-8 -*-
import ir_documents
import treetagger

def process_questions(questions):
	print 'Start questions process'
	answers = []
	ic = ir_documents.IndexChave()
	tagger = treetagger.TreeTagger(language='portuguese')
	for question in questions :
		print '\nQuestion '+str(questions.index(question))+'/'+str(len(questions))
		print 'Q: '+question.text.replace('\n', '')
		a = process_question(question, ic, tagger)
		for ra in question.right_answers:
			print 'Dr: '+ra.docid
		answers.append(a)
		if not (a is None or a.docs is None):
			for i in range(len(a.docs)):
				print 'Da'+str(i+1)+': '+a.docs[i]
	return answers

def sintatic_process(question, tagger, class_filter=['V','N']):
	res = tagger.tag(question)
	ret = ''
	for r in res :
		if r[1][0] in class_filter :
			ret += r[0] + ' '
	return ret.strip()

def process_question(question, ic, tagger):
	answer = Answer()
	#ToDo - criar resposta (answer.text)
	#answer.text = 'Lisboa'
	text = question.text.replace('"','').replace('(','').replace(')','').replace('?','').replace(u'«','').replace(u'»','').replace(',','').replace('.','').replace(';','')
	#text = sintatic_process(text, tagger)
	ret = ic.search(text)
	if not ret is None :
		answer.docid = ret[0]
		answer.docs = ret
	return answer

class Question:
	def __init__(self, text=''):
		self.text = text
		self.right_answers = []

class Answer:
	def __init__(self, text=None, docid=None, docs=[]):
		self.text = text
		self.docid = docid
		self.docs = docs