import os, secrets, urllib.parse, json
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


@auth.get('/google')
def google_login():
    if not _google_configured():
        return redirect('/?auth_error=google_not_configured')
    state = secrets.token_urlsafe(32)
    nonce = secrets.token_urlsafe(32)
    params = {'client_id': os.getenv('GOOGLE_CLIENT_ID'), 'redirect_uri': os.getenv('GOOGLE_REDIRECT_URI'), 'response_type': 'code', 'scope': 'openid email profile', 'access_type': 'online', 'state': state, 'nonce': nonce, 'prompt': 'select_account'}
    response = make_response(redirect(GOOGLE_AUTHORIZE + '?' + urllib.parse.urlencode(params)))
    response.set_cookie(OAUTH_STATE_COOKIE, state, max_age=600, httponly=True, secure=True, samesite='Lax', path='/')
    response.set_cookie(OAUTH_NONCE_COOKIE, nonce, max_age=600, httponly=True, secure=True, samesite='Lax', path='/')
    return response


@auth.get('/google/callback')
def google_callback():
    state = request.args.get('state')
    expected = request.cookies.get(OAUTH_STATE_COOKIE)
    if not state or not expected or not secrets.compare_digest(state, expected):
        return redirect('/?auth_error=invalid_oauth_state')
    code = request.args.get('code')
    if not code:
        return redirect('/?auth_error=oauth_cancelled')
    if not _google_configured():
        return redirect('/?auth_error=oauth_unavailable')
    try:
        token_response = requests.post(GOOGLE_TOKEN, data={'code': code, 'client_id': os.getenv('GOOGLE_CLIENT_ID'), 'client_secret': os.getenv('GOOGLE_CLIENT_SECRET'), 'redirect_uri': os.getenv('GOOGLE_REDIRECT_URI'), 'grant_type': 'authorization_code'}, timeout=15)
        token_response.raise_for_status()
        token_data = token_response.json()
        raw_id_token = token_data.get('id_token')
        if not raw_id_token:
            return redirect('/?auth_error=missing_id_token')
        claims = id_token.verify_oauth2_token(raw_id_token, google_requests.Request(), os.getenv('GOOGLE_CLIENT_ID'))
        if claims.get('iss') not in ('accounts.google.com', 'https://accounts.google.com'):
            return redirect('/?auth_error=invalid_issuer')
        if claims.get('nonce') != request.cookies.get(OAUTH_NONCE_COOKIE):
            return redirect('/?auth_error=invalid_nonce')
        if claims.get('email_verified') is not True:
            return redirect('/?auth_error=email_not_verified')
        if not claims.get('sub') or not claims.get('email'):
            return redirect('/?auth_error=invalid_google_identity')
        user = get_or_create_google_user(claims['sub'], claims['email'], claims.get('name', ''), claims.get('picture', ''))
        if user.get('status') != 'ACTIVE':
            return redirect('/?auth_error=account_not_active')
        raw_session, expires = create_session(user['id'], request.remote_addr, request.headers.get('User-Agent', ''))
        audit('USER_LOGIN', user['id'], user['id'], request.remote_addr, request.headers.get('User-Agent', ''), {'provider': 'google'})
        target = '/admin' if user['role'] == 'ADMIN' else '/app/dashboard'
        response = make_response(redirect(target))
        response.set_cookie(SESSION_COOKIE, raw_session, expires=expires, httponly=True, secure=True, samesite='Lax', path='/')
        response.set_cookie(OAUTH_STATE_COOKIE, '', expires=0, httponly=True, secure=True, samesite='Lax', path='/')
        response.set_cookie(OAUTH_NONCE_COOKIE, '', expires=0, httponly=True, secure=True, samesite='Lax', path='/')
        return response
    except requests.HTTPError:
        return redirect('/?auth_error=google_token_exchange_failed')
    except Exception:
        return redirect('/?auth_error=authentication_failed')


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
        return jsonify({'authenticated': False}), 401
    return jsonify({'authenticated': True, 'user': user})


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
    return jsonify({'error': 'unsupported_export_format', 'supported': ['docx', 'pdf', 'csv']}), 415
