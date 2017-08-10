# -*- coding: utf-8 -*-

import sklearn
import nltk
import gensim
import numpy as np

MIN_NGRAMS = 1
MAX_NGRAMS = 1
TFIDF = False
WORD2VEC = True
LOWER = False  # Passar as questões para minúsculo
STEMMER = False
STOPWORD = False

#ToDo - OTHER
class_synonyms = [u'tempo prazo duração período dia data prazo ciclo horas momento ano fase etapa mês século minuto segundo',  # TIME
                  u'definição manifestação explicação descrição declaração',  # DEFINITION
                  u'medida grandeza dimensão tamanho proporção quantidade capacidade contagem número escore placar pontuação',  # MEASURE
                  u'localização posição ponto lugar local posicionamento instalação situação locação colocação',  # LOCATION
                  u'pessoa personagem humano criatura indivíduo mulher ente consciência cidadão homem sujeito',  # PERSON
                  u'organismo órgão coletividade entidade associação instituição corporação sociedade corpo constituição físico temperamento compleição estrutura'  # ORGANIZATION
                  ]


class QuestionProcess:  # Determina a classe da questão (ok) e gera a query de consulta (ToDo)

    def __init__(self):
        self.pairs = []  # Pares para avaliação
        self.train_pairs = []  # Pares para treinamento
        self.transform = None  # Transforma as questões em input para a SVM
        self.question_class = []  # Classes de questões
        self.word2vec_model = None

    # Classifica as questões dos pares de avaliação
    def question_classification(self):
        question_class = self.classifications()
        clf = self.train_svm()  # Treina uma SVM para classificar
        print "Predicting..."
        for pair in self.pairs:  # Para cada par é classificado o tipo da sua questão
            class_out = clf.predict(self.transform_data(self.treat_question(pair.question)))
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
        ret = x.toarray()
        if WORD2VEC:
            print 'Word2Vec...'
            self.word2vec_model = gensim.models.Word2Vec.load("dataset/w2v/pt.bin")
            self.word2vec_model.init_sims(replace=True)

            # Adicionar novas dimensões
            z = np.zeros((len(ret), len(class_synonyms)))
            old_ret0_size = len(ret[0])
            ret = np.concatenate((ret, z), axis=1)
            # ret = np.zeros((len(ret), len(class_synonyms))) # Comment
            # old_ret0_size = 0 # Comment
            # Atribuir valor para as novas dimensões
            for question in questions:
                for synonyms in class_synonyms:
                    distance = self.word2vec_model.wmdistance(question.split(), synonyms.split())
                    if distance == float('NaN') or distance == float('Inf') or distance == -float('Inf'):
                        distance = 1.0
                    i = questions.index(question)
                    j = old_ret0_size + class_synonyms.index(synonyms)
                    ret[i][j] = distance
        print 'Input size: '+str(len(ret[0]))
        return ret

    def transform_data(self, text):
        ret = self.transform.transform([self.treat_question(text)]).toarray()

        if WORD2VEC:
            z = np.zeros((1, len(class_synonyms)))
            old_ret0_size = len(ret[0])
            ret = np.concatenate((ret, z), axis=1)
            # ret = np.zeros((len(ret), len(class_synonyms))) # Comment
            # old_ret0_size = 0 # Comment
            for synonyms in class_synonyms:
                distance = self.word2vec_model.wmdistance(text.split(), synonyms.split())
                if distance == float('NaN') or distance == float('Inf') or distance == -float('Inf'):
                    distance = 1.0
                j = old_ret0_size + class_synonyms.index(synonyms)
                ret[0][j] = distance
        return ret

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
        return " ".join(str(x) for x in ret).decode('utf-8')

    # Determina quais são as possíveis classes de questões
    def classifications(self):
        if len(self.question_class) == 0:
            for pair in self.train_pairs + self.pairs:
                if pair.correct_classification not in self.question_class:
                    self.question_class.append(pair.correct_classification)
        return self.question_class
