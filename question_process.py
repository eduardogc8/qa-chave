# -*- coding: utf-8 -*-

import sklearn
import nltk
from collections import Counter


NGRAM = 1
STOPWORD = False  # Remover as stopwords das questões
STEMMER = False  # Fazer Stemming nas questões
LOWER = False  # Passar as questões para minúsculo


class QuestionProcess:  # Determina a classe da questão (ok) e gera a query de consulta (ToDo)

    def __init__(self):
        self.pairs = []  # Pares para avaliação
        self.train_pairs = []  # Pares para treinamento
        self.n_grams = []  # Armazena os n-gramas na memŕoia para não precisar processar eles todas as vezes
        self.question_class = []  # Classes de questões

    # Classifica as questões dos pares de avaliação
    def run(self):
        question_class = self.classifications()
        clf = self.train_svm()  # Treina uma SVM para classificar
        print "Predicting..."
        for pair in self.pairs:  # Para cada para é classificado o tipo da sua questão
            class_out = clf.predict([self.normalize_question(pair.question)])
            pair.question_classification = question_class[class_out[0]]
        print 'End Processing\n'

    # Treina a SVM Linear
    def train_svm(self):
        clf = sklearn.svm.LinearSVC(verbose=False)
        # from sklearn.naive_bayes import MultinomialNB
        # clf = MultinomialNB()
        print 'Normalizing...'
        data = self.normalize_questions_train()
        target = self.normalize_classifications_train()
        print 'Data: '+str(len(data)) + ' | Target: ' + str(len(target))
        print "Training..."
        clf.fit(data, target)
        return clf

    # Normaliza a questão para input na SVM
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

    # Normaliza a classe da questão para output na SVM
    def normalize_classification(self, question_class):
        return self.classifications().index(question_class)

    # Normaliza o conjunto de treinamento de entrada
    def normalize_questions_train(self):
        data = []
        for pair in self.train_pairs:
            data.append(self.normalize_question(pair.question))
        return data

    # Normaliza o conjunto de treinamento de saída
    def normalize_classifications_train(self):
        target = []
        question_class = self.classifications()
        for pair in self.train_pairs:
            target.append(question_class.index(pair.correct_classification))
        return target

    # Cria os possíveis ngram do dataset, processando o conjunto de treinament e o de avaliação
    def ngrams(self):
        if len(self.n_grams) == 0:
            print "Processing N-grams..."
            for pair in self.train_pairs + self.pairs:
                tokens = self.to_tokens(pair.question)
                q_ngrams = Counter(nltk.ngrams(tokens, NGRAM))

                for g in q_ngrams:
                    if g not in self.n_grams:
                        self.n_grams.append(g)
            print 'ngrams: ' + str(len(self.n_grams))
        return self.n_grams

    # Recebe um texto e cria os tokens e reliza um pré-processamento se estiver parametrizado
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

    # Determina quais são as possíveis classes de questões
    def classifications(self):
        if len(self.question_class) == 0:
            for pair in self.train_pairs + self.pairs:
                if pair.correct_classification not in self.question_class:
                    self.question_class.append(pair.correct_classification)
        return self.question_class
