from unicodedata import normalize


CHARACTERS_REPLACE = [('\n',''), ('\\', ''), (u'«', ''), (u'»', ''), (u'"', ''), (u'\"', '')]

#Retorna True se a string representa um INT
def represents_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

#Remove o acento das palavras
def remove_acentts(txt):
    if type(txt) is str:
        txt = unicode(txt, 'utf-8')
    return normalize('NFKD', txt).encode('ASCII', 'ignore').decode('ASCII')

# Tratamento no texto
def treat_text(text):
    for replace in CHARACTERS_REPLACE:
        text = text.replace(replace[0], replace[1])
    text = text.strip()
    return text
