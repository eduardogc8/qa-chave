# -*- coding: utf-8 -*-
import codecs
import io
import os

def make_field(name):
	return "<field name='"+name+"'>"

paths_documents = ['dataset/documents/folha94/', 'dataset/documents/folha95/', 'dataset/documents/publico94/', 'dataset/documents/publico95/']
#paths_documents = ['dataset/documents/test/']
lista2 = []
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
			text = ''
			doc_id = ''
			for l in lista :
				s = l
				if in_text :
					if '</TEXT>' in s :
						in_text = False
						lista2.append(doc_id + '|' + text)
						text = ''
						doc_id = '\n'
						continue
					else :
						text += s.replace('\n','')
				else:
					if '<DOCNO>' in s :
						doc_id += s.replace('\n', '').replace('<DOCNO>','').replace('</DOCNO>','')
						continue
					if '<TEXT>' in s :
						in_text = True
						continue

			count += 1
			#print str(count)
			if count == 100 :
				count = 0
				print "****"+str(count2)+'**** Docs: '+str(docs_c)
				novo_arquivo = codecs.open("dataset/texts_lines_"+str(count)+".txt", 'w', 'utf-8')
				count2 += 1
				novo_arquivo.writelines(lista2)
				novo_arquivo.close()
				lista2 = []
				docs_c = 0
			arquivo.close()

if count > 0 :
	print "****"+str(count2)+'****'
	novo_arquivo = codecs.open("dataset/texts_lines_"+str(count)+".txt", 'w', 'utf-8')
	count2 += 1
	novo_arquivo.writelines(lista2)
	novo_arquivo.close()
print "End docs: "+str(docs_t)