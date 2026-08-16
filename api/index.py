"""Vercel entrypoint for the IntelliHire Flask application."""
from backend.core.app import app
from backend.core.production_hardening import install
from auth_api_alias import auth_api

# Vercel exposes api/index.py under /api/*; keep authentication available
# under the same origin without colliding with Next.js /auth/* pages.
if "auth_api" not in app.blueprints:
    app.register_blueprint(auth_api)

# Keep deployment hardening at the actual WSGI entrypoint.
install(app)

handler = app
