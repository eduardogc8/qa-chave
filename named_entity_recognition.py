import xml.etree.ElementTree as et
from util import corenlp as CNLP
import sklearn_crfsuite
from sklearn_crfsuite import metrics
from util import util
import random
import nltk
import dill


patch_train = "data/harem/CDPrimeiroHAREMprimeiroevento.xml"
patch_test = "data/harem/colSegundoHAREM.xml"
file_ner = 'data/models/ner.sav'

char_end_sentence = ['.', ';', '?', '!']


def train():
    sentences = load_sentences()
    #X_train = [sent2features(s) for s in sentences]
    X_train = []
    count = 0
    classes = {}
    tt = 0
    for i, s in enumerate(sentences):
        count += 1

        for ss in s:
            if ss[1] not in classes:
                classes[ss[1]] = 0
            classes[ss[1]] += 1
            tt += 1
        if count >= 10:
            print(i, '/', len(sentences))
            count = 0
        X_train.append(sent2features(s))
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

    print(classes)
    print(tt)

    return crf


def test_approach(remove_o=True):
    sentences = load_sentences()
    random.seed = 1
    random.shuffle(sentences)
    size_s = len(sentences)
    train_sents = sentences[:int(size_s-size_s/5)]
    test_sents = sentences[int(size_s-size_s/5):]

    print("Sentences:", size_s, "Train:", len(train_sents), "Test:", len(test_sents))

    X_train = [sent2features(s) for s in train_sents]
    y_train = [sent2labels(s) for s in train_sents]

    X_test = [sent2features(s) for s in test_sents]
    y_test = [sent2labels(s) for s in test_sents]

    crf = sklearn_crfsuite.CRF(
        algorithm='lbfgs',
        c1=0.1,
        c2=0.1,
        max_iterations=100,
        all_possible_transitions=True
    )
    crf.fit(X_train, y_train)
    if remove_o:
        labels = list(crf.classes_)
        labels.remove('O')

    y_pred = crf.predict(X_test)
    f1 = metrics.flat_f1_score(y_test, y_pred, average='weighted', labels=labels)
    print('F1-Score:'+ '%.3f' % (f1))
    # group B and I results
    sorted_labels = sorted(
        labels,
        key=lambda name: (name[1:], name[0])
    )
    print(metrics.flat_classification_report(
        y_test, y_pred, labels=sorted_labels, digits=3
    ))


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
    #print('\n+=', util.treat_text(in_text), '=+')
    #return CNLP.tokens_pos(util.treat_text(in_text))[0]


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
    sentence = ' '.join([x[0] for x in sent])
    word = sent[i][0]
    features = {
        'bias': 1.0,
        'word.lower()': word.lower(),
        #'word.pos': CNLP.pos(sentence, i),
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
