import json
from pathlib import Path


def _client():
    from importlib import import_module

    module = import_module("api.index")
    module.app.config.update(TESTING=True, SECRET_KEY="smoke-test-secret")
    return module.app.test_client()


def test_vercel_wsgi_entrypoint_and_liveness():
    client = _client()
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"
    assert response.headers["X-Request-ID"]
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"


def test_core_health_contract():
    client = _client()
    response = client.get("/api/health")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "ok"
    assert payload["auth"] == "enabled"
    assert payload["modules"] == ["module1", "module2", "module3", "module4", "module5"]


def test_public_routes_are_reachable_through_flask_entrypoint():
    client = _client()
    for path in ["/", "/about", "/how-it-works", "/features", "/pricing", "/contact"]:
        response = client.get(path, follow_redirects=False)
        assert response.status_code in {200, 302}, path
        if path != "/":
            assert b"INTELLIHIRE" in response.data, path


def test_vercel_routes_cover_public_and_application_surfaces():
    config = json.loads(Path("vercel.json").read_text(encoding="utf-8"))
    rewrites = {item["source"]: item["destination"] for item in config["rewrites"]}
    expected = {
        "/": "/api/index.py",
        "/about": "/api/index.py",
        "/how-it-works": "/api/index.py",
        "/features": "/api/index.py",
        "/pricing": "/api/index.py",
        "/contact": "/api/index.py",
        "/api/:path*": "/api/index.py",
        "/auth/:path*": "/api/index.py",
        "/admin/:path*": "/api/index.py",
        "/app/:path*": "/api/index.py",
    }
    for source, destination in expected.items():
        assert rewrites.get(source) == destination, source


def test_demo_endpoint_is_read_only_and_structurally_valid():
    client = _client()
    response = client.get("/api/demo")
    assert response.status_code == 200
    payload = response.get_json()
    assert set(payload) == {"resume", "job", "result"}
    assert payload["result"]["isSimulated"] is True


def test_protected_application_route_requires_authentication():
    client = _client()
    response = client.get("/app/dashboard")
    assert response.status_code in {302, 401}
    if response.status_code == 302:
        assert response.headers["Location"].endswith("/")


def test_ready_contract_reports_application_even_without_database():
    client = _client()
    response = client.get("/readyz")
    assert response.status_code in {200, 503}
    payload = response.get_json()
    assert payload["checks"]["application"] == "ok"
    assert payload["status"] in {"ready", "not_ready"}
