import json
import urllib
import requests

DEP_MODEL_PATH = 'models/pt-model/dep-parser'  # Relativo a pasta do servidor
POS_MODEL_PATH = 'models/pt-model/pos-tagger.dat'  # Relativo a pasta do servidor
IP = 'localhost'
PORT = 9000


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
                  'outputFormat': outputFormat}  # conllu, json, xml, text

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
