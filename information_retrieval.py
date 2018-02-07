
from SolrClient import SolrClient
import os


CORE_NAME = 'Chave'
PATH_SYSTEM = 'c://solr-7.2.1/'

class InformationRetrieval(object):

    def __init__(self):
        self.solr = None

    def start(self):
        if not self.check_status():
            os.system(PATH_SYSTEM + 'bin/solr.cmd start')
        self.solr = SolrClient('http://localhost:8983/solr')

    def stop(self):
        if self.check_status():
            os.system(PATH_SYSTEM + 'bin/solr.cmd stop -all')

    def check_status(self):
        ret = os.popen(PATH_SYSTEM + 'bin/solr.cmd status').read()
        if not 'No running Solr nodes found.' == ret.strip():
            return True
        print('here')
        return False
