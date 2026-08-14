from flask import Blueprint, jsonify, request
from module2_engine import QUESTION_BANK, evaluate_answer, score_assessment, select_next
from auth_routes import require_auth
from auth_db import record_performance
from module2_store import create_assessment, get_assessment, latest_assessment, save_answer, abandon_assessment

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

@module2.post('/assessments')
def start_assessment():
    user, response = require_auth('USER')
    if response:
        return response
    data = request.get_json(silent=True) or {}
    try:
        assessment = create_assessment(user['id'], data.get('section', ''), data.get('target_questions', 8))
        return jsonify(assessment), 201
    except (TypeError, ValueError):
        return jsonify({'error': 'invalid_assessment_request'}), 400
    except Exception:
        return jsonify({'error': 'assessment_storage_unavailable'}), 503

@module2.get('/assessments/latest')
def latest():
    user, response = require_auth('USER')
    if response:
        return response
    try:
        assessment = latest_assessment(user['id'])
        return jsonify({'assessment': assessment})
    except Exception:
        return jsonify({'error': 'assessment_storage_unavailable'}), 503

@module2.get('/assessments/<assessment_id>')
def get_one(assessment_id):
    user, response = require_auth('USER')
    if response:
        return response
    try:
        assessment = get_assessment(user['id'], assessment_id)
        if not assessment:
            return jsonify({'error': 'assessment_not_found'}), 404
        return jsonify({'assessment': assessment})
    except Exception:
        return jsonify({'error': 'assessment_storage_unavailable'}), 503

@module2.post('/assessments/<assessment_id>/answer')
def answer_persisted(assessment_id):
    user, response = require_auth('USER')
    if response:
        return response
    data = request.get_json(silent=True) or {}
    qid = data.get('question_id')
    q = next((x for x in QUESTION_BANK if x.id == qid), None)
    if not q:
        return jsonify({'error': 'question_not_found'}), 404
    try:
        current = get_assessment(user['id'], assessment_id)
        if not current:
            return jsonify({'error': 'assessment_not_found'}), 404
        event = evaluate_answer(current['ability'], q, int(data.get('answer', -1)))
        saved = save_answer(user['id'], assessment_id, event)
        result = score_assessment(saved['events'])
        if saved['status'] == 'COMPLETED':
            try:
                record_performance(user['id'], 'module2', result.get('score', 0), result)
            except Exception:
                pass
        return jsonify({'event': event, 'assessment': saved, 'result': result})
    except LookupError:
        return jsonify({'error': 'assessment_not_found'}), 404
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 409
    except Exception:
        return jsonify({'error': 'assessment_storage_unavailable'}), 503

@module2.post('/assessments/<assessment_id>/abandon')
def abandon(assessment_id):
    user, response = require_auth('USER')
    if response:
        return response
    try:
        assessment = get_assessment(user['id'], assessment_id)
        if not assessment:
            return jsonify({'error': 'assessment_not_found'}), 404
        return jsonify({'assessment': abandon_assessment(user['id'], assessment_id)})
    except Exception:
        return jsonify({'error': 'assessment_storage_unavailable'}), 503
