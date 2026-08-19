"""Canonical IntelliHire Flask backend application.

The Next.js app owns presentation routes. This module owns the Python API,
authentication blueprints, module services, and health boundary used by Vercel.
"""
from __future__ import annotations

import os
from flask import Flask, jsonify, request

from backend.auth.auth_routes import auth, require_auth
from backend.auth.auth_db import init_db, record_performance
from backend.auth.public_routes import public
from backend.auth.oauth_bridge import google_login as production_google_login, google_callback as production_google_callback
from backend.api.ai_routes import ai_api
from backend.modules.module2.module2_routes import module2
from backend.modules.module3.module3_routes import module3
from backend.modules.module4.module4_routes import module4
from backend.modules.module5.module5_routes import module5
from backend.modules.module1.module1_ai import analyze_with_ai


app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = os.getenv("FLASK_SECRET_KEY", os.getenv("SESSION_SECRET", "dev-only-change-me"))
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_SAMESITE="Lax",
)

for blueprint in (public, auth, module2, module3, module4, module5, ai_api):
    if blueprint.name not in app.blueprints:
        app.register_blueprint(blueprint)

# Keep the legacy /auth OAuth URLs on the same production PostgreSQL-backed
# implementation as /api/auth. This is important when GOOGLE_REDIRECT_URI is
# configured with the legacy callback URL.
app.view_functions["auth.google_login"] = production_google_login
app.view_functions["auth.google_callback"] = production_google_callback


def _init_db() -> None:
    try:
        init_db()
    except Exception:
        # Database initialization must not prevent health/auth endpoints from
        # loading; individual persistence operations report their own failures.
        pass


def _text(value) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return " ".join(str(v) for v in value.values())
    return str(value or "")


@app.get("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "engine": "IntelliHire Python backend",
        "version": "3.0",
        "modules": ["module1", "module2", "module3", "module4", "module5"],
        "auth": "enabled",
    })


@app.post("/api/analyze")
def api_analyze():
    user, response = require_auth("USER")
    if response:
        return response

    payload = request.get_json(silent=True) or {}
    resume = _text(payload.get("resume", ""))
    job = _text(payload.get("job", ""))
    if len(resume.strip()) < 40 or len(job.strip()) < 40:
        return jsonify({"error": "resume_and_job_required"}), 422

    try:
        result = analyze_with_ai(resume, job, str(payload.get("company", ""))[:160], str(payload.get("role", ""))[:160])
    except Exception:
        return jsonify({"error": "analysis_unavailable"}), 503

    # Keep the frontend contract stable while the backend intelligence layer
    # uses snake_case domain fields.
    result = {
        **result,
        "atsScore": result.get("ats_score", 0),
        "overallMatch": result.get("overall_match", 0),
        "skillsMatch": result.get("skills_match", 0),
        "keywordMatch": result.get("keyword_match", 0),
        "semanticSimilarity": result.get("semantic_match", 0),
        "missingSkills": result.get("missing_skills", []),
        "shortlist": result.get("shortlist", "CONSIDER"),
        "isSimulated": not bool(result.get("is_ai")),
    }

    try:
        record_performance(user["id"], "module1", result["atsScore"], result)
    except Exception:
        pass
    return jsonify(result)


_init_db()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
