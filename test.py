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

			for line in lines:
				new_lines.append(line)

	new_file = codecs.open("data/docs_"+str(paths_documents.index(path))+".txt", 'w', 'utf-8')
	new_file.writelines(new_lines)
	new_file.close()
	old_file.close()
print('End')
