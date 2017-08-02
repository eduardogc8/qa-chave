import manager_dataset
from terminaltables import AsciiTable

valid, invalid = manager_dataset.valid_invalid_pairs()

pairs = valid + invalid

n = []
for p in pairs:
    if not p.correct_type == 'X':
        n.append(p)
# pairs = n
len(pairs)

types = {}
for i in pairs:
    t = i.correct_type
    if t not in types.keys():
        types[t] = 0
    types[t] += 1
types

classifications = {}
for i in pairs:
    t = i.correct_classification
    if t not in classifications.keys():
        classifications[t] = 0
    classifications[t] += 1
classifications

categorys = {}
for i in pairs:
    t = i.question_category
    if t not in categorys.keys():
        categorys[t] = 0
    categorys[t] += 1
categorys

d = []
for p in pairs:
    if p.correct_classification == 'OBJECT':
        d.append([p.question_category, p.question.replace('\n', '')])

tb = AsciiTable(d)
tb.inner_footing_row_border = False
tb.inner_heading_row_border = False
print tb.table
