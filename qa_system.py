# -*- coding: utf-8 -*-

import question_process  # Módulo de processamento da questão
# import ir_documents  # Módulo de Information Retrivial
# import answer_process  # Módulo de processamento da resposta


class QASystem:
    def __init__(self):
        self.questionProcess = question_process.QuestionProcess()
        # self.informationRetrivial = None
        # self.answerProcess = None


class Pair(object):  # Representa um par (Pergunta e Resposta) e suas informações complementares

    def __init__(self):
        self.question = None  # Pergunta

        # Informações utilizada na classificação da questões em classes
        self.correct_classification = None  # Classe correta da questão
        self.question_classification = None  # Classe atribuida pelo sistema (isto que se quer classificar)

        # Informações utilizadas em Information Retrivial
        self.docs_id = []  # Documentos buscados pelo sistema
        self.correct_docs_id = []  # Documentos corretos do dataset

        # Informações utilizada no processamento da resposta
        self.answers = []  # Respostas geradas pelo sistema
        self.correct_answers = []  # Repostas corretas do dataset

        # Informações complementares do dataset
        self.question_type = None
        self.question_category = None
        self.question_restriction = None
        self.extractos = []  # Passagens que contém a resposta
