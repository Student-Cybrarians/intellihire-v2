"""Production OAuth handlers with server-side state correlation.

OAuth state is persisted in PostgreSQL so Vercel serverless instances do not
need to share browser-state signing keys or memory.
"""
import os
import secrets
import urllib.parse
from flask import make_response, redirect, request
from backend.auth.auth_db import create_oauth_state, consume_oauth_state, get_or_create_google_user, create_session, audit

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

SESSION_COOKIE = 'intellihire_session'
OAUTH_STATE_COOKIE = 'intellihire_oauth_state'
OAUTH_NONCE_COOKIE = 'intellihire_oauth_nonce'
GOOGLE_AUTHORIZE = 'https://accounts.google.com/o/oauth2/v2/auth'
GOOGLE_TOKEN = 'https://oauth2.googleapis.com/token'
CANONICAL_HOST = 'intellihire-v2.vercel.app'
CANONICAL_GOOGLE_REDIRECT_URI = f'https://{CANONICAL_HOST}/auth/google/callback'


def _configured():
    return all(os.getenv(k) for k in ('GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET', 'GOOGLE_REDIRECT_URI')) and requests is not None and id_token is not None and google_requests is not None


def _redirect_uri():
    """Use the canonical production callback on the canonical host.

    Keep the configured legacy callback available for old deployment URLs so
    existing OAuth clients do not break during migration. Once the canonical
    URI is registered in Google Cloud, the canonical host becomes the stable
    production OAuth surface.
    """
    host = (request.host or '').split(':', 1)[0].lower()
    if host == CANONICAL_HOST:
        return CANONICAL_GOOGLE_REDIRECT_URI
    return os.getenv('GOOGLE_REDIRECT_URI')


def google_login():
    if not _configured():
        return redirect('/?auth_error=google_not_configured')
    nonce = secrets.token_urlsafe(32)
    state, _ = create_oauth_state(nonce)
    redirect_uri = _redirect_uri()
    params = {
        'client_id': os.getenv('GOOGLE_CLIENT_ID'),
        'redirect_uri': redirect_uri,
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


def google_callback():
    state = request.args.get('state', '')
    state_payload = consume_oauth_state(state)
    if not state_payload:
        return redirect('/?auth_error=invalid_oauth_state')
    code = request.args.get('code')
    if not code:
        return redirect('/?auth_error=oauth_cancelled')
    if not _configured():
        return redirect('/?auth_error=oauth_unavailable')
    try:
        redirect_uri = _redirect_uri()
        token_response = requests.post(GOOGLE_TOKEN, data={
            'code': code,
            'client_id': os.getenv('GOOGLE_CLIENT_ID'),
            'client_secret': os.getenv('GOOGLE_CLIENT_SECRET'),
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code',
        }, timeout=15)
        token_response.raise_for_status()
        token_data = token_response.json()
        raw_id_token = token_data.get('id_token')
        if not raw_id_token:
            return redirect('/?auth_error=missing_id_token')
        claims = id_token.verify_oauth2_token(raw_id_token, google_requests.Request(), os.getenv('GOOGLE_CLIENT_ID'))
        if claims.get('iss') not in ('accounts.google.com', 'https://accounts.google.com'):
            return redirect('/?auth_error=invalid_issuer')
        if claims.get('nonce') != state_payload.get('nonce'):
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
