from flask import Blueprint, jsonify, request
from module4_liftoff import start, question, answer, finish
from module4_liftoff import model_feedback
import os

module4 = Blueprint('module4', __name__, url_prefix='/api/module4')
SESSIONS = {}

def _get_session():
    payload = request.get_json(silent=True) or {}
    sid = payload.get('session_id') or request.args.get('session_id')
    return sid, SESSIONS.get(sid)

@module4.post('/start')
def start_route():
    data = request.get_json(silent=True) or {}
    state = start(data.get('role', 'Software Engineer'), data.get('interviewer', 'AI HR Manager'), int(data.get('duration', 15)))
    SESSIONS[state['id']] = state
    return jsonify({'session': state, 'question': question(state)}), 201

@module4.get('/question')
def question_route():
    sid, state = _get_session()
    if not state:
        return jsonify({'error': 'session_not_found'}), 404
    return jsonify({'question': question(state), 'question_number': state.get('question_index', 0) + 1})

@module4.post('/answer')
def answer_route():
    sid, state = _get_session()
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
    sid, state = _get_session()
    if not state:
        return jsonify({'error': 'session_not_found'}), 404
    return jsonify(finish(state))

@module4.get('/report/<session_id>')
def report(session_id):
    state = SESSIONS.get(session_id)
    if not state:
        return jsonify({'error': 'session_not_found'}), 404
    return jsonify(finish(state))

@module4.get('/history')
def history():
    return jsonify({'interviews': [{'id': s['id'], 'role': s['role'], 'status': s['status'], 'created_at': s['created_at'], 'questions': len(s.get('events', []))} for s in SESSIONS.values()]})

@module4.post('/transcribe')
def transcribe():
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
