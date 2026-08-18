from backend.core import production_hardening


def test_health_probe_is_public_and_structured():
    app = __import__("flask").Flask(__name__)
    production_hardening.install(app)
    client = app.test_client()
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json["status"] == "ok"
    assert response.headers["X-Request-ID"]
    assert response.headers["X-Content-Type-Options"] == "nosniff"


def test_ready_probe_returns_503_when_database_is_unavailable(monkeypatch):
    app = __import__("flask").Flask(__name__)
    production_hardening.install(app)

    class BrokenDB:
        def __enter__(self):
            raise RuntimeError("database_down")
        def __exit__(self, *args):
            return False

    from backend.auth import auth_db
    monkeypatch.setattr(auth_db, "db_connect", lambda: BrokenDB())
    response = app.test_client().get("/readyz")
    assert response.status_code == 503
    assert response.json["status"] == "not_ready"
    assert response.json["checks"]["database"] == "unavailable"


def test_rate_limit_returns_retryable_429(monkeypatch):
    app = __import__("flask").Flask(__name__)
    monkeypatch.setenv("API_RATE_LIMIT_PER_MINUTE", "1")
    production_hardening._buckets.clear()
    production_hardening.install(app)
    client = app.test_client()
    assert client.get("/api/test").status_code == 404
    response = client.get("/api/test")
    assert response.status_code == 429
    assert response.json["error"] == "rate_limited"
