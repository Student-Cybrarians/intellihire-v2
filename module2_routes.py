from flask import Blueprint, jsonify, request
from module2_engine import QUESTION_BANK, evaluate_answer, score_assessment, select_next

module2 = Blueprint('module2', __name__, url_prefix='/api/module2')

@module2.get('/questions')
def questions():
    section = request.args.get('section')
    items = [q for q in QUESTION_BANK if not section or q.section == section]
    return jsonify({'questions': [q.__dict__ | {'answer': None} for q in items]})

@module2.post('/next')
def next_question():
    data = request.get_json(silent=True) or {}
    q = select_next(float(data.get('ability', 0)), data.get('answered', []), data.get('section'))
    return jsonify({'question': q.__dict__ | {'answer': None}} if q else {'question': None})

@module2.post('/answer')
def answer():
    data = request.get_json(silent=True) or {}
    qid = data.get('question_id')
    q = next((x for x in QUESTION_BANK if x.id == qid), None)
    if not q:
        return jsonify({'error': 'question_not_found'}), 404
    return jsonify(evaluate_answer(float(data.get('ability', 0)), q, int(data.get('answer', -1))))

@module2.post('/score')
def score():
    return jsonify(score_assessment((request.get_json(silent=True) or {}).get('events', [])))
