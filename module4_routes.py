from flask import Blueprint, jsonify, request
from module4_liftoff import start, question, answer, finish
from module5_engine import evaluate as evaluate_module5
from auth_routes import require_auth
from auth_db import record_performance
import os

module4 = Blueprint('module4', __name__, url_prefix='/api/module4')
SESSIONS = {}

def _auth_user():
    return require_auth('USER')

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
    if response:return response
    data = request.get_json(silent=True) or {}
    state = start(data.get('role', 'Software Engineer'), data.get('interviewer', 'AI HR Manager'), int(data.get('duration', 15)))
    state['user_id'] = user['id']; SESSIONS[state['id']] = state
    return jsonify({'session': state, 'question': question(state)}), 201

@module4.get('/question')
def question_route():
    user, response = _auth_user()
    if response:return response
    sid, _ = _get_session(); state = _owned_session(sid, user)
    if not state:return jsonify({'error':'session_not_found'}),404
    return jsonify({'question': question(state), 'question_number': state.get('question_index', 0)+1})

@module4.post('/answer')
def answer_route():
    user, response = _auth_user()
    if response:return response
    sid, _ = _get_session(); state = _owned_session(sid, user)
    if not state:return jsonify({'error':'session_not_found'}),404
    data=request.get_json(silent=True) or {}; text=str(data.get('answer',data.get('transcript',''))).strip()
    if not text:return jsonify({'error':'answer_required'}),422
    event=answer(state,text)
    if event is None:return jsonify({'error':'interview_complete'}),409
    return jsonify({'event':event,'next':question(state),'question_number':state.get('question_index',0)+1})

@module4.post('/finish')
def finish_route():
    user, response = _auth_user()
    if response:return response
    sid, _ = _get_session(); state = _owned_session(sid, user)
    if not state:return jsonify({'error':'session_not_found'}),404
    result=finish(state)
    try: record_performance(user['id'],'module4',result.get('score',0),result)
    except Exception: pass
    return jsonify(result)

@module4.get('/report/<session_id>')
def report(session_id):
    user, response = _auth_user()
    if response:return response
    state=_owned_session(session_id,user)
    if not state:return jsonify({'error':'session_not_found'}),404
    result=finish(state)
    return jsonify(result)

@module4.get('/history')
def history():
    user, response = _auth_user()
    if response:return response
    return jsonify({'interviews':[{'id':s['id'],'role':s['role'],'status':s['status'],'created_at':s['created_at'],'questions':len(s.get('events',[]))} for s in SESSIONS.values() if s.get('user_id')==user.get('id')]})

@module4.post('/transcribe')
def transcribe():
    user, response = _auth_user()
    if response:return response
    uploaded=request.files.get('file')
    if not uploaded:return jsonify({'error':'audio_file_required'}),400
    key=os.getenv('OPENAI_API_KEY')
    if not key:return jsonify({'error':'OPENAI_API_KEY_not_configured'}),503
    try:
        import requests
        r=requests.post('https://api.openai.com/v1/audio/transcriptions',headers={'Authorization':f'Bearer {key}'},files={'file':(uploaded.filename or 'answer.webm',uploaded.stream,uploaded.mimetype or 'audio/webm')},data={'model':os.getenv('INTELLIHIRE_TRANSCRIBE_MODEL','whisper-1')},timeout=90)
        r.raise_for_status();return jsonify({'transcript':r.json().get('text','')})
    except Exception:return jsonify({'error':'transcription_unavailable'}),502

@module4.get('/handoff/<session_id>')
def handoff(session_id):
    user, response = _auth_user()
    if response:return response
    state=_owned_session(session_id,user)
    if not state:return jsonify({'error':'session_not_found'}),404
    report_data=finish(state)
    return jsonify({'module4_report':report_data,'module5':evaluate_module5({'Module 4':report_data.get('score',0)})})
