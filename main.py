# -*- coding: utf-8 -*-
import manager_dataset
import qa_system
import result

#Seleciona as perguntas com resposta do data_set
perguntas = manager_dataset.with_valid_resposta()
manager_dataset.index_documents()

#Obtem a lista de resposta para as perguntas
respostas = qa_system.process_questions(perguntas)

#Produz o arquivo de resultados
result.produce(perguntas, respostas)