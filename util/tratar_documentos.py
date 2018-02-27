# -*- coding: utf-8 -*-
import codecs
import io
import os


paths_documents = ['data/documents/folha94/', 'data/documents/folha95/', 'data/documents/publico94/', 'data/documents/publico95/']


for path in paths_documents:
	print (path)
	new_lines = []
	for file in os.listdir(path):
		if file.endswith(".sgml"):
			old_file = io.open(path+file, 'r', encoding='latin-1')
			lines = old_file.readlines()
			in_text = False
			doc_text = ''
			doc_id = ''
			for line in lines:
				if in_text:
					if '</TEXT>' in line:
						in_text = False
						new_lines.append(doc_id + '|' + doc_text)
						doc_text = ''
						doc_id = '\n'
					else:
						doc_text += line.replace('\n',' ')
				else:
					if '<DOCNO>' in line: 
						doc_id += line.replace('\n', '').replace('<DOCNO>','').replace('</DOCNO>','')
					if '<TEXT>' in line :
						in_text = True

	new_file = codecs.open("data/docs_"+str(paths_documents.index(path))+".txt", 'w', 'utf-8')
	new_file.writelines(new_lines)
	new_file.close()
	old_file.close()
print('End')