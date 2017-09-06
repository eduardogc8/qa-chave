# -*- coding: utf-8 -*-
import manager_dataset  # Responsável por obter os dados do dataset
import qa_system  # Funcionamento do Sistema de QA
import result  # Responsável por gerar a saída de resultados
import random

from util import w2c_test

# Obtem os pares válidos (com resposta) e inválidos (sem respostas)
v, inv = manager_dataset.valid_invalid_pairs()

# Pares para treinamento e testes pegos aleatoriamente (usando SEED) para cross-validation (k-fold)
k = 5  # Está sendo usado k = 8
SEED = 1  # Está sendo usando a SEED 1
random.seed(SEED)
p = v + inv  # As questões válidas e inválidas são juntadas e embaralhadas
random.shuffle(p)
s = len(p)/k  # Tamanho do conjunto de avaliação
results = []  # Irá conter k resultados para o cross-validation (k-fold)

for i in range(k):
    print (i+1), '/', k
    a = p[i*s:i*s+s]  # Conjunto de avaliação
    t = p[:i*s] + p[i*s+s:]  # Conjunto de treinamento
    qas = qa_system.QASystem()  # Cria um sistema de QA para classificar as questões
    qas.questionProcess.pairs = a  # Define o conjunto de avaliação
    qas.questionProcess.train_pairs = t  # Define o conjunto de treinamento
    qas.questionProcess.question_classification()
    results.append(qas.questionProcess.pairs)
result.qc_procude(results)

#result.produce(w2c_test.test(p))
