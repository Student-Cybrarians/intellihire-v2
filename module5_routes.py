from flask import Blueprint, jsonify, request
from module5_engine import evaluate
from auth_routes import require_auth
from auth_db import get_user_performance, record_performance

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
