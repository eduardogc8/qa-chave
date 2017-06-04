# -*- coding: utf-8 -*-

def process_questions(questions):
	answers = []
	for question in questions :
		answers.append(process_question(question))
	return answers

def process_question(question):
	#TODO
	return None
	#return Answer('Lisboa')

class Question:
	def __init__(self, text=''):
		self.text = text
		self.right_answers = []

class Answer:
	def __init__(self, text='', docid=''):
		self.text = text
		self.docid = docid