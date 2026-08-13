import os, secrets, urllib.parse
from flask import Blueprint, abort, redirect, request, jsonify, session, render_template, make_response
from auth_db import get_or_create_google_user, create_session, get_session, revoke_session, audit

try:
    import requests
except ImportError:
    requests = None

auth = Blueprint('auth', __name__, url_prefix='/auth')
OAUTH_STATE_COOKIE = 'intellihire_oauth_state'
SESSION_COOKIE = 'intellihire_session'
GOOGLE_AUTHORIZE = 'https://accounts.google.com/o/oauth2/v2/auth'
GOOGLE_TOKEN = 'https://oauth2.googleapis.com/token'
GOOGLE_USERINFO = 'https://openidconnect.googleapis.com/v1/userinfo'


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
    return all(os.getenv(k) for k in ('GOOGLE_CLIENT_ID','GOOGLE_CLIENT_SECRET','GOOGLE_REDIRECT_URI')) and requests is not None


@auth.get('/google')
def google_login():
    if not _google_configured():
        return redirect('/?auth_error=google_not_configured')
    state = secrets.token_urlsafe(32)
    params = {
        'client_id': os.getenv('GOOGLE_CLIENT_ID'),
        'redirect_uri': os.getenv('GOOGLE_REDIRECT_URI'),
        'response_type': 'code',
        'scope': 'openid email profile',
        'access_type': 'online',
        'state': state,
        'prompt': 'select_account',
    }
    response = make_response(redirect(GOOGLE_AUTHORIZE + '?' + urllib.parse.urlencode(params)))
    response.set_cookie(OAUTH_STATE_COOKIE, state, max_age=600, httponly=True, secure=True, samesite='Lax')
    return response


@auth.get('/google/callback')
def google_callback():
    state = request.args.get('state')
    expected = request.cookies.get(OAUTH_STATE_COOKIE)
    if not state or not expected or not secrets.compare_digest(state, expected):
        return redirect('/?auth_error=invalid_oauth_state')
    code = request.args.get('code')
    if not code or requests is None or not _google_configured():
        return redirect('/?auth_error=oauth_unavailable')
    try:
        token_response = requests.post(GOOGLE_TOKEN, data={
            'code': code,
            'client_id': os.getenv('GOOGLE_CLIENT_ID'),
            'client_secret': os.getenv('GOOGLE_CLIENT_SECRET'),
            'redirect_uri': os.getenv('GOOGLE_REDIRECT_URI'),
            'grant_type': 'authorization_code',
        }, timeout=15)
        token_response.raise_for_status()
        token = token_response.json().get('access_token')
        if not token:
            return redirect('/?auth_error=missing_access_token')
        profile = requests.get(GOOGLE_USERINFO, headers={'Authorization': f'Bearer {token}'}, timeout=15)
        profile.raise_for_status()
        data = profile.json()
        if not data.get('sub') or not data.get('email'):
            return redirect('/?auth_error=invalid_google_identity')
        user = get_or_create_google_user(data['sub'], data['email'], data.get('name',''), data.get('picture',''))
        if user.get('status') != 'ACTIVE':
            return redirect('/?auth_error=account_not_active')
        raw_session, expires = create_session(user['id'], request.remote_addr, request.headers.get('User-Agent',''))
        audit('USER_LOGIN', user['id'], user['id'], request.remote_addr, request.headers.get('User-Agent',''), {'provider':'google'})
        target = '/app/dashboard' if user['role'] == 'USER' else '/admin'
        response = make_response(redirect(target))
        response.set_cookie(SESSION_COOKIE, raw_session, expires=expires, httponly=True, secure=True, samesite='Lax', path='/')
        response.set_cookie(OAUTH_STATE_COOKIE, '', expires=0, httponly=True, secure=True, samesite='Lax')
        return response
    except Exception:
        return redirect('/?auth_error=authentication_failed')


@auth.get('/logout')
def logout():
    user = current_user()
    raw = request.cookies.get(SESSION_COOKIE)
    if raw:
        revoke_session(raw)
    if user:
        audit('USER_LOGOUT', user['id'], user['id'], request.remote_addr, request.headers.get('User-Agent',''))
    response = make_response(redirect('/'))
    response.set_cookie(SESSION_COOKIE, '', expires=0, httponly=True, secure=True, samesite='Lax', path='/')
    return response


@auth.get('/me')
def me():
    user = current_user()
    if not user:
        return jsonify({'authenticated': False}), 401
    return jsonify({'authenticated': True, 'user': user})


@auth.get('/user')
def user_entry():
    user, response = require_auth('USER')
    if response: return response
    return redirect('/app/dashboard')


@auth.get('/admin')
def admin_entry():
    user, response = require_auth('ADMIN')
    if response: return response
    return render_template('admin.html', user=user)
