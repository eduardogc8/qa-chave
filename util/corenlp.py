import json
import urllib
import requests

DEP_MODEL_PATH = 'models/pt-model/dep-parser'  # Relativo a pasta do servidor
POS_MODEL_PATH = 'models/pt-model/pos-tagger.dat'  # Relativo a pasta do servidor
IP = 'localhost'
PORT = 9000


def call(text, annotators, tokenizeWhitespace='false', outputFormat='xml'):
    properties = {'tokenize.whitespace': tokenizeWhitespace,
                  'annotators': annotators,
                  'depparse.model': DEP_MODEL_PATH,
                  'pos.model': POS_MODEL_PATH,
                  'outputFormat': outputFormat  # conllu, json, xml, text
                 }

    properties_val = json.dumps(properties)

    params = {'properties': properties_val}
    encoded_params = urllib.parse.urlencode(params)
    url = 'http://{ip}:{port}/?{params}'.format(ip=IP, port=PORT,
                                                params=encoded_params)

    headers = {'Content-Type': 'text/plain;charset=utf-8'}
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
