from flask import Blueprint, jsonify, request
from module5_engine import evaluate
from auth_routes import require_auth
from auth_db import get_user_performance, record_performance
from career_intelligence import build_career_twin, build_roadmap
from career_twin_store import save as save_career_twin, latest as latest_career_twin

module5 = Blueprint('module5', __name__, url_prefix='/api/module5')

@module5.post('/evaluate')
def evaluate_route():
    user, response = require_auth('USER')
    if response:
        return response
    performance=get_user_performance(user['id'])
    scores={f'Module {i}': (performance[f'module{i}']['score'] if performance[f'module{i}'] else 0) for i in range(1,5)}
    result=evaluate(scores)
    try:
        record_performance(user['id'],'module5',result.get('score',result.get('readiness',0)),result)
    except Exception:
        pass
    return jsonify(result)

@module5.get('/summary')
def summary():
    user, response = require_auth('USER')
    if response:
        return response
    performance=get_user_performance(user['id'])
    scores={f'Module {i}': (performance[f'module{i}']['score'] if performance[f'module{i}'] else 0) for i in range(1,5)}
    result=evaluate(scores)
    return jsonify(result)

@module5.post('/career-twin')
def career_twin():
    user, response = require_auth('USER')
    if response:
        return response
    data=request.get_json(silent=True) or {}
    resume=str(data.get('resume',''))
    jd=str(data.get('job_description',data.get('jd','')))
    role=str(data.get('role',''))
    if not resume.strip() or not jd.strip():
        return jsonify({'error':'resume_and_job_description_required'}),400
    try:
        twin=build_career_twin(resume,jd,role)
        twin['roadmap']=build_roadmap(twin,data.get('weeks',8))
        save_result=save_career_twin(user['id'],twin,resume,jd)
        twin['persistence']=save_result
        return jsonify(twin)
    except Exception:
        return jsonify({'error':'career_twin_persistence_unavailable'}),503

@module5.get('/career-twin')
def get_career_twin():
    user, response = require_auth('USER')
    if response:
        return response
    try:
        twin=latest_career_twin(user['id'])
    except Exception:
        return jsonify({'error':'career_twin_persistence_unavailable'}),503
    if not twin:
        return jsonify({'error':'career_twin_not_found'}),404
    return jsonify(twin)
