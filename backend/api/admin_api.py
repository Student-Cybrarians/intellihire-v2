"""Vercel-facing admin API boundary for the Next.js admin UI."""
from flask import Blueprint, jsonify, request

from backend.auth.auth_routes import current_user
from backend.auth.auth_db import get_user_activity, get_user_performance, list_user_summaries

admin_api = Blueprint("admin_api", __name__, url_prefix="/api/admin")


def _admin_guard():
    user = current_user()
    if not user or user.get("status") != "ACTIVE":
        return None, jsonify({"error": "authentication_required"}), 401
    if user.get("role") != "ADMIN":
        return None, jsonify({"error": "admin_access_required"}), 403
    return user, None, None


@admin_api.get("/overview")
def overview():
    _, response, status = _admin_guard()
    if response:
        return response, status
    try:
        query = (request.args.get("q") or "").strip() or None
        users = list_user_summaries(query)
        activity = get_user_activity(limit=40)
        completed = [u["overall"] for u in users if u.get("overall") is not None]
        return jsonify({
            "users": users,
            "activity": activity,
            "stats": {
                "users": len(users),
                "active": sum(1 for u in users if u.get("status") == "ACTIVE"),
                "admins": sum(1 for u in users if u.get("role") == "ADMIN"),
                "average_readiness": round(sum(completed) / len(completed), 1) if completed else None,
            },
        })
    except Exception as exc:
        return jsonify({"error": "admin_data_unavailable", "detail": str(exc)}), 503


@admin_api.get("/users/<user_id>")
def user_detail(user_id):
    _, response, status = _admin_guard()
    if response:
        return response, status
    try:
        users = [u for u in list_user_summaries() if u["id"] == user_id]
        if not users:
            return jsonify({"error": "user_not_found"}), 404
        return jsonify({
            "user": users[0],
            "performance": get_user_performance(user_id),
            "activity": get_user_activity(user_id, limit=100),
        })
    except Exception as exc:
        return jsonify({"error": "admin_data_unavailable", "detail": str(exc)}), 503
