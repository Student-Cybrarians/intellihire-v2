"""Production request hardening and deployment health endpoints."""
from __future__ import annotations

import os
import threading
import time
import uuid
from collections import defaultdict, deque
from flask import Flask, g, jsonify, request

_WINDOW = 60.0
_lock = threading.Lock()
_buckets = defaultdict(deque)


def _limit(path):
    name = "API_RATE_LIMIT_PER_MINUTE" if path.startswith("/api/") else "REQUEST_RATE_LIMIT_PER_MINUTE"
    default = "30" if path.startswith("/api/") else "60"
    try:
        return max(1, min(int(os.getenv(name, default)), 300))
    except ValueError:
        return int(default)


def _client_key():
    if os.getenv("TRUST_PROXY_HEADERS", "0") == "1":
        forwarded = request.headers.get("X-Forwarded-For", "").split(",", 1)[0].strip()
        if forwarded:
            return forwarded
    return request.remote_addr or "unknown"


def _allow(key, limit):
    now = time.monotonic()
    with _lock:
        bucket = _buckets[key]
        cutoff = now - _WINDOW
        while bucket and bucket[0] <= cutoff:
            bucket.popleft()
        if len(bucket) >= limit:
            return False
        bucket.append(now)
        if len(_buckets) > 5000:
            stale = [k for k, v in _buckets.items() if not v or v[-1] <= cutoff]
            for stale_key in stale[:1000]:
                _buckets.pop(stale_key, None)
        return True


def install(app: Flask):
    try:
        configured = int(os.getenv("MAX_CONTENT_LENGTH_BYTES", str(5 * 1024 * 1024)))
    except ValueError:
        configured = 5 * 1024 * 1024
    app.config["MAX_CONTENT_LENGTH"] = max(64 * 1024, min(configured, 25 * 1024 * 1024))

    @app.before_request
    def _before():
        g.request_id = request.headers.get("X-Request-ID", "")[:128] or uuid.uuid4().hex
        if request.endpoint in {"healthz", "readyz", "static"} or request.method == "OPTIONS":
            return None
        if not _allow(_client_key(), _limit(request.path)):
            return jsonify({"error": "rate_limited", "request_id": g.request_id}), 429
        g.started_at = time.monotonic()
        return None

    @app.after_request
    def _after(response):
        response.headers["X-Request-ID"] = getattr(g, "request_id", uuid.uuid4().hex)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none'; base-uri 'self'"
        if os.getenv("VERCEL") or os.getenv("FLASK_ENV") == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        started = getattr(g, "started_at", None)
        if started is not None:
            response.headers["Server-Timing"] = f"app;dur={(time.monotonic() - started) * 1000:.1f}"
        return response

    @app.errorhandler(413)
    def _too_large(_error):
        return jsonify({"error": "payload_too_large", "request_id": getattr(g, "request_id", None)}), 413

    @app.get("/healthz")
    def healthz():
        return jsonify({"status": "ok", "service": "intellihire", "request_id": g.request_id})

    @app.get("/readyz")
    def readyz():
        checks = {"application": "ok"}
        try:
            from auth_db import db_connect
            with db_connect() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                    cur.fetchone()
            checks["database"] = "ok"
        except Exception:
            checks["database"] = "unavailable"
            return jsonify({"status": "not_ready", "checks": checks, "request_id": g.request_id}), 503
        return jsonify({"status": "ready", "checks": checks, "request_id": g.request_id})

    return app
