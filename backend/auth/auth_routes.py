import base64, hashlib, hmac, json, os, secrets, time, urllib.parse
from io import BytesIO
from flask import Blueprint, abort, redirect, request, jsonify, make_response, send_file
from backend.auth.auth_db import get_or_create_google_user, create_session, get_session, revoke_session, audit, record_performance
from backend.modules.module1.module1_ai import analyze_with_ai, resume_docx_bytes, resume_pdf_bytes, resume_csv_bytes
from backend.intelligence.ml_engine import build_career_context, career_gap_analysis, research_plan

try:
    import requests
except ImportError:
    requests = None
try:
    from google.oauth2 import id_token
    from google.auth.transport import requests as google_requests
except ImportError:
    id_token = None
    google_requests = None

auth = Blueprint('auth', __name__, url_prefix='/auth')
OAUTH_STATE_COOKIE = 'intellihire_oauth_state'
OAUTH_NONCE_COOKIE = 'intellihire_oauth_nonce'
SESSION_COOKIE = 'intellihire_session'
GOOGLE_AUTHORIZE = 'https://accounts.google.com/o/oauth2/v2/auth'
GOOGLE_TOKEN = 'https://oauth2.googleapis.com/token'


def current_user():
    return get_session(request.cookies.get(SESSION_COOKIE))


def require_auth(role=None):
    user = current_user()
    if not user or user.get('status') != 'ACTIVE':
        return None, redirect('/')
    if role and user.get('role') != role:
        abort(403)
    return user, None


def _google_configured():
    return all(os.getenv(k) for k in ('GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET', 'GOOGLE_REDIRECT_URI')) and requests is not None and id_token is not None and google_requests is not None


def _oauth_signing_key():
    return os.getenv('GOOGLE_CLIENT_SECRET', '').encode('utf-8')


def _build_oauth_state(nonce):
    payload = {'nonce': nonce, 'iat': int(time.time())}
    raw = json.dumps(payload, separators=(',', ':'), sort_keys=True).encode('utf-8')
    body = base64.urlsafe_b64encode(raw).decode().rstrip('=')
    key = _oauth_signing_key()
    signature = hmac.new(key, body.encode('ascii'), hashlib.sha256).digest()
    return body + '.' + base64.urlsafe_b64encode(signature).decode().rstrip('=')


def _read_oauth_state(state):
    try:
        body, encoded_sig = state.split('.', 1)
        key = _oauth_signing_key()
        if not key:
            return None
        expected = hmac.new(key, body.encode('ascii'), hashlib.sha256).digest()
        supplied = base64.urlsafe_b64decode(encoded_sig + '=' * (-len(encoded_sig) % 4))
        if not hmac.compare_digest(expected, supplied):
            return None
        payload = json.loads(base64.urlsafe_b64decode(body + '=' * (-len(body) % 4)).decode('utf-8'))
        if not isinstance(payload, dict) or not payload.get('nonce'):
            return None
        if abs(int(time.time()) - int(payload.get('iat', 0))) > 600:
            return None
        return payload
    except Exception:
        return None


@auth.get('/google')
def google_login():
    # Keep the legacy /auth route wired to the same production OAuth bridge as
    # /api/auth. This is important when GOOGLE_REDIRECT_URI points at /auth.
    from backend.auth.oauth_bridge import google_login as production_google_login
    return production_google_login()


@auth.get('/google/callback')
def google_callback():
    # The callback must use the same server-side state store as the login route;
    # otherwise a valid /api/auth login can fail with invalid_oauth_state when
    # Google redirects to the legacy /auth callback URL.
    from backend.auth.oauth_bridge import google_callback as production_google_callback
    return production_google_callback()


@auth.get('/logout')
def logout():
    user = current_user(); raw = request.cookies.get(SESSION_COOKIE)
    if raw: revoke_session(raw)
    if user: audit('USER_LOGOUT', user['id'], user['id'], request.remote_addr, request.headers.get('User-Agent', ''))
    response = make_response(redirect('/'))
    response.set_cookie(SESSION_COOKIE, '', expires=0, httponly=True, secure=True, samesite='Lax', path='/')
    return response


@auth.get('/me')
def me():
    user = current_user()
    if not user:
        response = jsonify({'authenticated': False})
        response.status_code = 401
    else:
        response = jsonify({'authenticated': True, 'user': user})
    response.headers['Cache-Control'] = 'no-store, private'
    response.headers['Vary'] = 'Cookie'
    return response


@auth.post('/module1/analyze')
def module1_analyze():
    user, response = require_auth('USER')
    if response: return response
    data = request.get_json(silent=True) or {}
    resume_text = str(data.get('resume_text', '')).strip()
    jd_text = str(data.get('jd_text', '')).strip()
    if not resume_text or not jd_text:
        return jsonify({'error': 'resume_text_and_jd_text_required'}), 400
    result = analyze_with_ai(resume_text, jd_text, str(data.get('company', '')), str(data.get('role', '')))
    result['resume_text_length'] = len(resume_text); result['jd_text_length'] = len(jd_text)
    try: record_performance(user['id'], 'module1', result.get('ats_score', 0), result)
    except Exception: pass
    return jsonify(result)


@auth.post('/module1/analyze-file')
def module1_analyze_file():
    user, response = require_auth('USER')
    if response: return response
    upload = request.files.get('resume')
    jd_text = request.form.get('jd_text', '').strip()
    if not upload or not jd_text:
        return jsonify({'error': 'resume_file_and_jd_text_required'}), 400
    filename = (upload.filename or '').lower()
    raw = upload.read()
    try:
        if filename.endswith('.pdf'):
            from pypdf import PdfReader
            resume_text = '\n'.join((page.extract_text() or '') for page in PdfReader(BytesIO(raw)).pages)
        elif filename.endswith('.docx'):
            from docx import Document
            resume_text = '\n'.join(p.text for p in Document(BytesIO(raw)).paragraphs)
        elif filename.endswith(('.txt', '.md')):
            resume_text = raw.decode('utf-8', errors='ignore')
        else:
            return jsonify({'error': 'unsupported_resume_format', 'supported': ['pdf', 'docx', 'txt', 'md']}), 415
    except Exception as exc:
        return jsonify({'error': 'resume_parse_failed', 'detail': str(exc)}), 422
    result = analyze_with_ai(resume_text, jd_text, request.form.get('company', ''), request.form.get('role', ''))
    result['source_filename'] = upload.filename
    result['resume_text_length'] = len(resume_text)
    try: record_performance(user['id'], 'module1', result.get('ats_score', 0), result)
    except Exception: pass
    return jsonify(result)


@auth.post('/career/intelligence')
def career_intelligence():
    user, response = require_auth('USER')
    if response: return response
    data = request.get_json(silent=True) or {}
    profile = data.get('profile') or {}
    target_role = str(data.get('target_role') or profile.get('target_role') or '').strip()
    if not target_role:
        return jsonify({'error': 'target_role_required'}), 400
    performance = data.get('performance') or []
    context = build_career_context(profile, performance, target_role)
    gap = career_gap_analysis(profile, target_role)
    plan = research_plan(profile, target_role)
    return jsonify({'mode': 'career-preparation', 'context': context, 'gap': gap, 'research_plan': plan, 'human_review_required_for_employment_decisions': True})


@auth.post('/module1/export/<fmt>')
def module1_export(fmt):
    user, response = require_auth('USER')
    if response: return response
    data = request.get_json(silent=True) or {}
    resume = data.get('tailored_resume') or {}
    if not resume: return jsonify({'error': 'tailored_resume_required'}), 400
    try:
        if fmt == 'docx':
            return send_file(BytesIO(resume_docx_bytes(resume)), as_attachment=True, download_name='intellihire_ats_resume.docx', mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        if fmt == 'pdf':
            return send_file(BytesIO(resume_pdf_bytes(resume)), as_attachment=True, download_name='intellihire_ats_resume.pdf', mimetype='application/pdf')
        if fmt == 'csv':
            return send_file(BytesIO(resume_csv_bytes(resume)), as_attachment=True, download_name='intellihire_ats_resume.csv', mimetype='text/csv')
    except Exception as exc:
        return jsonify({'error': 'resume_export_failed', 'detail': str(exc)}), 500
    return jsonify({'error': 'unsupported_export_format', 'supported': ['docx', 'pdf', 'csv']}) , 415
