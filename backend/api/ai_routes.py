from flask import Blueprint, Response, jsonify, request, stream_with_context

from backend.ai import AIProviderError, AIUnavailableError, get_orchestrator
from backend.auth.auth_routes import require_auth

ai_api = Blueprint('ai_api', __name__, url_prefix='/api/ai')


def _auth():
    return require_auth('USER')


@ai_api.get('/health')
def health():
    user, response = _auth()
    if response:
        return response
    status = get_orchestrator().health()
    configured = any(v.get('configured') for v in status.get('providers', {}).values())
    return jsonify({'status': 'ok' if configured else 'degraded', **status}), 200 if configured else 503


@ai_api.post('/stream')
def stream():
    user, response = _auth()
    if response:
        return response
    payload = request.get_json(silent=True) or {}
    feature = str(payload.get('feature', 'general'))[:80]
    task = str(payload.get('task', '')).strip()
    context = payload.get('context') if isinstance(payload.get('context'), dict) else {}
    if not task:
        return jsonify({'error': 'task_required'}), 400
    try:
        chunks = get_orchestrator().stream(feature=feature, task=task, context=context, reasoning=bool(payload.get('reasoning', False)))
        return Response(stream_with_context((f'data: {chunk}\n\n' for chunk in chunks)), mimetype='text/event-stream')
    except AIUnavailableError:
        return jsonify({'error': 'AI analysis is temporarily unavailable.'}), 503
    except AIProviderError:
        return jsonify({'error': 'AI analysis failed. Please retry.'}), 502
