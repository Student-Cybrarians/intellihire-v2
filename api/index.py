"""Vercel entrypoint for the IntelliHire Flask application."""
from app import app
from production_hardening import install

# Apply deployment-only hardening at the actual WSGI entrypoint so Vercel and
# local Flask imports can continue to use the same core application object.
install(app)

handler = app
