"""Vercel WSGI entrypoint for IntelliHire."""
from app import app

# Register support at the production entrypoint without creating a second
# blueprint registration when the application is imported locally.
from chat_routes import support
if "support" not in {bp.name for bp in app.iter_blueprints()}:
    app.register_blueprint(support, url_prefix="/auth")

__all__ = ["app"]
