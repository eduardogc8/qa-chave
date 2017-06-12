# -*- coding: utf-8 -*-
import codecs
import io
import os



arquivo = io.open('base_tep2.txt', 'r', encoding='latin-1')
lista = arquivo.readlines()
	
lista2 = []
for l in lista :
	i1 = l.index('{')
	i2 = l.index('}')
	lista2.append(l[i1+1:i2]+'\n')
				
novo_arquivo = codecs.open("synonyms_pt.txt", 'w', 'utf-8')
novo_arquivo.writelines(lista2)
novo_arquivo.close()
arquivo.close()