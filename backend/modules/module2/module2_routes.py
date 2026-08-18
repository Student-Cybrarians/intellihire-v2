from flask import Blueprint, jsonify, request
from backend.modules.module2.module2_engine import QUESTION_BANK, evaluate_answer, score_assessment, select_next
from backend.auth.auth_routes import require_auth
from backend.auth.auth_db import record_performance
from backend.modules.module2.module2_store import create_assessment, get_assessment, latest_assessment, save_answer, abandon_assessment

module2 = Blueprint('module2', __name__, url_prefix='/api/module2')


def _public_question(question):
    if not question:
        return None
    data = question.__dict__.copy()
    data['answer'] = None
    return data


def _parse_answer(data):
    if not isinstance(data, dict) or 'answer' not in data:
        raise ValueError('invalid_answer')
    try:
        return int(data['answer'])
    except (TypeError, ValueError):
        raise ValueError('invalid_answer')


@module2.get('/questions')
def questions():
    user, response = require_auth('USER')
    if response:
        return response
    section = request.args.get('section')
    items = [q for q in QUESTION_BANK if not section or q.section == section]
    return jsonify({'questions': [_public_question(q) for q in items]})


@module2.post('/next')
def next_question():
    user, response = require_auth('USER')
    if response:
        return response
    data = request.get_json(silent=True) or {}
    try:
        ability = float(data.get('ability', 0))
    except (TypeError, ValueError):
        return jsonify({'error': 'invalid_ability'}), 400
    answered = data.get('answered', [])
    if not isinstance(answered, list) or not all(isinstance(item, str) for item in answered):
        return jsonify({'error': 'invalid_answered'}), 400
    q = select_next(ability, answered, data.get('section'))
    return jsonify({'question': _public_question(q)})


@module2.post('/answer')
def answer():
    user, response = require_auth('USER')
    if response:
        return response
    data = request.get_json(silent=True) or {}
    qid = data.get('question_id')
    q = next((x for x in QUESTION_BANK if x.id == qid), None)
    if not q:
        return jsonify({'error': 'question_not_found'}), 404
    try:
        ability = float(data.get('ability', 0))
        answer_index = _parse_answer(data)
    except (TypeError, ValueError):
        return jsonify({'error': 'invalid_answer_request'}), 400
    event = evaluate_answer(ability, q, answer_index)
    event['question'] = _public_question(q)
    return jsonify(event)


@module2.post('/score')
def score():
    user, response = require_auth('USER')
    if response:
        return response
    data = request.get_json(silent=True) or {}
    events = data.get('events', [])
    if not isinstance(events, list):
        return jsonify({'error': 'invalid_events'}), 400
    return jsonify(score_assessment(events))


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


@module2.get('/assessments/<assessment_id>/next')
def persisted_next(assessment_id):
    user, response = require_auth('USER')
    if response:
        return response
    try:
        assessment = get_assessment(user['id'], assessment_id)
        if not assessment:
            return jsonify({'error': 'assessment_not_found'}), 404
        if assessment['status'] != 'ACTIVE':
            return jsonify({'error': 'assessment_not_active', 'assessment': assessment}), 409
        question = select_next(assessment['ability'], assessment['answered_ids'], assessment['section'] or None)
        return jsonify({'question': _public_question(question), 'assessment': assessment})
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
        answer_index = _parse_answer(data)
        current = get_assessment(user['id'], assessment_id)
        if not current:
            return jsonify({'error': 'assessment_not_found'}), 404
        if current['status'] != 'ACTIVE':
            return jsonify({'error': 'assessment_not_active'}), 409
        event = evaluate_answer(current['ability'], q, answer_index)
        saved = save_answer(user['id'], assessment_id, event)
        result = score_assessment(saved['events'])
        if saved['status'] == 'COMPLETED':
            try:
                record_performance(user['id'], 'module2', result.get('score', 0), result)
            except Exception:
                pass
        public_event = dict(event)
        public_event['question'] = _public_question(q)
        return jsonify({'event': public_event, 'assessment': saved, 'result': result})
    except ValueError as exc:
        if str(exc) == 'invalid_answer':
            return jsonify({'error': 'invalid_answer_request'}), 400
        if str(exc) in {'assessment_not_active', 'question_already_answered'}:
            return jsonify({'error': str(exc)}), 409
        return jsonify({'error': 'invalid_assessment_request'}), 400
    except LookupError:
        return jsonify({'error': 'assessment_not_found'}), 404
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
    except (ValueError, TypeError):
        return jsonify({'error': 'assessment_not_found'}), 404
    except Exception:
        return jsonify({'error': 'assessment_storage_unavailable'}), 503
