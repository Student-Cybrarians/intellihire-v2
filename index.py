"""Canonical IntelliHire backend entrypoint.

The repository root intentionally contains only this Python entrypoint. All
application implementation lives under backend/.
"""
from backend.core.app import app
from backend.core.production_hardening import install
from backend.auth.oauth_bridge import google_login, google_callback
from backend.api.auth_api_alias import auth_api
from backend.api.admin_api import admin_api

# Replace the legacy /auth Google handlers with the same persistent-state
# implementation used by /api/auth. This keeps both callback URLs consistent
# during the migration and across Vercel serverless instances.
if 'auth.google_login' in app.view_functions:
    app.view_functions['auth.google_login'] = google_login
if 'auth.google_callback' in app.view_functions:
    app.view_functions['auth.google_callback'] = google_callback

if "auth_api" not in app.blueprints:
    app.register_blueprint(auth_api)
if "admin_api" not in app.blueprints:
    app.register_blueprint(admin_api)

install(app)
handler = app
