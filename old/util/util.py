# -*- coding: utf-8 -*-
from unicodedata import normalize

#Retorna True se a string representa um INT
def represents_int(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

#Remove o acento das palavras (Lá -> La)
def remove_acentts(txt):
	if type(txt) is str :
		txt = unicode(txt, 'utf-8')
	return normalize('NFKD', txt).encode('ASCII','ignore').decode('ASCII')



