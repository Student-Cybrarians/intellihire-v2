from flask import Blueprint, jsonify, request
from module5_engine import evaluate
from auth_routes import require_auth
from auth_db import get_user_performance, record_performance
from career_intelligence import build_career_twin, build_roadmap
from career_twin_store import save as save_career_twin, latest as latest_career_twin
from research_engine import build_research_brief
from research_retrieval import run_research
from research_store import save as save_research_brief, latest as latest_research_briefs

module5 = Blueprint('module5', __name__, url_prefix='/api/module5')

@module5.post('/evaluate')
def evaluate_route():
    user, response = require_auth('USER')
    if response: return response
    performance=get_user_performance(user['id'])
    scores={f'Module {i}': (performance[f'module{i}']['score'] if performance[f'module{i}'] else 0) for i in range(1,5)}
    result=evaluate(scores)
    try: record_performance(user['id'],'module5',result.get('score',result.get('readiness',0)),result)
    except Exception: pass
    return jsonify(result)

@module5.get('/summary')
def summary():
    user, response = require_auth('USER')
    if response: return response
    performance=get_user_performance(user['id'])
    scores={f'Module {i}': (performance[f'module{i}']['score'] if performance[f'module{i}'] else 0) for i in range(1,5)}
    return jsonify(evaluate(scores))

@module5.post('/career-twin')
def career_twin():
    user, response = require_auth('USER')
    if response: return response
    data=request.get_json(silent=True) or {}
    resume=str(data.get('resume','')); jd=str(data.get('job_description',data.get('jd',''))); role=str(data.get('role',''))
    if not resume.strip() or not jd.strip(): return jsonify({'error':'resume_and_job_description_required'}),400
    try:
        twin=build_career_twin(resume,jd,role); twin['roadmap']=build_roadmap(twin,data.get('weeks',8))
        twin['persistence']=save_career_twin(user['id'],twin,resume,jd)
        return jsonify(twin)
    except Exception: return jsonify({'error':'career_twin_persistence_unavailable'}),503

@module5.get('/career-twin')
def get_career_twin():
    user, response = require_auth('USER')
    if response: return response
    try: twin=latest_career_twin(user['id'])
    except Exception: return jsonify({'error':'career_twin_persistence_unavailable'}),503
    if not twin: return jsonify({'error':'career_twin_not_found'}),404
    return jsonify(twin)

@module5.post('/research')
def research():
    user, response = require_auth('USER')
    if response: return response
    data=request.get_json(silent=True) or {}; question=str(data.get('question','')).strip()
    if not question: return jsonify({'error':'research_question_required'}),400
    try:
        twin=latest_career_twin(user['id']) or {}
        brief=run_research(twin,question,data.get('sources'),data.get('max_sources',6))
        brief['persistence']=save_research_brief(user['id'],question,brief)
        return jsonify(brief)
    except ValueError as exc: return jsonify({'error':str(exc)}),400
    except Exception: return jsonify({'error':'research_service_unavailable'}),503

@module5.get('/research')
def research_history():
    user, response = require_auth('USER')
    if response: return response
    try: return jsonify({'items':latest_research_briefs(user['id'],request.args.get('limit',10))})
    except Exception: return jsonify({'error':'research_persistence_unavailable'}),503
