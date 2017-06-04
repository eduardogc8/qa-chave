# -*- coding: utf-8 -*-
import nltk
from collections import defaultdict

class Index:

	def __init__(self):
		self.documents = {}
		self.__unique_id = 0
		self.index = defaultdict(list)

	def add(self, document):

		for token in [t.lower() for t in nltk.word_tokenize(document)]:
			if self.__unique_id not in self.index[token]:
				self.index[token].append(self.__unique_id)
 
		self.documents[self.__unique_id] = document
		self.__unique_id += 1