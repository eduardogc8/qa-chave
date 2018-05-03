# -*- coding: utf-8 -*-
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, confusion_matrix
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC
from collections import Counter, defaultdict
import matplotlib.pyplot as plt
from util import util
import numpy as np
import itertools
import dill
import pickle
import nltk


answer_type_file = 'data/models/answer_type.sav'
MAX_DOCUMENTS_RETRIEVAL = 10

##### QUESTION CLASSIFICATION #####

def count_vectorizer(MIN_GRAM=1, MAX_GRAM=1, LOWER=True):
    return CountVectorizer(analyzer=lambda x: x, strip_accents=None, ngram_range=(MIN_GRAM, MAX_GRAM),
                           token_pattern=u'(?u)\\\\b\\\\w+\\\\b', lowercase=LOWER)

def tfidf_vectorizer(MIN_GRAM=1, MAX_GRAM=1, LOWER=True):
    return TfidfVectorizer(analyzer=lambda x: x, strip_accents=None, ngram_range=(MIN_GRAM, MAX_GRAM),
                           token_pattern=u'(?u)\\\\b\\\\w+\\\\b', lowercase=LOWER)


class MeanEmbeddingVectorizer(object):
    def __init__(self, word2vec):
        self.word2vec = word2vec
        self.dim = len(word2vec)

    def fit(self, X, y):
        return self

    def transform(self, X):
        ret = np.array([
            np.mean([self.word2vec[w] for w in words if w in self.word2vec]
                    or [np.zeros(self.dim)], axis=0)
            for words in X
        ])
        return ret


class HybridVectorizer(object):
    def __init__(self, word2vec):
        self.word2vec = word2vec
        self.dim = len(word2vec)
        self.bow = count_vectorizer()

    def fit(self, X, y):
        self.bow.fit(X)
        return self

    def transform(self, X):
        ret = []
        for sentence in X:
            w2v = np.mean([self.word2vec[w] for w in sentence if w in self.word2vec]
                    or [np.zeros(self.dim)], axis=0)
            bow = self.bow.transform([sentence]).toarray()
            ret.append(np.concatenate([w2v, bow[0]]))
        ret = np.array(ret)
        return ret


class TfidfHybridVectorizer(object):
    def __init__(self, word2vec):
        self.word2vec = word2vec
        self.dim = len(word2vec)
        self.tf = tfidf_vectorizer()


    def fit(self, X, y):
        self.tf.fit(X)
        return self

    def transform(self, X):
        ret = []
        for sentence in X:
            w2v = np.mean([self.word2vec[w] for w in sentence if w in self.word2vec]
                    or [np.zeros(self.dim)], axis=0)
            tf = self.tf.transform([sentence]).toarray()
            ret.append(np.concatenate([w2v, tf[0]]))
        ret = np.array(ret)
        return ret


class SequenceHybridVectorizer(object):
    def __init__(self, word2vec, tfidf=False):
        self.word2vec = word2vec
        self.dim = len(word2vec)
        self.word2weight = None
        self.tfidf = tfidf
        self.bow = count_vectorizer()


    def fit(self, X, y):
        self.bow.fit(X)
        tfidf = tfidf_vectorizer()
        tfidf.fit(X)
        max_idf = max(tfidf.idf_)
        self.word2weight = defaultdict(
            lambda: max_idf,
            [(w, tfidf.idf_[i]) for w, i in tfidf.vocabulary_.items()])
        return self

    def transform(self, X):
        ret = []
        for sentence in X:
            vector = np.array([])
            maxWords = 16
            count = 0
            for word in sentence:
                if count < maxWords:
                    if word in self.word2vec:
                        count += 1
                        if self.tfidf:
                            vector = np.concatenate([vector, self.word2vec[word] * self.word2weight[word]])
                        else:
                            vector = np.concatenate([vector, self.word2vec[word]])
            for i in range(maxWords-count):
                vector = np.concatenate([vector, np.zeros(self.dim)])
            bow = self.bow.transform([sentence]).toarray()
            vector = np.concatenate([vector, bow[0]])
            ret.append(vector)

        ret = np.array(ret)
        return ret



# Setting SVM classifier
def svm_classifier():
    classifier = LinearSVC()
    return classifier


# Train model
def train_model(X, y, classifier, vectorizer):
    model = Pipeline([("vector_model", vectorizer), ("classifer", classifier)])
    model.fit(X, y)
    dill.dump(model, open(answer_type_file, 'wb'))
    return model


# Remove questions with incosiderate_classes
def remove_incosiderate_classes(questions, incosiderate_classes=['X', 'MANNER', 'OBJECT', 'OTHER', 'DEFINITION']):
    ret = []
    for question in questions:
        if question['class'] is not None and question['class'] not in incosiderate_classes:
            ret.append(question)
    return ret

# Separete the questions in data (X) and label (y)
def separete_questions(questions):
    X = []
    y = []
    for question in questions:
        text = question['question']
        text = text.lower()
        text = nltk.word_tokenize(text)
        X.append(text)
        y.append(question['class'])
    return X, y

# Select what class will be inconsiderate in question classification
def inconsiderate_classes(c):
    if c == None:
        return True
    if c == 'X':
        return True
    if c == 'MANNER':
        return True
    if c == 'OBJECT':
        return True
    if c == 'OTHER':
        return True
    return False

# All questions recive in question['predict_class'] the predicted answer type from the model
def predict_answer_type(model, questions):
    ret = []
    for question in questions:
        text = question['question']
        text = text.lower()
        text = nltk.word_tokenize(text)
        question['predict_class'] = model.predict([text])[0]
        if question['predict_class'] == question['class']:
            question['correct_answer_type'] = True
        else:
            question['correct_answer_type'] = False
    return ret

## TESTING ##

def testing(model, X_test, y_test):

        result = model.predict(X_test)
        print('Accuracy:', accuracy_score(result, y_test))
        print('F1 Score:', f1_score(result, y_test, average="macro"))
        cm = confusion_matrix(result, y_test, labels=['LOCATION', 'MEASURE', 'ORGANIZATION', 'PERSON', 'TIME'])
        return cm

def plot_confusion_matrix(cm, classes, normalize=False, title='Confusion matrix', cmap=plt.cm.Blues):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """

    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    fmt = '.2f' if normalize else 'd'
    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, format(cm[i, j], fmt),
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')

def queryFormulation(questions):
    for question in questions:
        question['query'] = make_query(question['question'])
    return questions

def make_query(question_text):
    query = {'fl': 'id', 'rows': str(MAX_DOCUMENTS_RETRIEVAL)}
    q = ''

    """
    # Default
    for word in question_text.split():
        w = util.replace_ponctutation(word)
        if w != '':
            q += ' text:' + w
    query['q'] = q
    """
    """
    # Keywords and distances Old
    keywords = ""
    distance = 5
    for word in question_text.split():
        w = util.replace_ponctutation(word).lower()
        if w != '' and not util.is_stopword(w):
            keywords += w + ' '
    keywords = keywords.strip()
    query = "text:\"" + keywords + "\"~" + str(distance)
    """
    """
    # Keywords and distances New
    distance = '20'
    words = ''
    for word in question_text.split():
        w = util.replace_ponctutation(word).lower()
        if w != '' and not util.is_stopword(w):
            words += ' ' + w
    query = "text:(\"" + words.strip() + "\"~" + distance + ' ' + words.strip() + ')'
    """
    # Distance between terms with edismax
    words = ''
    for word in question_text.split():
        w = util.replace_ponctutation(word).lower()
        if w != '' and not util.is_stopword(w):
            words += ' ' + w
    query['q'] = words.strip()
    query['defType'] = 'edismax'
    query['qf'] = 'text'
    query['pf'] = 'text'
    query['ps'] = '15'
    query['pf2'] = 'text'
    query['ps2'] = '15'
    query['pf3'] = 'text'
    query['ps3'] = '15'

    return query

# Traduz o nome da classe para o modo utilizado no NER (em portugues)
def classPT(name_class):
    name = name_class.lower()
    if name == 'organization':
        return 'ORGANIZACAO'
    if name == 'time':
        return 'TEMPO'
    if name == 'location':
        return 'LOCAL'
    if name == 'measure':
        return 'VALOR'
    if name == 'person':
        return 'PESSOA'
