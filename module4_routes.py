from flask import Blueprint, jsonify, request
from module4_hr import start_interview, next_question, submit_answer, finish_interview
from module4_liftoff import openai_feedback
import os

module4=Blueprint('module4',__name__,url_prefix='/api/module4')
SESSIONS={}

def _session():
    payload=request.get_json(silent=True) or {}
    sid=payload.get('session_id') or request.args.get('session_id')
    return sid, SESSIONS.get(sid)

@module4.post('/start')
def start():
    data=request.get_json(silent=True) or {}
    state=start_interview(data.get('role','Software Engineer'),int(data.get('duration',15)))
    SESSIONS[state['id']]=state
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
    event=submit_answer(state,text)
    ai=openai_feedback(event['question']['prompt'],text)
    if ai:event['metrics']['ai_feedback']=ai
    return jsonify({'event':event,'next':next_question(state)})

@module4.post('/transcribe')
def transcribe():
    uploaded=request.files.get('file')
    if not uploaded:return jsonify({'error':'audio_file_required'}),400
    key=os.getenv('OPENAI_API_KEY')
    if not key:return jsonify({'transcript':'','error':'OPENAI_API_KEY is not configured; use text mode or browser speech transcription.'})
    try:
        import requests
        response=requests.post('https://api.openai.com/v1/audio/transcriptions',headers={'Authorization':f'Bearer {key}'},files={'file':(uploaded.filename or 'answer.webm',uploaded.stream,uploaded.mimetype or 'audio/webm')},data={'model':os.getenv('INTELLIHIRE_TRANSCRIBE_MODEL','whisper-1')},timeout=90)
        response.raise_for_status()
        return jsonify({'transcript':response.json().get('text','')})
    except Exception as exc:
        return jsonify({'transcript':'','error':f'transcription_unavailable: {exc}'}),502

@module4.post('/finish')
def finish():
    sid,state=_session()
    if not state:return jsonify({'error':'session_not_found'}),404
    return jsonify(finish_interview(state))

@module4.get('/history')
def history():
    return jsonify({'interviews':[{'id':s['id'],'role':s['role'],'status':s['status'],'created_at':s['created_at'],'questions':len(s['events'])} for s in SESSIONS.values()]})
