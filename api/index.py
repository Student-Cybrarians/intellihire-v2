"""Vercel entrypoint for the IntelliHire Flask application.

Keep the main application in app.py for local development while exposing an
unambiguous top-level WSGI application to Vercel's Python runtime.
"""
from app import app

handler = app
