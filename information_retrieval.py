
from SolrClient import SolrClient, IndexQ
import xml.etree.ElementTree as ET
import question_processing as QP
from util import util
from util import corenlp as CNLP
import named_entity_recognition as NER
import glob
import os
import io


CORE_NAME = 'Chave'
PATH_SYSTEM = 'c://solr-7.2.1/'
PATH_DOCUMENTS = 'data/documents/indexing/'
VERSION = '0'
MAX_DOCUMENTS_RETRIEVAL = 10


class InformationRetrieval(object):

    def __init__(self):
        self.solr = None

    def start(self, reset=False):
        if not self.server_status():
            os.system(PATH_SYSTEM + 'bin/solr.cmd start')
        self.solr = SolrClient('http://localhost:8983/solr')

        if reset:
            self.remove_all_documents()

        if not self.has_documents():
            # Indexing
            self.index_documents()

    def stop(self):
        if self.server_status():
            os.system(PATH_SYSTEM + 'bin/solr.cmd stop -all')

    # Return True when server is online
    def server_status(self):
        ret = os.popen(PATH_SYSTEM + 'bin/solr.cmd status').read()
        if not 'No running Solr nodes found.' == ret.strip():
            return True
        return False

    def index_documents(self):
        print('Indexing:')
        '''
        for file_name in glob.glob(PATH_DOCUMENTS + "*.txt"):
            f = io.open(file_name, 'r', encoding='utf-8')
            lines = f.readlines()
            print('File: '+str(len(lines))+' lines: ')
            index = IndexQ('data/documents/', 'indexq', size=len(lines))
            count = 1
            for line in lines:
                count += 1
                document_id = line[:line.index('|')]
                document_text = line[line.index('|')+1:]
                index.add({'id': document_id, 'text': document_text})
            print('End')
            index.add(finalize=True)
            index.index(self.solr, CORE_NAME)
            self.solr.commit(CORE_NAME, openSearcher=True)
        '''
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
                print(str(len(lines))+'/'+str(lines.index(line)))
        print('End')



    def remove_all_documents(self):
        # <delete><query>*:*</query></delete>
        self.solr.delete_doc_by_query(CORE_NAME, '*:*')
        self.solr.commit(CORE_NAME, openSearcher=True)

    def has_documents(self):
        res = self.solr.query(CORE_NAME, {'q': '*:*'})
        if res.get_results_count() > 0:
            return True
        return False

    def retrievalDocuments(self, questions):
        for question in questions:
            ret = self.solr.query(CORE_NAME, {'q': question['query'], 'rows': str(MAX_DOCUMENTS_RETRIEVAL), 'fl': 'id'})
            aux = []
            for doc in ret.docs:
                aux.append(doc['id'])
            question['retrieval'] = aux
        return questions

    def documentText(self, doc_id):
        ret = self.solr.query(CORE_NAME, {'q': 'id:'+doc_id})
        return ret.docs[0]['text']


def retrievalPassages(document_text, ner_model, answer_type=None):
    """
    Retorna as passagens dos documentos e as entidades mencionadas.

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
                if class_entity == QP.classPT(answer_type.lower()):
                    control = True
                    break
        if control:
            passages.append((passage, entitys, count))
        count += 1
    return passages


def retrievalPassagesQuestions(questions, ner_model, ir):
    for question in questions:
        question['passages'] = []
        rank = 1
        for doc_id in question['retrieval']:
            text = ir.documentText(doc_id)
            passages = retrievalPassages(text, ner_model, question['predict_class'])
            for passage in passages:
                question['passages'].append({
                    'passage': passage[0], 'entitys': passage[1], 'sequence': passage[2], 'doc_id': doc_id, 'doc_rank': rank
                    })
            rank += 1

    return questions
