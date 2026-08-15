"""Vercel WSGI entrypoint for IntelliHire.

Vercel discovers Python functions from the api/ directory. The application
itself remains in app.py so local Gunicorn execution continues to work.
"""
from app import app

# Vercel's Python runtime looks for a WSGI application named `app`.
__all__ = ["app"]
