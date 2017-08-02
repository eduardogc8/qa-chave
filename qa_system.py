# -*- coding: utf-8 -*-

import question_process
# import ir_documents
# import answer_process


class QASystem:
    def __init__(self):
        self.qp = question_process.QuestionProcess()
        self.ir = None
        self.ap = None


class Pair(object):

    def __init__(self):
        self.question = None  # Perguntas do dataset

        self.correct_classification = None
        self.question_classification = None

        self.correct_type = None
        self.question_type = None

        self.question_category = None
        self.question_restriction = None

        self.answers = []  # Respostas geradas pelo sistema
        self.correct_answers = []  # Repostas corretas do dataset

        self.docs_id = []  # Documentos buscados pelo sistema
        self.correct_docs_id = []  # Documentos corretos do dataset

        self.extractos = []  # Passagens cque contém a resposta
