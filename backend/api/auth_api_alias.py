"""Vercel-facing aliases for authentication endpoints under /api/auth."""
from flask import Blueprint

from backend.auth.auth_routes import google_login, google_callback, logout, me


auth_api = Blueprint("auth_api", __name__, url_prefix="/api/auth")

auth_api.add_url_rule("/google", view_func=google_login, methods=["GET"])
auth_api.add_url_rule("/google/callback", view_func=google_callback, methods=["GET"])
auth_api.add_url_rule("/logout", view_func=logout, methods=["GET"])
auth_api.add_url_rule("/me", view_func=me, methods=["GET"])
