"""Vercel entrypoint for the IntelliHire Flask application."""
from backend.core.app import app
from backend.core.production_hardening import install

# Keep deployment hardening at the actual WSGI entrypoint.
install(app)

handler = app
