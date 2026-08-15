from flask import Blueprint, jsonify, request
import re
from auth_routes import require_auth
from auth_db import record_performance
from module3_store import init_module3_db, create_session, get_session, save_session, latest_session
from module3_evaluator import evaluate_code
from module3_adaptive import initial_state, select_next_question, update_skill_state, record_code_signal

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

def _next(s):
    return select_next_question(QUESTIONS, s)

@module3.post('/start')
def start():
    user,response=_auth()
    if response:return response
    data=request.get_json(silent=True) or {}; role=str(data.get('role','Software Engineer')).strip()[:120]
    if not role:return jsonify({'error':'role_required'}),422
    init=_safe_init()
    if init:return init
    state=initial_state(len(QUESTIONS))
    try: sid=create_session(user['id'],role,state)
    except Exception:return jsonify({'error':'service_unavailable'}),503
    return jsonify({'session':{'id':sid,'role':role,'progress':0,'total':len(QUESTIONS),'ability':state['ability'],'skill_scores':state['skill_scores']},'question':_next(state)}),201

@module3.get('/resume')
def resume():
    user,response=_auth()
    if response:return response
    try: init_module3_db(); s=latest_session(user['id'])
    except Exception:return jsonify({'error':'service_unavailable'}),503
    if not s:return jsonify({'error':'session_not_found'}),404
    q=_next(s) if not s.get('completed_at') else None
    return jsonify({'session':{'id':s['id'],'role':s['role'],'progress':len([e for e in s.get('events',[]) if e.get('question_id')]),'total':len(QUESTIONS),'completed':bool(s.get('completed_at')),'ability':s.get('ability',50.0),'skill_scores':s.get('skill_scores',{})},'question':q})

@module3.get('/question')
def question():
    user,response=_auth()
    if response:return response
    sid=request.args.get('session_id'); s=_load(sid,user['id'])
    if not s:return jsonify({'error':'session_not_found'}),404
    if s.get('completed_at'):return jsonify({'error':'interview_complete'}),409
    return jsonify({'question':_next(s),'progress':len([e for e in s.get('events',[]) if e.get('question_id')]),'total':len(QUESTIONS),'ability':s.get('ability',50.0),'skill_scores':s.get('skill_scores',{})})

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
    q=_next(s)
    if not q:return jsonify({'error':'interview_complete'}),409
    result=score_answer(text)
    try:
        from ai import get_orchestrator
        from ai.schemas import INTERVIEW_SCHEMA
        ai_result=get_orchestrator().generate_structured(user_id=user['id'],feature='module3_interview',task='Evaluate technical reasoning and explanation quality and propose one follow-up question. Do not override deterministic code results.',context={'question':q,'answer':text[:12000],'deterministic_evaluation':result},schema=INTERVIEW_SCHEMA,reasoning=True,max_tokens=900,retries=0)
        result['ai_feedback']=ai_result['data']
    except Exception:
        result['ai_feedback']={'status':'unavailable','message':'AI analysis is temporarily unavailable.'}
    s['events'].append({'question_id':q['id'],'answer':text,'evaluation':result})
    update_skill_state(s,q,result)
    try: save_session(sid,user['id'],s)
    except Exception:return jsonify({'error':'service_unavailable'}),503
    return jsonify({'evaluation':result,'next':_next(s),'progress':len([e for e in s['events'] if e.get('question_id')]),'total':len(QUESTIONS),'ability':s['ability'],'skill_scores':s['skill_scores']})

@module3.post('/code/evaluate')
def code_evaluate():
    user,response=_auth()
    if response:return response
    data=request.get_json(silent=True) or {}; sid=data.get('session_id'); s=_load(sid,user['id'])
    if not s:return jsonify({'error':'session_not_found'}),404
    if s.get('completed_at'):return jsonify({'error':'interview_complete'}),409
    data_code=str(data.get('code',''))
    if len(data_code)>16000:return jsonify({'error':'code_too_long'}),413
    try: result=evaluate_code(data_code,data.get('language','python'),data.get('question',''))
    except ValueError:return jsonify({'error':'code_required'}),422
    event={'type':'code_evaluation','language':str(data.get('language','python'))[:32],'evaluation':result}
    s['events'].append(event); record_code_signal(s,result)
    try: save_session(sid,user['id'],s)
    except Exception:return jsonify({'error':'service_unavailable'}),503
    return jsonify({**result,'ability':s['ability'],'skill_scores':s['skill_scores']})

@module3.post('/finish')
def finish():
    user,response=_auth()
    if response:return response
    data=request.get_json(silent=True) or {}; sid=data.get('session_id'); s=_load(sid,user['id'])
    if not s:return jsonify({'error':'session_not_found'}),404
    answered=len([e for e in s.get('events',[]) if e.get('question_id')])
    if s.get('completed_at'):
        scores=[e['evaluation']['score'] for e in s['events'] if 'evaluation' in e]; score=round(sum(scores)/len(scores),1) if scores else 0
        return jsonify({'score':score,'questions_answered':answered,'completed':True,'ability':s.get('ability',50.0),'skill_scores':s.get('skill_scores',{})})
    if answered<len(QUESTIONS):return jsonify({'error':'interview_incomplete','remaining':len(QUESTIONS)-answered}),409
    scores=[e['evaluation']['score'] for e in s['events'] if 'evaluation' in e]; score=round(sum(scores)/len(scores),1) if scores else 0
    result={'score':score,'questions_answered':answered,'events':s['events'],'ability':s.get('ability',50.0),'skill_scores':s.get('skill_scores',{})}
    try:
        save_session(sid,user['id'],s,completed=True); record_performance(user['id'],'module3',score,result)
    except Exception:return jsonify({'error':'service_unavailable'}),503
    return jsonify({**result,'completed':True})
