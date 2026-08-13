import os, secrets, urllib.parse
from flask import Blueprint, abort, redirect, request, jsonify, make_response
from auth_db import get_or_create_google_user, create_session, get_session, revoke_session, audit

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
    params = {
        'client_id': os.getenv('GOOGLE_CLIENT_ID'),
        'redirect_uri': os.getenv('GOOGLE_REDIRECT_URI'),
        'response_type': 'code',
        'scope': 'openid email profile',
        'access_type': 'online',
        'state': state,
        'nonce': nonce,
        'prompt': 'select_account',
    }
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
        token_response = requests.post(
            GOOGLE_TOKEN,
            data={
                'code': code,
                'client_id': os.getenv('GOOGLE_CLIENT_ID'),
                'client_secret': os.getenv('GOOGLE_CLIENT_SECRET'),
                'redirect_uri': os.getenv('GOOGLE_REDIRECT_URI'),
                'grant_type': 'authorization_code',
            },
            timeout=15,
        )
        token_response.raise_for_status()
        token_data = token_response.json()
        raw_id_token = token_data.get('id_token')
        if not raw_id_token:
            return redirect('/?auth_error=missing_id_token')

        claims = id_token.verify_oauth2_token(
            raw_id_token,
            google_requests.Request(),
            os.getenv('GOOGLE_CLIENT_ID'),
        )
        issuer = claims.get('iss')
        if issuer not in ('accounts.google.com', 'https://accounts.google.com'):
            return redirect('/?auth_error=invalid_issuer')
        if claims.get('nonce') != request.cookies.get(OAUTH_NONCE_COOKIE):
            return redirect('/?auth_error=invalid_nonce')
        if claims.get('email_verified') is not True:
            return redirect('/?auth_error=email_not_verified')
        if not claims.get('sub') or not claims.get('email'):
            return redirect('/?auth_error=invalid_google_identity')

        user = get_or_create_google_user(
            claims['sub'],
            claims['email'],
            claims.get('name', ''),
            claims.get('picture', ''),
        )
        if user.get('status') != 'ACTIVE':
            return redirect('/?auth_error=account_not_active')

        raw_session, expires = create_session(
            user['id'],
            request.remote_addr,
            request.headers.get('User-Agent', ''),
        )
        audit(
            'USER_LOGIN',
            user['id'],
            user['id'],
            request.remote_addr,
            request.headers.get('User-Agent', ''),
            {'provider': 'google'},
        )
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
    user = current_user()
    raw = request.cookies.get(SESSION_COOKIE)
    if raw:
        revoke_session(raw)
    if user:
        audit('USER_LOGOUT', user['id'], user['id'], request.remote_addr, request.headers.get('User-Agent', ''))
    response = make_response(redirect('/'))
    response.set_cookie(SESSION_COOKIE, '', expires=0, httponly=True, secure=True, samesite='Lax', path='/')
    return response


@auth.get('/me')
def me():
    user = current_user()
    if not user:
        return jsonify({'authenticated': False}), 401
    return jsonify({'authenticated': True, 'user': user})
