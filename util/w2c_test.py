# -*- coding: utf-8 -*-

import gensim
import operator
import nltk

class_terms = [u'tempo', u'definição', u'medida', u'localização', u'pessoa', u'organização']

class_synonyms_ = [u'tempo prazo duração período dia data ciclo horas momento ano fase etapa mês século minuto segundo',  # TIME
                  u'definição manifestação explicação descrição declaração',  # DEFINITION
                  u'medida grandeza dimensão tamanho proporção quantidade capacidade contagem número escore placar pontuação',  # MEASURE
                  u'localização posição ponto lugar local posicionamento instalação situação locação colocação',  # LOCATION
                  u'pessoa personagem humano criatura indivíduo mulher ente consciência cidadão homem sujeito',  # PERSON
                  u'organização organismo órgão coletividade entidade associação instituição corporação sociedade corpo constituição físico temperamento compleição estrutura'  # ORGANIZATION
                  ]

class_synonyms = [
                  u'pessoa personagem humano criatura indivíduo mulher cidadão homem sujeito criador autor presidente senador prefeito deputado vereador capitão secretário papa diretor santo scritor deuses rei rainha príncipe filho pai mãe avo tio primo irmão músico inventor princesa criança filho sobrinho celebridade marido esposa cantor engenheiro arquiteto fundador artista estudioso professor proprietário',  # PERSON
                  u'organização partido empresa grupo polícia companhia fundação time clube orquestra circo estúdio universidade fábrica armazém company cidade agência banda seleção departamento país academia museu prefeitura equipe força conselho'  # ORGANIZATION
                  ]

def test(pairs):
    w2v = gensim.models.Word2Vec.load("dataset/w2v/pt.bin")
    w2v.init_sims(replace=True)
    ret = []
    for pair in pairs:
        print pairs.index(pair), '/', len(pairs)
        text = pair.question
        stopwords = nltk.corpus.stopwords.words('portuguese')
        tokens = nltk.word_tokenize(text)
        tkns = []
        for token in tokens:
            if not (u''+token) in stopwords:
                tkns.append(token)
        text = " ".join(str(x) for x in tkns).decode('utf-8')
        if not (pair.correct_classification == 'PERSON' or pair.correct_classification == 'ORGANIZATION'): continue
        distances = {}
        for class_term in class_synonyms:
            distance = w2v.wmdistance(text.decode('utf-8').split(), class_term.split())
            distances[class_term.split()[0]] = distance
        distances = sorted(distances.items(), key=operator.itemgetter(1), reverse=False)
        d = distances[0][0]
        if d == u'tempo': d = 'TIME'
        if d == u'definição': d = 'DEFINITION'
        if d == u'medida': d = 'MEASURE'
        if d == u'localização': d = 'LOCATION'
        if d == u'pessoa': d = 'PERSON'
        if d == u'organização': d = 'ORGANIZATION'
        pair.question_classification = d
        ret.append(pair)

    ret2 = []
    count1 = 0
    count2 = 0
    for p in ret:
        if count1 < 350 and p.correct_classification == 'PERSON':
            ret2.append(p)
            count1 += 1
        if count2 < 350 and p.correct_classification == 'ORGANIZATION':
            ret2.append(p)
            count2 += 1
    return ret2
