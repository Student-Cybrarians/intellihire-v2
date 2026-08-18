"""Canonical IntelliHire backend entrypoint.

The repository root intentionally contains only this Python entrypoint. All
application implementation lives under backend/.
"""
from backend.core.app import app
from backend.core.production_hardening import install
from backend.api.auth_api_alias import auth_api
from backend.api.admin_api import admin_api

if "auth_api" not in app.blueprints:
    app.register_blueprint(auth_api)
if "admin_api" not in app.blueprints:
    app.register_blueprint(admin_api)

install(app)
handler = app
