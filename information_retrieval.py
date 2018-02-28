
from SolrClient import SolrClient, IndexQ
import xml.etree.ElementTree as ET
from util import util
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
            ret = self.solr.query(CORE_NAME, {'q': question['query'], 'rows':str(MAX_DOCUMENTS_RETRIEVAL)})
            aux = []
            for doc in ret.docs:
                aux.append(doc['id'])
            question['retrieval'] = aux
        return questions

    def documentText(self, doc_id):
        ret = self.solr.query(CORE_NAME, {'q': 'id:'+doc_id})
        return ret.docs[0]['text']
