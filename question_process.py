# -*- coding: utf-8 -*-

import sklearn
import nltk
from collections import Counter


NGRAM = 1
STOPWORD = False
STEMMER = False
LOWER = False
FILTER = True


class QuestionProcess:

    def __init__(self):
        self.pairs = []
        self.train_pairs = []
        self.n_grams = []
        self.clss = []  # Tipos de questões

    def run(self):
        if FILTER:
            self.filter_pairs()
        clss = self.classifications()
        clf = self.train_svm()
        for pair in self.pairs:
            r = clf.predict([self.normalize_question(pair.question)])
            r_classification = clss[r[0]]
            pair.question_classification = r_classification

    def train_svm(self):
        print "Train Started"
        clf = sklearn.svm.LinearSVC(verbose=False)
        # from sklearn.naive_bayes import MultinomialNB
        # clf = MultinomialNB()
        data = self.normalize_questions_train()
        target = self.normalize_classifications_train()
        print '\nData: '+str(len(data)) + ' | Target: ' + str(len(target))

        clf.fit(data, target)
        print "Train Completed"
        return clf

    def filter_pairs(self):
        new_pairs = []
        for pair in self.pairs:
            if not (pair.correct_classification is None
                    or pair.correct_classification.lower().strip() == 'x'):
                new_pairs.append(pair)
        self.pairs = new_pairs
        new_pairs2 = []
        for pair in self.train_pairs:
            if not (pair.correct_classification is None
                    or pair.correct_classification.lower().strip() == 'x'):
                new_pairs2.append(pair)
        self.train_pairs = new_pairs2

    def normalize_question(self, question):
        n_grams = self.ngrams()
        tokens = self.to_tokens(question)
        q_ngrams = Counter(nltk.ngrams(tokens, NGRAM))
        data = []
        for g in n_grams:
            if g in q_ngrams:
                data.append(1)
            else:
                data.append(0)
        return data

    def normalize_classification(self, tp):
        return self.classifications().index(tp)

    def normalize_questions_train(self):
        data = []
        for pair in self.train_pairs:
            data.append(self.normalize_question(pair.question))
        return data

    def normalize_classifications_train(self):
        target = []
        clss = self.classifications()
        for pair in self.train_pairs:
            target.append(clss.index(pair.correct_classification))
        return target

    def ngrams(self):
        interval_print = 1000
        aux_count = 0
        if len(self.n_grams) == 0:
            for pair in self.train_pairs + self.pairs:

                if aux_count == interval_print:
                    aux_count = 0
                    p = str((self.train_pairs + self.pairs).index(pair))
                    a = str(len(self.train_pairs + self.pairs))
                    print p + '/' + a
                else:
                    aux_count += 1

                tokens = self.to_tokens(pair.question)
                q_ngrams = Counter(nltk.ngrams(tokens, NGRAM))

                for g in q_ngrams:
                    if g not in self.n_grams:
                        self.n_grams.append(g)
            print 'ngrams: ' + str(len(self.n_grams))
        return self.n_grams

    def to_tokens(self, text):
        t = text
        if LOWER:
            t = text.lower()
        tokens = nltk.word_tokenize(t)
        if STEMMER:
            stemmer = nltk.stem.RSLPStemmer()
            for i in range(len(tokens)):
                tokens[i] = stemmer.stem(tokens[i])

        if STOPWORD:
            stopwords = nltk.corpus.stopwords.words('portuguese')
            ret = []
            for token in tokens:
                if not (u''+token) in stopwords:
                    ret.append(token)
        else:
            ret = tokens
        return ret

    def classifications(self):
        if len(self.clss) == 0:
            for pair in self.train_pairs + self.pairs:
                if pair.correct_classification not in self.clss:
                    self.clss.append(pair.correct_classification)
        return self.clss
