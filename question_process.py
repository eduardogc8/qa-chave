# -*- coding: utf-8 -*-

import sklearn
import nltk


MIN_NGRAMS = 1
MAX_NGRAMS = 1
TFIDF = False
LOWER = False  # Passar as questões para minúsculo
STEMMER = False
STOPWORD = False


class QuestionProcess:  # Determina a classe da questão (ok) e gera a query de consulta (ToDo)

    def __init__(self):
        self.pairs = []  # Pares para avaliação
        self.train_pairs = []  # Pares para treinamento
        self.transform = None  # Transforma as questões em input para a SVM
        self.question_class = []  # Classes de questões

    # Classifica as questões dos pares de avaliação
    def question_classification(self):
        question_class = self.classifications()
        clf = self.train_svm()  # Treina uma SVM para classificar
        print "Predicting..."
        for pair in self.pairs:  # Para cada par é classificado o tipo da sua questão
            class_out = clf.predict(self.transform_data(pair.question))
            pair.question_classification = question_class[class_out[0]]
        print 'Finished Question Classification\n'

    # Treina a SVM Linear
    def train_svm(self):
        clf = sklearn.svm.LinearSVC(verbose=False)
        # from sklearn.naive_bayes import MultinomialNB
        # clf = MultinomialNB()
        print 'Transforming...'
        data = self.transform_data_train()
        target = self.transform_classifications_train()
        print 'Data: '+str(len(data)) + ' | Target: ' + str(len(target))
        print "Training..."
        clf.fit(data, target)
        return clf

    # Normaliza o conjunto de treinamento de entrada
    def transform_data_train(self):
        questions = []
        for pair in self.train_pairs:
            questions.append(self.treat_question(pair.question))
        if TFIDF:
            # TF-IDF
            print 'TF-IDF Transform'
            from sklearn.feature_extraction.text import TfidfVectorizer
            self.transform = TfidfVectorizer(strip_accents=None, ngram_range=(MIN_NGRAMS, MAX_NGRAMS), token_pattern=u'(?u)\\b\\w+\\b', lowercase=LOWER)
        else:
            # Bag of Words
            print 'Bag of Words Transform'
            from sklearn.feature_extraction.text import CountVectorizer
            self.transform = CountVectorizer(strip_accents=None, ngram_range=(MIN_NGRAMS, MAX_NGRAMS), token_pattern=u'(?u)\\b\\w+\\b', lowercase=LOWER)

        x = self.transform.fit_transform(questions)
        print 'Input size: '+str(len(x.toarray()[0]))
        return x.toarray()

    def transform_data(self, text):
        return self.transform.transform([text]).toarray()

    # Transforma o conjunto de treinamento de saída
    def transform_classifications_train(self):
        target = []
        question_class = self.classifications()
        for pair in self.train_pairs:
            target.append(question_class.index(pair.correct_classification))
        return target

    # Recebe um texto e cria os tokens e reliza um pré-processamento se estiver parametrizado
    def treat_question(self, text):
        t = text
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
        return " ".join(str(x) for x in ret)

    # Determina quais são as possíveis classes de questões
    def classifications(self):
        if len(self.question_class) == 0:
            for pair in self.train_pairs + self.pairs:
                if pair.correct_classification not in self.question_class:
                    self.question_class.append(pair.correct_classification)
        return self.question_class
