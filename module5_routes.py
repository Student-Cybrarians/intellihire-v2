from flask import Blueprint, jsonify, request
from module5_engine import evaluate
from module5_readiness import build_readiness
from readiness_store import save as save_readiness, latest as latest_readiness
from auth_routes import require_auth
from auth_db import get_user_performance, record_performance
from career_intelligence import build_career_twin, build_roadmap
from career_twin_store import save as save_career_twin, latest as latest_career_twin
from skill_graph_store import save as save_skill_graph, latest as latest_skill_graph
from module4_competency_store import get_competencies
from research_retrieval import run_research
from research_store import save as save_research_brief, latest as latest_research_briefs
from roadmap_engine import generate_roadmap
from roadmap_store import save as save_roadmap, latest as latest_roadmap

module5 = Blueprint('module5', __name__, url_prefix='/api/module5')

def _behavioral(user_id):
    try: return get_competencies(user_id) or {}
    except Exception: return {}

def _readiness_inputs(user_id):
    performance=get_user_performance(user_id)
    twin=latest_career_twin(user_id) or {}
    behavioral=_behavioral(user_id)
    research_items=latest_research_briefs(user_id,1)
    research=research_items[0] if research_items else {}
    roadmap=latest_roadmap(user_id) or {}
    return performance,twin,research,roadmap,behavioral

@module5.post('/evaluate')
def evaluate_route():
    user, response = require_auth('USER')
    if response: return response
    try:
        performance,twin,research,roadmap,behavioral=_readiness_inputs(user['id'])
        result=build_readiness(performance,twin,research,roadmap,behavioral)
        result['persistence']=save_readiness(user['id'],result)
        record_performance(user['id'],'module5',result['weighted_score'],result)
        return jsonify(result)
    except Exception: return jsonify({'error':'readiness_service_unavailable'}),503

@module5.get('/summary')
def summary():
    user, response = require_auth('USER')
    if response: return response
    try:
        result=latest_readiness(user['id'])
        if not result:
            performance,twin,research,roadmap,behavioral=_readiness_inputs(user['id'])
            result=build_readiness(performance,twin,research,roadmap,behavioral)
        return jsonify(result)
    except Exception: return jsonify({'error':'readiness_service_unavailable'}),503

@module5.post('/career-twin')
def career_twin():
    user,response=require_auth('USER')
    if response:return response
    data=request.get_json(silent=True) or {}; resume=str(data.get('resume','')); jd=str(data.get('job_description',data.get('jd',''))); role=str(data.get('role',''))
    if not resume.strip() or not jd.strip():return jsonify({'error':'resume_and_job_description_required'}),400
    try:
        twin=build_career_twin(resume,jd,role)
        twin['behavioral_competencies']=_behavioral(user['id'])
        twin['roadmap']=build_roadmap(twin,data.get('weeks',8))
        twin['persistence']=save_career_twin(user['id'],twin,resume,jd)
        twin['skill_graph_persistence']=save_skill_graph(user['id'],twin)
        twin['skill_graph']=twin['skill_graph_persistence']['graph']
        return jsonify(twin)
    except Exception:return jsonify({'error':'career_twin_persistence_unavailable'}),503

@module5.get('/career-twin')
def get_career_twin():
    user,response=require_auth('USER')
    if response:return response
    try:twin=latest_career_twin(user['id'])
    except Exception:return jsonify({'error':'career_twin_persistence_unavailable'}),503
    if not twin:return jsonify({'error':'career_twin_not_found'}),404
    try:
        graph=latest_skill_graph(user['id'])
        if graph:twin['skill_graph']=graph
    except Exception:
        return jsonify({'error':'career_twin_skill_graph_unavailable'}),503
    return jsonify(twin)

@module5.get('/career-twin/skill-graph')
def get_skill_graph():
    user,response=require_auth('USER')
    if response:return response
    try: graph=latest_skill_graph(user['id'])
    except Exception:return jsonify({'error':'skill_graph_persistence_unavailable'}),503
    if not graph:return jsonify({'error':'skill_graph_not_found'}),404
    return jsonify(graph)

@module5.post('/research')
def research():
    user,response=require_auth('USER')
    if response:return response
    data=request.get_json(silent=True) or {}; question=str(data.get('question','')).strip()
    if not question:return jsonify({'error':'research_question_required'}),400
    try:
        twin=latest_career_twin(user['id']) or {}; twin['behavioral_competencies']=_behavioral(user['id']); brief=run_research(twin,question,data.get('sources'),data.get('max_sources',6)); brief['persistence']=save_research_brief(user['id'],question,brief); return jsonify(brief)
    except ValueError as exc:return jsonify({'error':str(exc)}),400
    except Exception:return jsonify({'error':'research_service_unavailable'}),503

@module5.get('/research')
def research_history():
    user,response=require_auth('USER')
    if response:return response
    try:return jsonify({'items':latest_research_briefs(user['id'],request.args.get('limit',10))})
    except Exception:return jsonify({'error':'research_persistence_unavailable'}),503

@module5.post('/roadmap')
def roadmap():
    user,response=require_auth('USER')
    if response:return response
    data=request.get_json(silent=True) or {}
    try:
        twin=latest_career_twin(user['id'])
        if not twin:return jsonify({'error':'career_twin_not_found'}),404
        twin['behavioral_competencies']=_behavioral(user['id']); research=data.get('research')
        if research is None:
            history=latest_research_briefs(user['id'],1); research=history[0] if history else {}
        plan=generate_roadmap(twin,research,data.get('weeks',8)); plan['behavioral_competencies']=twin['behavioral_competencies']; plan['persistence']=save_roadmap(user['id'],plan); return jsonify(plan)
    except ValueError as exc:return jsonify({'error':str(exc)}),400
    except Exception:return jsonify({'error':'roadmap_service_unavailable'}),503

@module5.get('/roadmap')
def get_roadmap():
    user,response=require_auth('USER')
    if response:return response
    try:
        plan=latest_roadmap(user['id'])
        if not plan:return jsonify({'error':'roadmap_not_found'}),404
        return jsonify(plan)
    except Exception:return jsonify({'error':'roadmap_persistence_unavailable'}),503

@module5.get('/readiness/history')
def readiness_history():
    user,response=require_auth('USER')
    if response:return response
    try:return jsonify({'latest':latest_readiness(user['id'])})
    except Exception:return jsonify({'error':'readiness_persistence_unavailable'}),503
