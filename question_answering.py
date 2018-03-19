import question_processing as QP
import information_retrieval as IR
import answer_processing as AP


def run(questions, qc_model, ir, ner_model, show_status=True):
    if show_status: print('Predict Answer Type ...')
    QP.predict_answer_type(qc_model, questions)
    if show_status: print('Answer Candidates ...')
    AP.answer_candidates(questions, ir, ner_model, answer_type_filter=True)
    if show_status: print('Final Answer Selection ...')
    AP.finals_answer(questions)
    if show_status: print('Evaluate Questions ...')
    AP.evaluate_questions(questions)

def correct_answer_rate(questions):
    correct = 0
    for question in questions:
        if question['correct_final_answer']:
            correct += 1
    return correct / len(questions)
