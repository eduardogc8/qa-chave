import os
import json
import urllib
import socket
import requests
import xml.etree.ElementTree as ET


DEP_MODEL_PATH = 'c://corenlp/models/pt-model/dep-parser'  # Relativo a pasta do servidor
POS_MODEL_PATH = 'c://corenlp/models/pt-model/pos-tagger.dat'  # Relativo a pasta do servidor
NER_MODEL_PATH = 'c://corenlp/models/pt-model/ner_model.ser.gz'  # Relativo a pasta do servidor
PATH_SYSTEM = 'c://corenlp/'
IP = 'localhost'
PORT = 9000


# Return True when server is online
def server_status():
    """Check server status."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((IP, PORT))
    if not result == 0:
        return False
    return True


def tokens_pos(text):
    """Dado um texto de entrada, eh retornado duas lista, os tokens do texto e as POS."""
    tokens = []
    pos = []
    output = call(text, 'tokenize,pos')
    root = ET.fromstring(output)
    sentences = root[0][0]
    for sentence in sentences:
        s_tokens = sentence[0]
        for token in s_tokens:
            tokens.append(token[0].text)
            pos.append(token[3].text)
    return tokens, pos


def pos(text, index):
    """Dado um texto de entrada, eh retornado duas lista, os tokens do texto e as POS."""
    return tokens_pos(text)[1][index]


def ssplit(text):
    """Dado um texto de entrada, eh retornado a lista de sentencas."""
    passages = []
    output = call(text, 'ssplit', outputFormat='text')
    control = False
    for line in output.split('\r\n'):
        if control:
            passages.append(line)
            control = False
        elif 'Sentence #' in line:
            control = True
    return passages


def call(text, annotators, outputFormat='xml'):
    """
    Realiza uma chamada no servidor CoreNLP (o servidor deve estar ligado).

    Ligar servidor. Ir na pasta do CorneNLP e executar o seguinte comando na cmd:
    "java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer".
    text eh o input em string.
    annotators define os as funcoes a serem executadas em textself.
        exemplo: annotators='tokenize,ssplit,pos,depparse'
    outputFormat eh o formato de saida (conllu, json, xml, text).
    """
    properties = {'tokenize.whitespace': 'false',
                  'annotators': annotators,
                  'depparse.model': DEP_MODEL_PATH,
                  'pos.model': POS_MODEL_PATH,
                  'ner.model': NER_MODEL_PATH,
                  'outputFormat': outputFormat}  # conllu, json, xml, text

    properties_val = json.dumps(properties)

    params = {'properties': properties_val}
    encoded_params = urllib.parse.urlencode(params)
    url = 'http://{ip}:{port}/?{params}'.format(ip=IP, port=PORT,
                                                params=encoded_params)
    headers = {'Content-Type': 'text/plain;charset=utf-8'}

    if not server_status():
        # Conectar
        print("start java -mx4g -cp " + PATH_SYSTEM + "\"*\"  edu.stanford.nlp.pipeline.StanfordCoreNLPServer")
        os.system("start java -mx4g -cp " + PATH_SYSTEM + "\"*\"  edu.stanford.nlp.pipeline.StanfordCoreNLPServer")
    response = requests.post(url, text.encode('utf-8'), headers=headers)
    response.encoding = 'utf-8'
    output = response.text.replace('\0', '')
    return output


# Testing
def call_corenlp(text, dep_model_path, pos_model_path, ip, port):
    """
    Chama o parser do CoreNLP em um servidor.

    Creditos: Erik do http://linguaecomputador.blogspot.com.br
    """
    properties = {'tokenize.whitespace': 'true',
                  'annotators': 'tokenize,ssplit,pos,depparse',
                  'depparse.model': dep_model_path,
                  'pos.model': pos_model_path,
                  'outputFormat': 'xml'}

    # converte o dicionário em uma string
    properties_val = json.dumps(properties)

    # codifica os parâmetros com urllib para usar parâmetros GET. O conteúdo
    # do POST é o texto
    params = {'properties': properties_val}
    encoded_params = urllib.parse.urlencode(params)
    url = 'http://{ip}:{port}/?{params}'.format(ip=ip, port=port,
                                                params=encoded_params)

    headers = {'Content-Type': 'text/plain;charset=utf-8'}
    response = requests.post(url, text.encode('utf-8'), headers=headers)
    response.encoding = 'utf-8'

    # apenas para ter certeza...
    output = response.text.replace('\0', '')

    return output
