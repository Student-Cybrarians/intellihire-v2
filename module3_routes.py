from flask import Blueprint, jsonify, request
import re, uuid
from auth_routes import require_auth
from auth_db import record_performance

module3 = Blueprint('module3', __name__, url_prefix='/api/module3')
SESSIONS = {}
QUESTIONS = [
    {'id':'tech-01','difficulty':'medium','topic':'Python','prompt':'Explain how you would design a scalable Python API and handle slow dependencies.'},
    {'id':'tech-02','difficulty':'hard','topic':'Algorithms','prompt':'Given a list of integers, explain an O(n) approach to finding the first duplicate.'},
    {'id':'tech-03','difficulty':'hard','topic':'System Design','prompt':'Design a URL shortener and describe storage, caching, scaling, and failure handling.'},
]

def score_answer(text):
    words=re.findall(r'[A-Za-z0-9_]+', text.lower()); n=len(words)
    concepts=['complexity','cache','database','api','test','error','scale','index','queue','tradeoff','validation','security']
    hits=sum(c in text.lower() for c in concepts)
    quality=min(100, round(45 + min(35,n/3) + hits*3))
    return {'score':quality,'accuracy':quality,'communication':min(100,50+n*2),'concept_hits':hits}

def _auth():
    user,response=require_auth('USER')
    return user,response

@module3.post('/start')
def start():
    user,response=_auth()
    if response:return response
    sid='tech-'+uuid.uuid4().hex[:12]
    state={'id':sid,'user_id':user['id'],'role':(request.get_json(silent=True) or {}).get('role','Software Engineer'),'index':0,'events':[]}
    SESSIONS[sid]=state
    return jsonify({'session':state,'question':QUESTIONS[0]}),201

@module3.get('/question')
def question():
    user,response=_auth()
    if response:return response
    sid=request.args.get('session_id'); s=SESSIONS.get(sid)
    if not s or s.get('user_id')!=user['id']:return jsonify({'error':'session_not_found'}),404
    q=QUESTIONS[s['index']] if s['index']<len(QUESTIONS) else None
    return jsonify({'question':q,'progress':s['index'],'total':len(QUESTIONS)})

@module3.post('/answer')
def answer():
    user,response=_auth()
    if response:return response
    data=request.get_json(silent=True) or {}; s=SESSIONS.get(data.get('session_id'))
    if not s or s.get('user_id')!=user['id']:return jsonify({'error':'session_not_found'}),404
    text=str(data.get('answer','')).strip()
    if not text:return jsonify({'error':'answer_required'}),422
    if s['index']>=len(QUESTIONS):return jsonify({'error':'interview_complete'}),409
    q=QUESTIONS[s['index']]; result=score_answer(text)
    s['events'].append({'question':q,'answer':text,'evaluation':result}); s['index']+=1
    return jsonify({'evaluation':result,'next':QUESTIONS[s['index']] if s['index']<len(QUESTIONS) else None})

@module3.post('/finish')
def finish():
    user,response=_auth()
    if response:return response
    data=request.get_json(silent=True) or {}; s=SESSIONS.get(data.get('session_id'))
    if not s or s.get('user_id')!=user['id']:return jsonify({'error':'session_not_found'}),404
    scores=[e['evaluation']['score'] for e in s['events']]
    score=round(sum(scores)/len(scores),1) if scores else 0
    result={'score':score,'questions_answered':len(scores),'events':s['events']}
    try: record_performance(user['id'],'module3',score,result)
    except Exception: pass
    return jsonify(result)
