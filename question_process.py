# -*- coding: utf-8 -*-

import sklearn
import nltk
import gensim
import numpy as np

MIN_NGRAMS = 1
MAX_NGRAMS = 1
TFIDF = False
WORD2VEC = False
LOWER = False  # Passar as questões para minúsculo
STEMMER = False
STOPWORD = False

# ToDo - OTHER
class_synonyms = [u'tempo prazo duração período dia data ciclo horas momento ano fase etapa mês século minuto segundo',  # TIME
                  u'definição manifestação explicação descrição declaração',  # DEFINITION
                  u'medida grandeza dimensão tamanho proporção quantidade capacidade contagem número escore placar pontuação',  # MEASURE
                  u'localização posição ponto lugar local posicionamento instalação situação locação colocação',  # LOCATION
                  u'pessoa personagem humano criatura indivíduo mulher ente consciência cidadão homem sujeito',  # PERSON
                  u'organização organismo órgão coletividade entidade associação instituição corporação sociedade corpo constituição físico temperamento compleição estrutura'  # ORGANIZATION
                  ]

class_terms = [u'tempo', u'definição', u'medida', u'localização', u'pessoa', u'organização']


class QuestionProcess:  # Determina a classe da questão (ok) e gera a query de consulta (ToDo)

    def __init__(self):
        self.pairs = []  # Pares para avaliação
        self.train_pairs = []  # Pares para treinamento
        self.transform = None  # Transforma as questões em input para a SVM
        self.question_class = []  # Classes de questões
        self.word2vec_model = None
        self.word2vec_distances = None
        self.dictionary_terms = None

    # Classifica as questões dos pares de avaliação
    def question_classification(self):
        question_class = self.classifications()
        clf = self.train_svm()  # Treina uma SVM para classificar
        print "Predicting..."
        for pair in self.pairs:  # Para cada par é classificado o tipo da sua questão
            data_in = self.transform_data(self.treat_question(pair.question))
            #print pair.question
            #print self.treat_question(pair.question)
            #print data_in
            class_out = clf.predict(data_in)
            pair.question_classification = question_class[class_out[0]]
        print 'Finished Question Classification\n'

    # Treina a SVM Linear
    def train_svm(self):
        from sklearn.svm import SVC
        clf = sklearn.svm.LinearSVC(verbose=False)
        #clf = SVC(kernel="linear")
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
        # print self.transform.get_feature_names()
        ret = x.toarray()
        if WORD2VEC:
            print 'Word2Vec...'
            z = np.zeros((len(ret), len(self.transform.get_feature_names()*len(class_terms))))
            old_ret0_size = len(ret[0])
            ret = np.concatenate((ret, z), axis=1)
            # ret = np.zeros((len(ret), len(self.transform.get_feature_names()*len(class_terms)))) # Comment
            # old_ret0_size = 0 # Comment
            # Atribuir valor para as novas dimensões
            count = 0
            for question in questions:
                if count == 0 or count > 1000:
                    print str(questions.index(question))+" / "+str(len(questions))
                    count = 0
                count += 1
                w2v_input = self.word2vec_input(self.treat_question(question))
                i = questions.index(question)
                new_input = np.concatenate((ret[i][:old_ret0_size], w2v_input))
                ret[i] = new_input
                # np.set_printoptions(threshold='nan')
                # print ret[i]
        print 'Input size: '+str(len(ret[0]))
        return ret

    def transform_data(self, text):
        ret = self.transform.transform([text]).toarray()

        if WORD2VEC:
            z = np.zeros((1, len(self.transform.get_feature_names()*len(class_terms))))
            old_ret0_size = len(ret[0])
            ret = np.concatenate((ret, z), axis=1)
            # ret = np.zeros((1, len(self.transform.get_feature_names()*len(class_terms)))) # Comment
            # old_ret0_size = 0 # Comment
            # Atribuir valor para as novas dimensões
            w2v_input = self.word2vec_input(self.treat_question(text))
            new_input = np.concatenate((ret[0][:old_ret0_size], w2v_input))
            ret[0] = new_input
        return ret

    def word2vec_input(self, text):
        if self.dictionary_terms is None:
            self.dictionary_terms = self.transform.get_feature_names()

        ret = np.zeros(len(self.dictionary_terms)*len(class_terms))
        if self.word2vec_model is None:
            self.word2vec_model = gensim.models.Word2Vec.load("data/word_embedding/pt.bin")
            self.word2vec_model.init_sims(replace=True)

        if self.word2vec_distances is None:
            self.word2vec_distances = {}
            for class_term in class_terms:
                self.word2vec_distances[class_term] = {}
                for term in self.dictionary_terms:
                    if term in self.word2vec_model and class_term in self.word2vec_model:
                        similarity = self.word2vec_model.similarity([class_term], [term])
                    else:
                            similarity = 0
                    self.word2vec_distances[class_term][term] = similarity

        l = len(self.dictionary_terms)
        for class_term in class_terms:
            c = class_terms.index(class_term)
            for term in text:
                if term in self.dictionary_terms:
                    similarity = self.word2vec_distances[class_term][term]
                    i = self.dictionary_terms.index(term) + l*c
                    ret[i] = similarity
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
        if not (STEMMER or STOPWORD):
            return text.decode('utf-8')
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
