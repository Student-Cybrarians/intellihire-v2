from flask import Blueprint, jsonify, request
import re
from auth_routes import require_auth
from auth_db import record_performance
from module3_store import init_module3_db, create_session, get_session, save_session, latest_session

module3 = Blueprint('module3', __name__, url_prefix='/api/module3')
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

def _auth(): return require_auth('USER')

def _safe_init():
    try: init_module3_db(); return None
    except Exception: return jsonify({'error':'service_unavailable'}),503

def _load(sid,user_id):
    try: return get_session(sid,user_id)
    except Exception: return None

@module3.post('/start')
def start():
    user,response=_auth()
    if response:return response
    data=request.get_json(silent=True) or {}
    role=str(data.get('role','Software Engineer')).strip()[:120]
    if not role:return jsonify({'error':'role_required'}),422
    init=_safe_init()
    if init:return init
    state={'index':0,'events':[],'total':len(QUESTIONS)}
    try: sid=create_session(user['id'],role,state)
    except Exception:return jsonify({'error':'service_unavailable'}),503
    return jsonify({'session':{'id':sid,'role':role,'progress':0,'total':len(QUESTIONS)},'question':QUESTIONS[0]}),201

@module3.get('/resume')
def resume():
    user,response=_auth()
    if response:return response
    try: init_module3_db(); s=latest_session(user['id'])
    except Exception:return jsonify({'error':'service_unavailable'}),503
    if not s:return jsonify({'error':'session_not_found'}),404
    q=QUESTIONS[s['index']] if s['index']<len(QUESTIONS) else None
    return jsonify({'session':{'id':s['id'],'role':s['role'],'progress':s['index'],'total':len(QUESTIONS),'completed':bool(s.get('completed_at'))},'question':q})

@module3.get('/question')
def question():
    user,response=_auth()
    if response:return response
    sid=request.args.get('session_id'); s=_load(sid,user['id'])
    if not s:return jsonify({'error':'session_not_found'}),404
    if s.get('completed_at'):return jsonify({'error':'interview_complete'}),409
    q=QUESTIONS[s['index']] if s['index']<len(QUESTIONS) else None
    return jsonify({'question':q,'progress':s['index'],'total':len(QUESTIONS)})

@module3.post('/answer')
def answer():
    user,response=_auth()
    if response:return response
    data=request.get_json(silent=True) or {}; sid=data.get('session_id'); s=_load(sid,user['id'])
    if not s:return jsonify({'error':'session_not_found'}),404
    if s.get('completed_at'):return jsonify({'error':'interview_complete'}),409
    text=str(data.get('answer','')).strip()
    if not text:return jsonify({'error':'answer_required'}),422
    if len(text)>12000:return jsonify({'error':'answer_too_long'}),413
    if s['index']>=len(QUESTIONS):return jsonify({'error':'interview_complete'}),409
    q=QUESTIONS[s['index']]; result=score_answer(text)
    s['events'].append({'question_id':q['id'],'answer':text,'evaluation':result}); s['index']+=1
    try: save_session(sid,user['id'],s)
    except Exception:return jsonify({'error':'service_unavailable'}),503
    return jsonify({'evaluation':result,'next':QUESTIONS[s['index']] if s['index']<len(QUESTIONS) else None,'progress':s['index'],'total':len(QUESTIONS)})

@module3.post('/finish')
def finish():
    user,response=_auth()
    if response:return response
    data=request.get_json(silent=True) or {}; sid=data.get('session_id'); s=_load(sid,user['id'])
    if not s:return jsonify({'error':'session_not_found'}),404
    if s.get('completed_at'):
        scores=[e['evaluation']['score'] for e in s['events']]; score=round(sum(scores)/len(scores),1) if scores else 0
        return jsonify({'score':score,'questions_answered':len(scores),'completed':True})
    if s['index']<len(QUESTIONS):return jsonify({'error':'interview_incomplete','remaining':len(QUESTIONS)-s['index']}),409
    scores=[e['evaluation']['score'] for e in s['events']]; score=round(sum(scores)/len(scores),1) if scores else 0
    result={'score':score,'questions_answered':len(scores),'events':s['events']}
    try:
        save_session(sid,user['id'],s,completed=True)
        record_performance(user['id'],'module3',score,result)
    except Exception:return jsonify({'error':'service_unavailable'}),503
    return jsonify({**result,'completed':True})
