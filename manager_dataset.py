# -*- coding: utf-8 -*-
import xml.etree.ElementTree as et
from util import util
import re

path_questions = "data/questions.xml"

# path_questions = "data/questions_test.xml"
# path_questions = "data/questions_test_mini.xml"


# Open questions file and return it tree
def questions_tree():
    tree = et.parse(path_questions)
    return tree.getroot()


# Return a list with all questions in dataset
def questions(treated=False):
    ret = []
    count = 0
    for question in questions_tree():
        q = {}
        q['id'] = count
        q['id_org'] = question.attrib['id_org']
        q['year'] = question.attrib['ano']
        q['category'] = question.attrib['categoria']
        q['type'] = question.attrib['tipo']
        q['class'] = pair_classification(q['category'], q['type'])
        q['predict_class'] = ''
        q['ling'] = question.attrib['ling_orig']
        if u'restrição' in question.attrib:
            q['restriction'] = question.attrib[u'restrição']
        if 'restricao' in question.attrib:
            q['restriction'] = question.attrib['restricao']
        if q['restriction'] == 'NO': q['restriction'] = 'NONE'
        if q['restriction'] == 'X': q['restriction'] = ''

        q['answers'] = []
        q['extracts'] = []

        for e in question:
            if e.tag == 'texto':
                q['question'] = e.text
            if e.tag == 'resposta':
                ans = {'answer':e.text, 'n':e.attrib['n'], 'doc':e.attrib['docid']}
                ans['doc'] = validate_docid(ans['doc'])
                q['answers'].append(ans)
            if e.tag == 'extracto':
                q['extracts'].append({'extract':e.text, 'n':e.attrib['n'], 'answer_n':e.attrib['resposta_n']})
        count += 1
        ret.append(q)
    if treated:
        ret = treat_questions_text(ret)
        ret = select_questions_by_text(ret)
    return ret


# Question text is treated
def treat_questions_text(questions):
    for question in questions:
        if question['question'] is None:
            question['question'] = ''
        question['question'] = util.treat_text(question['question'])
    return questions


# Return questions with some text
def select_questions_by_text(questions):
    ret = []
    for question in questions:
        if len(question['question']) > 0:
            ret.append(question)
    return ret


# Split question in train and test
# The questions that has an answer will be used for test while another questions will be used for train
def split_questions(questions):
    train_questions = []
    test_questions = []
    for question in questions:
        if len(question['answers']) > 0:
            test_questions.append(question)
        else:
            train_questions.append(question)
    return train_questions, test_questions


# Check if a docid is valid (FolhaSP or Público) so return a docid in the
# documents docid else return None
def validate_docid(docid):
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


# Return the right question class based in category and type attributes
def pair_classification(c, t):
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
