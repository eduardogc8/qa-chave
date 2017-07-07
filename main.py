# -*- coding: utf-8 -*-
import manager_dataset
import qa_system
import result


#Controle de testes

# Parâmetros Question Process

valid, invalid = manager_dataset.valid_invalid_pairs()

#Executa o sistema e retorna os pares de pergunta e resposta
qas = qa_system.QASystem()
qas.qp.pairs = valid
qas.qp.train_pairs = invalid
qas.qp.run()

#Produz o arquivo de resultados
result.produce(qas.qp.pairs)