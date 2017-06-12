# -*- coding: utf-8 -*-
import codecs, sys, glob, os, unicodedata, io
from urllib2 import *
import subprocess
import util

class IndexChave:

	def __init__(self):	
		self.num_docs = 3

	def search(self, question):
		query = util.remove_acentts(self.make_query(question))
		command = "http://localhost:8983/solr/qa_chave/select?wt=python&indent=true&q="+query+"&fl=docno&start=0&rows="+str(self.num_docs)
		
		try :
			conn = urlopen(command.encode("utf-8"))
			rsp = eval(conn.read())
			res = rsp['response']['docs']
			ret = []
			for r in res :
				ret.append(r['docno'])
			if len(ret) > 0 :
				return ret
			else :
				print 'No return in search'
				print command.replace('%20', ' ').encode("utf-8")
				return None
			
		except HTTPError: 
			print "\nErro Search"
			print command.replace('%20', ' ').encode("utf-8")
		return None

	def make_query(self, question):
		words = question.strip().split(' ')
		query = ''
		for word in words :
			w = word
			if len(w)>0:
				query += ' OR doctext:'+w
		query = query [4:]
		return query.replace(' ', '%20')