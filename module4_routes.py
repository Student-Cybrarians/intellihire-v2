from flask import Blueprint, jsonify, request
from module4_liftoff import start, question, answer, finish
from module5_engine import evaluate as evaluate_module5
from auth_routes import require_auth
import os

module4 = Blueprint('module4', __name__, url_prefix='/api/module4')
SESSIONS = {}

def _auth_user():
    user, response = require_auth('USER')
    return user, response

def _get_session():
    payload = request.get_json(silent=True) or {}
    sid = payload.get('session_id') or request.args.get('session_id')
    return sid, SESSIONS.get(sid)

def _owned_session(sid, user):
    state = SESSIONS.get(sid)
    return state if state and state.get('user_id') == user.get('id') else None

@module4.post('/start')
def start_route():
    user, response = _auth_user()
    if response:
        return response
    data = request.get_json(silent=True) or {}
    state = start(data.get('role', 'Software Engineer'), data.get('interviewer', 'AI HR Manager'), int(data.get('duration', 15)))
    state['user_id'] = user['id']
    SESSIONS[state['id']] = state
    return jsonify({'session': state, 'question': question(state)}), 201

@module4.get('/question')
def question_route():
    user, response = _auth_user()
    if response:
        return response
    sid, _ = _get_session()
    state = _owned_session(sid, user)
    if not state:
        return jsonify({'error': 'session_not_found'}), 404
    return jsonify({'question': question(state), 'question_number': state.get('question_index', 0) + 1})

@module4.post('/answer')
def answer_route():
    user, response = _auth_user()
    if response:
        return response
    sid, _ = _get_session()
    state = _owned_session(sid, user)
    if not state:
        return jsonify({'error': 'session_not_found'}), 404
    data = request.get_json(silent=True) or {}
    text = str(data.get('answer', data.get('transcript', ''))).strip()
    if not text:
        return jsonify({'error': 'answer_required'}), 422
    event = answer(state, text)
    if event is None:
        return jsonify({'error': 'interview_complete'}), 409
    return jsonify({'event': event, 'next': question(state), 'question_number': state.get('question_index', 0) + 1})

@module4.post('/finish')
def finish_route():
    user, response = _auth_user()
    if response:
        return response
    sid, _ = _get_session()
    state = _owned_session(sid, user)
    if not state:
        return jsonify({'error': 'session_not_found'}), 404
    return jsonify(finish(state))

@module4.get('/report/<session_id>')
def report(session_id):
    user, response = _auth_user()
    if response:
        return response
    state = _owned_session(session_id, user)
    if not state:
        return jsonify({'error': 'session_not_found'}), 404
    return jsonify(finish(state))

@module4.get('/history')
def history():
    user, response = _auth_user()
    if response:
        return response
    interviews = [
        {'id': s['id'], 'role': s['role'], 'status': s['status'], 'created_at': s['created_at'], 'questions': len(s.get('events', []))}
        for s in SESSIONS.values() if s.get('user_id') == user.get('id')
    ]
    return jsonify({'interviews': interviews})

@module4.post('/transcribe')
def transcribe():
    user, response = _auth_user()
    if response:
        return response
    uploaded = request.files.get('file')
    if not uploaded:
        return jsonify({'error': 'audio_file_required'}), 400
    key = os.getenv('OPENAI_API_KEY')
    if not key:
        return jsonify({'error': 'OPENAI_API_KEY_not_configured'}), 503
    try:
        import requests
        response = requests.post(
            'https://api.openai.com/v1/audio/transcriptions',
            headers={'Authorization': f'Bearer {key}'},
            files={'file': (uploaded.filename or 'answer.webm', uploaded.stream, uploaded.mimetype or 'audio/webm')},
            data={'model': os.getenv('INTELLIHIRE_TRANSCRIBE_MODEL', 'whisper-1')},
            timeout=90,
        )
        response.raise_for_status()
        return jsonify({'transcript': response.json().get('text', '')})
    except Exception:
        return jsonify({'error': 'transcription_unavailable'}), 502

@module4.get('/handoff/<session_id>')
def handoff(session_id):
    user, response = _auth_user()
    if response:
        return response
    state = _owned_session(session_id, user)
    if not state:
        return jsonify({'error': 'session_not_found'}), 404
    report_data = finish(state)
    scores = {
        'Module 4': report_data.get('score', 0),
        'Module 1': request.args.get('module1', type=float) or 0,
        'Module 2': request.args.get('module2', type=float) or 0,
        'Module 3': request.args.get('module3', type=float) or 0,
        'Module 5': request.args.get('module5', type=float) or 0,
    }
    return jsonify({'module4_report': report_data, 'module5': evaluate_module5(scores)})
