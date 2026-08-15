from public_routes import public
from flask import Flask


def client():
    app = Flask(__name__)
    app.register_blueprint(public)
    return app.test_client()


def test_public_pages_are_reachable():
    c = client()
    for path in ['/about', '/how-it-works', '/features', '/pricing', '/contact']:
        response = c.get(path)
        assert response.status_code == 200
        assert b'INTELLIHIRE' in response.data
        assert b'viewport' in response.data


def test_public_pages_link_to_authenticated_entry():
    c = client()
    response = c.get('/features')
    assert response.status_code == 200
    assert b'/auth/google' in response.data
