
from SolrClient import SolrClient, IndexQ
import xml.etree.ElementTree as ET
import question_processing as QP
from util import util
from util import corenlp as CNLP
import named_entity_recognition as NER
import numpy as np
import socket
import glob
import os
import io


CORE_NAME = 'Chave'
PATH_SYSTEM = 'data/solr/'
PATH_DOCUMENTS = 'data/documents/indexing/'
VERSION = '0'
IP = 'localhost'
PORT = 8983


class InformationRetrieval(object):

    def __init__(self):
        """Contructor."""
        self.solr = None

    def start(self, reset=False):
        """
        Start IR server.

        When reset is true, all documents is removed and indexed again.
        If IR system has no documents indexed, then the documents will be indexed.
        """
        if not self.server_status():
            os.system(PATH_SYSTEM + 'start bin/solr.cmd start -p '+str(PORT))
        self.solr = SolrClient('http://localhost:'+str(PORT)+'/solr')

        if reset:
            self.remove_all_documents()

        if not self.has_documents():
            # Indexing
            self.index_documents()

    def stop(self):
        """Stop IR server."""
        if self.server_status():
            os.system(PATH_SYSTEM + 'bin/solr.cmd stop -all')

    # Return True when server is online
    def server_status(self):
        """Check server status."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((IP, PORT))
        if not result == 0:
            return False
        return True

    def index_documents(self):
        """Index documents."""
        print('Indexing:')
        for file_name in glob.glob(PATH_DOCUMENTS + "*.txt"):
            f = io.open(file_name, 'r', encoding='utf-8')
            lines = f.readlines()
            print('File: '+str(len(lines))+' lines: ')
            docs = []
            for line in lines:
                document_id = line[:line.index('|')]
                document_text = line[line.index('|')+1:]
                document_text = util.treat_text(document_text)
                docs.append({'id': document_id, 'text': document_text})
                if len(docs) >= 1000:
                    self.solr.index(CORE_NAME, docs)
                    self.solr.commit(CORE_NAME, openSearcher=True)
                    # print(str(len(lines))+'/'+str(lines.index(line)))
                    docs = []
            if len(docs) > 0:
                self.solr.index(CORE_NAME, docs)
                self.solr.commit(CORE_NAME, openSearcher=True)
        print('End')

    def remove_all_documents(self):
        """Remove all documents from IR system."""
        # <delete><query>*:*</query></delete>
        self.solr.delete_doc_by_query(CORE_NAME, '*:*')
        self.solr.commit(CORE_NAME, openSearcher=True)

    def has_documents(self):
        """Check if the IR system has one or more documents indexed."""
        res = self.solr.query(CORE_NAME, {'q': '*:*'})
        if res.get_results_count() > 0:
            return True
        return False

    def retrievalDocuments(self, questions, printing=True):
        """For each question is retrieval the docid."""

        if printing:
            count = 0
            print('Retrieval Documents [', end=' ')
        for question in questions:
            if printing:
                if count < len(questions) / 10:
                    count += 1
                else:
                    print('.', end=' ')
                    count = 0

            ret = self.solr.query(CORE_NAME, question['query'])
            aux = []
            for doc in ret.docs:
                aux.append(doc['id'])
            question['retrieval'] = aux
        if printing:
            print('. ]')
        return questions

    def documentText(self, doc_id):
        """Return documentText fo a input ID Doc."""
        ret = self.solr.query(CORE_NAME, {'q': 'id:'+doc_id})
        return ret.docs[0]['text']


def test_ir_system(questions):
    """Print precision, recall and f-score."""
    precisions = []
    recalls = []
    f_scores = []
    for question in questions:
        relevants = []
        for answer in question['answers']:
            if answer['doc'] is not None and len(answer['doc']) > 0:
                relevants.append(answer['doc'].strip())
        total_relevants = len(relevants)
        if total_relevants == 0:
            continue
        relevants_retrieval = 0
        for retrieval in question['retrieval']:
            if retrieval.strip() in relevants:
                relevants_retrieval += 1
        if len(question['retrieval']) == 0:
               # print(question['query'])
                precision = 0
        else:
            precision = relevants_retrieval / len(question['retrieval'])
        precisions.append(precision)
        recall = relevants_retrieval / total_relevants
        recalls.append(recall)
        if (precision + recall) == 0:
            f_score = 0
        else:
            f_score = 2 * ((precision * recall) / (precision + recall))
        f_scores.append(f_score)

    print('Precision: '+str(np.mean(precisions)))
    print('Recall: '+str(np.mean(recalls)))
    print('F-Score: '+str(np.mean(f_scores)))


def retrievalPassages(document_text, ner_model, answer_type=None):
    """
    Retorna as passagens dos documentos que tenha ao menos uma entidade desejada e as entidades mencionadas.

    retorna [(passage, entitys, sequence)]
    passage: string
    entitys: ['O', 'CLASS-B', ...]
    sequence: int. Caso seja fitrada as sentencas por classe, o numero da sequencia
    sera mantido pela lista original. Exemplo com filtro: 1, 2, 5, 7.
    """
    allPassages = CNLP.ssplit(document_text)
    passages = []
    if answer_type is None or ner_model is None:
        count = 1
        for passage in allPassages:
            entitys = NER.predict(ner_model, passage)[0]
            passages.append((passage, entitys, count))
            count += 1
        return passages

    count = 1
    for passage in allPassages:
        entitys = NER.predict(ner_model, passage)[0]
        control = False  # Se a passage contem ao menos um entidade mencionada de classe igual ao tipo de resposta
        for entity in entitys:
            if '-' in entity:  # Se eh uma entidade mencionada
                class_entity = entity[:entity.index('-')].lower()
                if class_entity == QP.classPT(answer_type.lower()).lower():
                    control = True
                    break
        if control:
            passages.append((passage, entitys, count))
        count += 1
    return passages


def retrievalPassagesQuestions(questions, ner_model, ir, answer_type=True, printing=True):
    """Para cada question in questions eh recuperado as passagens que tenha ao menos uma entidade de mesma predict_class."""
    if printing:
        count = 0
        print('Passages Retrieval [', end=' ')
    for question in questions:
        if printing:
            if count < len(questions) / 10:
                count += 1
            else:
                print('.', end=' ')
                count = 0

        question['passages'] = []
        rank = 1
        for doc_id in question['retrieval']:
            text = ir.documentText(doc_id)
            if answer_type:
                passages = retrievalPassages(text, ner_model, question['predict_class'])
            else:
                passages = retrievalPassages(text, ner_model)
            for passage in passages:
                question['passages'].append({
                    'passage': passage[0], 'entitys': passage[1], 'sequence': passage[2], 'doc_id': doc_id, 'doc_rank': rank
                    })
            rank += 1
    if printing:
        print('. ]')
    return questions
