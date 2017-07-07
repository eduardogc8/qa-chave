# -*- coding: utf-8 -*-

import sklearn
import nltk
from collections import Counter

NGRAM = 1
STOPWORD = False
STEMMER = False
LOWER = False
FILTER = True


class QuestionProcess:

	def __init__(self):
		self.pairs = []
		self.train_pairs = []
		self.n_grams = []
		self.tps = [] #Tipos de questões

	def run(self):
		if FILTER : self.filter_pairs()
		tps = self.types()
		clf = self.train_svm()
		for pair in self.pairs :
			r = clf.predict([self.normalize_question(pair.question)])
			r_type = self.types()[r[0]]
			pair.question_type = r_type

	def filter_pairs(self):
		new_pairs = []
		for pair in self.pairs :
			if not pair.correct_type.lower().strip() == 'x' :
				new_pairs.append(pair)
		self.pairs = new_pairs
		new_pairs2 = []
		for pair in self.train_pairs :
			if not pair.correct_type.lower().strip() == 'x' :
				new_pairs2.append(pair)
		self.train_pairs = new_pairs2
		

	def normalize_question(self, question):
		n_grams = self.ngrams()
		tokens = self.to_tokens(question)
		q_ngrams = Counter(nltk.ngrams(tokens, NGRAM))
		data = []
		for g in n_grams :
			if g in q_ngrams :
				data.append(1)
			else :
				data.append(0)
		return data

	def normalize_type(self, tp):
		return self.types().index(tp)

	def normalize_questions_train(self):
		data = []
		n_grams = self.ngrams()
		for pair in self.train_pairs :
			data.append(self.normalize_question(pair.question))
		return data

	def normalize_types_train(self):
		target = []
		tps = self.types()
		for pair in self.train_pairs :
			target.append(tps.index(pair.correct_type))
		return target 

	def ngrams(self):
		interval_print = 1000
		aux_count = 0
		if len(self.n_grams) == 0 :
			for pair in self.train_pairs + self.pairs :
				
				if aux_count == interval_print :
					aux_count = 0
					print str((self.train_pairs + self.pairs).index(pair))+'/'+str(len(self.train_pairs + self.pairs))
				else : aux_count += 1
				
				tokens = self.to_tokens(pair.question)
				q_ngrams = Counter(nltk.ngrams(tokens, NGRAM))

				for g in q_ngrams:
					if not g in self.n_grams: 
						self.n_grams.append(g)
			print 'ngrams: '+ str(len(self.n_grams))
		return self.n_grams

	def to_tokens(self, text):
		t = text
		if LOWER:
			t = text.lower()
		tokens = nltk.word_tokenize(t)
		if STEMMER:
			stemmer = nltk.stem.RSLPStemmer()
			for i in range(len(tokens)) :
				tokens[i] = stemmer.stem(tokens[i])

		if STOPWORD:
			stopwords = nltk.corpus.stopwords.words('portuguese')
			ret = []
			for token in tokens :
				if not (u''+token) in stopwords :
					ret.append(token)
		else :
			ret = tokens
		return ret

	def types(self):
		if len(self.tps) == 0 :
			for pair in self.train_pairs + self.pairs :
				if not pair.correct_type in self.tps :
					self.tps.append(pair.correct_type)
		return self.tps


	def train_svm(self):
		print "Train Started"
		clf = sklearn.svm.LinearSVC(verbose=True)
		data = self.normalize_questions_train()
		target = self.normalize_types_train()
		print '\nData: '+str(len(data)) + ' | Target: ' + str(len(target))

		clf.fit(data, target)
		print "Train Completed"
		return clf
