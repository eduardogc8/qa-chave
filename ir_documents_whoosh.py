# -*- coding: utf-8 -*-
from whoosh.index import create_in
from whoosh.index import open_dir
from whoosh.fields import Schema, TEXT, ID
from whoosh.analysis import StandardAnalyzer
from whoosh.qparser import QueryParser
from string import maketrans, punctuation
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import codecs, sys, glob, os, unicodedata

paths_documents = ['dataset/documents/folha94/', 'dataset/documents/folha95/', 'dataset/documents/publico94/', 'dataset/documents/publico95/']
#paths_documents = ['dataset/documents/test/']
path_index = "dataset/index"


class IndexChave:

	def __init__(self):
		self.metadata_dict = {}
		self.ix = None

	def run_index(self):

		if not os.path.exists(path_index):
			os.mkdir(path_index)
			schema = Schema(docid=TEXT(stored=True), doc_text=TEXT(stored=True,phrase=True,analyzer=StandardAnalyzer(stoplist=None)))
			self.ix = create_in(path_index, schema)

			writer = self.ix.writer()

			for path in paths_documents :
				print 'Dir'
				for file_doc in os.listdir(path):
					print '..File'
					lines = codecs.open(path+file_doc,"r","latin-1").read().split('\n')
					in_text = False
					text = ''
					docid = ''
					for line in lines :
						if in_text :
							if '</TEXT>' in line: 
								in_text = False
							else :
								text += ' '+line
						else :
							if '<TEXT>' in line: in_text = True
							if '<DOCID>' in line: docid = line.replace('<DOCID>','').replace('</DOCID>','').strip()
							if '<DOC>' in line:
								#New document
								in_text = False
								text = ''
								docid = ''
							if '</DOC>' in line:
								#Save new document
								writer.add_document(docid=docid, doc_text=text)
			writer.commit()

		else :
			self.ix = open_dir(path_index)


	def search(self, text):
		
		ret = {}
		if self.ix is None :
			print 'Index is Null'
			return None
		else :
			new_text = text.replace('\n','').replace('\r','').replace('?','').strip().lower()
			print 'Search: '+new_text
			q_text = ''
			for word in new_text.split(' '):
				q_text += ' OR ' + word
			q_text = q_text[4:]
			qp = QueryParser("doc_text", schema=self.ix.schema)
			q = qp.parse(q_text)

			s = self.ix.searcher()
			results = s.search(q, limit=1)
			if len(results) > 0 :
				print 'Resultado:' + results[0]['docid']
				ret['docid'] = results[0]['docid']
				ret['doc_text'] = results[0]['doc_text']
			else : ret = None
			#found = results.scored_length()
			#if results.has_exact_length():
			#	print("Scored ", found, " of exactly ", len(results), " documents")
			#else:
			#	high = results.estimated_length()
			#	print ("Scored ", found, " of extimated ", high, " documents")
			s.close()
		return ret