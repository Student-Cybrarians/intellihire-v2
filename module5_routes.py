from flask import Blueprint, jsonify, request
from module5_engine import evaluate
from auth_routes import require_auth
from auth_db import get_user_performance, record_performance
from career_intelligence import build_career_twin, build_roadmap
from career_twin_store import save as save_career_twin, latest as latest_career_twin
from module4_competency_store import get_competencies
from research_retrieval import run_research
from research_store import save as save_research_brief, latest as latest_research_briefs
from roadmap_engine import generate_roadmap
from roadmap_store import save as save_roadmap, latest as latest_roadmap

module5 = Blueprint('module5', __name__, url_prefix='/api/module5')

def _behavioral(user_id):
    try:
        return get_competencies(user_id) or {}
    except Exception:
        return {}

def _with_behavioral(result, behavioral):
    result['behavioral_competencies'] = behavioral
    result['integrity'] = {'employment_decision_support_only': True, 'autonomous_hiring_decision': False}
    return result

@module5.post('/evaluate')
def evaluate_route():
    user, response = require_auth('USER')
    if response: return response
    performance=get_user_performance(user['id'])
    scores={f'Module {i}': (performance[f'module{i}']['score'] if performance[f'module{i}'] else 0) for i in range(1,5)}
    result=_with_behavioral(evaluate(scores),_behavioral(user['id']))
    try: record_performance(user['id'],'module5',result.get('score',result.get('readiness',result.get('weighted_score',0))),result)
    except Exception: pass
    return jsonify(result)

@module5.get('/summary')
def summary():
    user, response = require_auth('USER')
    if response: return response
    performance=get_user_performance(user['id'])
    scores={f'Module {i}': (performance[f'module{i}']['score'] if performance[f'module{i}'] else 0) for i in range(1,5)}
    return jsonify(_with_behavioral(evaluate(scores),_behavioral(user['id'])))

@module5.post('/career-twin')
def career_twin():
    user, response = require_auth('USER')
    if response: return response
    data=request.get_json(silent=True) or {}
    resume=str(data.get('resume','')); jd=str(data.get('job_description',data.get('jd',''))); role=str(data.get('role',''))
    if not resume.strip() or not jd.strip(): return jsonify({'error':'resume_and_job_description_required'}),400
    try:
        twin=build_career_twin(resume,jd,role)
        behavioral=_behavioral(user['id'])
        twin['behavioral_competencies']=behavioral
        twin['roadmap']=build_roadmap(twin,data.get('weeks',8))
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
        twin['behavioral_competencies']=_behavioral(user['id'])
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

@module5.post('/roadmap')
def roadmap():
    user, response = require_auth('USER')
    if response: return response
    data=request.get_json(silent=True) or {}
    try:
        twin=latest_career_twin(user['id'])
        if not twin: return jsonify({'error':'career_twin_not_found'}),404
        twin['behavioral_competencies']=_behavioral(user['id'])
        research=data.get('research')
        if research is None:
            history=latest_research_briefs(user['id'],1)
            research=history[0] if history else {}
        plan=generate_roadmap(twin,research,data.get('weeks',8))
        plan['behavioral_competencies']=twin['behavioral_competencies']
        plan['persistence']=save_roadmap(user['id'],plan)
        return jsonify(plan)
    except ValueError as exc: return jsonify({'error':str(exc)}),400
    except Exception: return jsonify({'error':'roadmap_service_unavailable'}),503

@module5.get('/roadmap')
def get_roadmap():
    user, response = require_auth('USER')
    if response: return response
    try:
        plan=latest_roadmap(user['id'])
        if not plan: return jsonify({'error':'roadmap_not_found'}),404
        return jsonify(plan)
    except Exception: return jsonify({'error':'roadmap_persistence_unavailable'}),503
