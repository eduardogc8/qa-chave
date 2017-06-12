# -*- coding: utf-8 -*-
import codecs
import io
import os

def make_field(name):
	return "<field name='"+name+"'>"

paths_documents = ['dataset/documents/folha94/', 'dataset/documents/folha95/', 'dataset/documents/publico94/', 'dataset/documents/publico95/']
#paths_documents = ['dataset/documents/test/']
lista2 = ['<add>']
count = 0
count2 = 1
docs_t = 0
docs_c = 0

for path in paths_documents :
	print 'DIR'
	for file in os.listdir(path): 
	    #print '.'
	    if file.endswith(".sgml"):	
			arquivo = io.open(path+file, 'r', encoding='latin-1')
			lista = arquivo.readlines()
			in_text = False
			
			for l in lista :
				s = l
				if '<DOC>' in s :
					s = s.replace('<DOC>', "<doc>")
				if 'DOCNO' in s :
					s = s.replace('<DOCNO>', make_field('docno'))
				if '<TEXT>' in s :
					s = s.replace('<TEXT>', make_field('doctext'))
				if '<DOCID>' in s :
					s = None
				elif '<DATE>' in s :
					s = None
				elif '<CATEGORY>' in s :
					s = None
				elif '<AUTHOR>' in s :
					s = None
				else :
					s = s.replace('</DOCNO>', "</field>")
					s = s.replace('</TEXT>', "</field>")
					s = s.replace('</DOC>', "</doc>")
					s = s.replace('&', '')
					lista2.append(s)

			count += 1
			#print str(count)
			if count == 300000 :
				count = 0
				print "****"+str(count2)+'**** Docs: '+str(docs_c)
				lista2.append('</add>')
				novo_arquivo = codecs.open("dataset/documents_xml/data"+str(count2)+".xml", 'w', 'utf-8')
				count2 += 1
				novo_arquivo.writelines(lista2)
				novo_arquivo.close()
				lista2 = ['<add>']
				docs_c = 0
			arquivo.close()

if count > 0 :
	print "****"+str(count2)+'****'
	lista2.append('</add>')
	novo_arquivo = codecs.open("dataset/documents_xml/data"+str(count2)+".xml", 'w', 'utf-8')
	count2 += 1
	novo_arquivo.writelines(lista2)
	novo_arquivo.close()
print "End docs: "+str(docs_t)