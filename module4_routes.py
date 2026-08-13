from flask import Blueprint, jsonify, request
from module4_hr import start_interview, next_question, submit_answer, finish_interview

module4=Blueprint('module4',__name__,url_prefix='/api/module4')
SESSIONS={}

def _session():
    sid=(request.get_json(silent=True) or {}).get('session_id') or request.args.get('session_id')
    return sid, SESSIONS.get(sid)

@module4.post('/start')
def start():
    data=request.get_json(silent=True) or {}; state=start_interview(data.get('role','Software Engineer'),int(data.get('duration',15))); SESSIONS[state['id']]=state
    return jsonify({'session':state,'question':next_question(state)}),201

@module4.get('/question')
def question():
    sid,state=_session()
    if not state:return jsonify({'error':'session_not_found'}),404
    return jsonify({'question':next_question(state)})

@module4.post('/answer')
def answer():
    sid,state=_session()
    if not state:return jsonify({'error':'session_not_found'}),404
    data=request.get_json(silent=True) or {}; text=str(data.get('answer','')).strip()
    if not text:return jsonify({'error':'answer_required'}),422
    return jsonify({'event':submit_answer(state,text),'next':next_question(state)})

@module4.post('/finish')
def finish():
    sid,state=_session()
    if not state:return jsonify({'error':'session_not_found'}),404
    return jsonify(finish_interview(state))

@module4.get('/history')
def history():
    return jsonify({'interviews':[{'id':s['id'],'role':s['role'],'status':s['status'],'created_at':s['created_at'],'questions':len(s['events'])} for s in SESSIONS.values()]})
