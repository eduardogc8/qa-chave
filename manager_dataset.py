# -*- coding: utf-8 -*-

import xml.etree.ElementTree as et
import qa_system
import re

path_questions = "data/questions.xml"
paths_documents = ['data/documents/folha94/', 'data/documents/folha95/',
                   'data/documents/publico94/', 'data/documents/publico95/']

# path_questions = "data/questions_test.xml"
# path_questions = "data/questions_test_mini.xml"
# paths_documents = ['data/documents/test/']


# Verifica se os dados já estão indexados, se não estiverem é feito a indexação
def run_mananger(): pass


# Abre o arquivo dataset e retorna uma lista de perguntas em formato tree
def dataset():
    file = open(path_questions, 'r')
    tree = et.parse(file)
    return tree.getroot()


# Retorna todos os pares em um lista
def pairs():
    _, _, ret = valid_invalid_pairs()
    return ret


# Retorna todas os pares do dataset que tem ao menos uma resposta válida,
# também, é retornado os pares inválidos
# Válido significa: o par contém resposta e a resposta tem um docid de origem válida (FolhaSP ou Público)
def valid_invalid_pairs():
    ret = []  # Valid
    ret2 = []  # Invalid
    ret3 = []  # All
    pairs = dataset()

    tot = 0
    for pair in pairs:
        tot += 1
        pair = tree_to_pair(pair)

        if pair.question is None or pair.question.strip() == '':
            continue
        else:
            valid_answers = []
            valid_docid = []
            for i in range(len(pair.correct_answers)):
                answer = pair.correct_answers[i]
                docid = pair.correct_docs_id[i]
                new_docid = validate_docid(docid)
                if new_docid is not None:
                    valid_docid.append(new_docid)
                    valid_answers.append(answer)
            pair.correct_answers = valid_answers
            pair.correct_docs_id = valid_docid
            if len(pair.correct_answers) > 0:
                ret.append(pair)
            else:
                ret2.append(pair)
        ret3.append(pair)
    # print 'Total Questions:\t'+str(len(pairs))
    # print 'Valid Questions:\t'+str(len(ret))
    print 'Total:',tot
    print 'valid:',len(ret),'invalid:',len(ret2)
    return ret, ret2, ret3


# Se é um docid válido(FolhaSP ou Público) então retorna um docid no
# formato do docid dos documentos se não retorna None
def validate_docid(docid):
    global aux
    if docid is None or len(docid.strip()) < 10:
        return None
    else:
        docid = docid.strip()
        r = re.match(r'(?P<n1>.+)(?P<n2>\d{6,8})-(?P<n3>\d{1,3}$)', docid)
        if r is not None:
            if r.groupdict()['n1'][:1] == 'F':
                return 'FSP'+r.groupdict()['n2']+'-'+r.groupdict()['n3']
            else:
                return 'PUBLICO-19'+r.groupdict()['n2']+'-'+r.groupdict()['n3']
        else:
            return None


# Passa a pergunta em formato tree para um objeto do tipo Question
def tree_to_pair(tree_question):
    p = qa_system.Pair()

    if 'categoria' in tree_question.attrib:
        p.question_category = tree_question.attrib['categoria']
    if 'tipo' in tree_question.attrib:
        p.question_type = tree_question.attrib['tipo']
    if u'restrição' in tree_question.attrib:
        p.question_restriction = tree_question.attrib[u'restrição']

    p.correct_classification = pair_classification(p)

    for t in tree_question:
        if t.tag == 'texto':
            if t.text is not None:
                if type(t.text) == type(''): 
                    p.question = t.text.decode('utf-8')
                else:
                    p.question = t.text
        elif t.tag == 'resposta':
            docid = None
            if 'docid' in t.attrib:
                docid = t.attrib['docid']
            if t.text is not None and not t.text.strip() == '':
                p.correct_answers.append(t.text.encode('utf-8'))
                p.correct_docs_id.append(docid)
        elif t.tag == 'extracto':
            if t.text is not None:
                p.extractos.append(t.text)
    return p


# Retorna a classificação da questão com base em sua categoria e tipo
def pair_classification(pair):
    t = pair.question_type
    c = pair.question_category
    if c == 'COUNT':
        return 'MEASURE'
    if c == 'D' or c == 'DEFINITION':
        return 'DEFINITION'
    if c == 'F' or c == 'FACTOID':
        if t == 'COUNT':
            return 'MEASURE'
        else:
            return t
    if c == 'L' or c == 'LIST':
        if t == 'COUNT':
            return 'MEASURE'
        else:
            return t
    if c == 'LOCATION':
        return 'LOCATION'
    if c == 'MEASURE':
        return 'MEASURE'
    if c == 'OBJECT':
        return 'DEFINITION'
    if c == 'ORGANIZATION':
        return 'ORGANIZATION'
    if c == 'OTHER' and (t == 'FACTOID' or t == 'LIST'):
        return 'OTHER'
    if c == 'OTHER' and not (t == 'FACTOID' or t == 'LIST'):
        return t
    if c == 'PERSON' and t == 'DEFINITION':
        return 'DEFINITION'
    if c == 'PERSON' and not t == 'DEFINITION':
        return 'PERSON'
    if c == 'TIME':
        return 'TIME'
    return c


def treat(text):
    if text is None:
        return None
    ret = text.replace('?', '').replace(u'«', '\"').replace(u'»', '\"')
    return ret
