import xml.etree.ElementTree as et
import sklearn_crfsuite
from util import util
import nltk
import dill


patch_train = "data/harem/CDPrimeiroHAREMprimeiroevento.xml"
patch_test = "data/harem/colSegundoHAREM.xml"
file_ner = 'data/models/ner.sav'

char_end_sentence = ['.', ';', '?', '!']


def train():
    sentences = load_sentences()
    X_train = [sent2features(s) for s in sentences]
    y_train = [sent2labels(s) for s in sentences]

    crf = sklearn_crfsuite.CRF(
        algorithm='lbfgs',
        c1=0.1,
        c2=0.1,
        max_iterations=100,
        all_possible_transitions=True
    )
    crf.fit(X_train, y_train)
    dill.dump(crf, open(file_ner, 'wb'))
    return crf

def predict(model, sentenca):
    ws = sentenca.split()
    words = []
    for w in ws:
        words.append((w, ''))
    ret = model.predict([sent2features(words)])
    return ret

def tokens(in_text):
    if in_text is None: return []
    return nltk.word_tokenize(util.treat_text(in_text))

def load_sentences():
    # Documents-> DOC-> EM, ALT->EM, OMITIDO->EM
    tree = et.parse(patch_train)
    doc_trees = tree.getroot()

    sentences = []
    for doc in doc_trees:
        sentence = []
        text = tokens(doc.text)
        entities = []
        for tag in doc:
            for t in text:
                if t in char_end_sentence:
                    sentences.append(sentence)
                    sentence = []
                else:
                    sentence.append((t, 'O'))
            if tag.tag == 'EM':
                t_text = tokens(tag.text)
                first = True
                for t in t_text:
                    if first:
                        first = False
                        sentence.append((t, tag.attrib['CATEG'].split('|')[0]+'-B'))
                    else:
                        sentence.append((t, tag.attrib['CATEG'].split('|')[0]+'-I'))

            elif tag.tag == 'ALT':
                t_text = tokens(tag.text)
                for a_tag in tag:
                    end = False
                    for t in t_text:
                        if t == '|':
                            end = True
                            break
                        else:
                            sentence.append((t, 'O'))
                    if end:
                        break
                    first = True
                    a_text = tokens(a_tag.text)
                    for t in a_text:
                        if first:
                            first = False
                            sentence.append((t, a_tag.attrib['CATEG'].split('|')[0]+'-B'))
                        else:
                            sentence.append((t, a_tag.attrib['CATEG'].split('|')[0]+'-I'))
                    t_text = tokens(a_tag.tail)
            text = tokens(tag.tail)
        if len(sentence) > 0:
            sentences.append(sentence)
            sentence = []
    return sentences

def word2features(sent, i):
    word = sent[i][0]

    features = {
        'bias': 1.0,
        'word.lower()': word.lower(),
        'word[-3:]': word[-3:],
        'word[-2:]': word[-2:],
        'word.isupper()': word.isupper(),
        'word.istitle()': word.istitle(),
        'word.isdigit()': word.replace(',', '').replace('.', '').isdigit(),
    }
    if i > 0:
        word1 = sent[i-1][0]
        features.update({
            '-1:word.lower()': word1.lower(),
            '-1:word.istitle()': word1.istitle(),
            '-1:word.isupper()': word1.isupper(),
        })
    else:
        features['BOS'] = True

    if i < len(sent)-1:
        word1 = sent[i+1][0]
        features.update({
            '+1:word.lower()': word1.lower(),
            '+1:word.istitle()': word1.istitle(),
            '+1:word.isupper()': word1.isupper(),
        })
    else:
        features['EOS'] = True

    return features


def sent2features(sent):
    return [word2features(sent, i) for i in range(len(sent))]

def sent2labels(sent):
    return [label for token, label in sent]

def sent2tokens(sent):
    return [token for token, label in sent]
