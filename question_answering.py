import question_processing as QP
import answer_processing as AP


def run(questions, qc_model, ir, ner_model, printing=True):
    if printing: print('Predict Answer Type ...')
    QP.predict_answer_type(qc_model, questions)
    if printing: print('Answer Candidates ...')
    AP.answer_candidates(questions, ir, ner_model, answer_type_filter=True, printing=printing)
    if printing: print('Final Answer Selection ...')
    AP.finals_answer(questions, printing=printing)
    if printing: print('Evaluate Questions ...')
    AP.evaluate_questions(questions)


def correct_answer_rate(questions):
    correct = 0
    for question in questions:
        if question['correct_final_answer']:
            correct += 1
    return correct / len(questions)
