from unicodedata import normalize
import io


CHARACTERS_REPLACE = [('\n',''), ('\\', ''), (u'«', "\""), (u'»', "\""), (u"'", "\"")]
PONCTUATION_REPLACE = [(';', ''), (':', ''), ('(', ''), (')', ''), ('[', ''), (']', ''), ('{', ''), ('}', ''), ('?', ''), ('!', '')]
NUMBERS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

PATH_STOPWORDS = 'data/util/stopwords_pt.txt'


#Retorna True se a string representa um INT
def represents_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


#Remove o acento das palavras
def remove_acentts(txt):
    #if type(txt) is str:
    #    txt = unicode(txt, 'utf-8')
    return normalize('NFKD', txt).encode('ASCII', 'ignore').decode('ASCII')


# Tratamento no texto
def treat_text(text):
    for replace in CHARACTERS_REPLACE:
        text = text.replace(replace[0], replace[1])
    text = text.strip()
    text = " ".join(text.split())
    return text


# Remove os caracteres conforme PONCTUATION_REPLACE do texto
def replace_ponctutation(text):
    for replace in PONCTUATION_REPLACE:
        text = text.replace(replace[0], replace[1])
    if ',' in text or '.' in text:
        new_text = ''
        for i in range(len(text)):
            c = text[i]
            if c == ',' or c == '.':
                if i > 0 and text[i-1] in NUMBERS and i < len(text)-1 and text[i+1] in NUMBERS:
                    new_text += c
            else:
                new_text += c
        text = new_text
    text = text.strip()
    return text


def is_stopword(word):
    f = io.open(PATH_STOPWORDS, 'r', encoding='utf-8')
    lines = f.readlines()
    for line in lines:
        if word.lower() == treat_text(line).lower():
            return True
    return False


def findSentenceIndexs(text, sentence):
    indexs = []
    sentIndex = 0
    for i in range(len(text.split())):
        word = text.split()[i]
        if word == sentence.split()[sentIndex]:
            if sentIndex == len(sentence.split())-1:
                indexs.append((i-sentIndex, i))
                sentIndex = 0
            else:
                sentIndex += 1
        else:
            sentIndex = 0
    return indexs


def shortSentenceDistance(text, word, answer):
    if answer not in text:
        print(answer + ' | ' + text)
        return -2
    if word in text.split():
        indexs1 = findSentenceIndexs(text, word)
        indexs2 = findSentenceIndexs(text, word)
        if len(indexs1) <= 0:
            print('Index1 '+word+' : ' + text)
        if len(indexs2) <= 0:
            print('Index2 '+answer+' : ' + text)
        distance = float('inf')
        for i1 in indexs1:
            for i2 in indexs2:
                if i1[0] > i2[0]:
                    dist = abs(i1[0] - i2[1])
                else:
                    dist = abs(i1[1] - i2[0])
                if dist < distance:
                    distance = dist
        return distance
    return -1
