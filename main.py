# -*- coding: utf-8 -*-
import manager_dataset
import qa_system
import result
import random

# Obtem os pares válidos e inválidos
v, v2 = manager_dataset.valid_invalid_pairs()

# Pares para treinamento e testes pegos aleatoriamente (usando SEED) para cross validation
SEED = 1
p = v + v2
k = 8  # 2,4 or 8
random.seed(SEED)
random.shuffle(p)
len(p)
len(p)/float(k)
results = []
s = len(p)/k
for i in range(k):
    # Executa o sistema e retorna os pares de pergunta e resposta
    print (i+1), '/', k
    v = p[i*s:i*s+s]  # Conjunto de teste
    v2 = p[:i*s] + p[i*s+s:]  # Conjunto de treinamento
    qas = qa_system.QASystem()
    qas.qp.pairs = v
    qas.qp.train_pairs = v2
    qas.qp.run()
    results.append(qas.qp.pairs)
result.qc_procude(results)
# Produz o arquivo de resultados
# result.produce(qas.qp.pairs)
