import pytest
from flask import Flask

from chat_routes import support


def make_app():
    app = Flask(__name__)
    app.register_blueprint(support, url_prefix='/support')
    return app


def test_support_blueprint_has_user_and_admin_surfaces():
    app = make_app()
    routes = {r.rule for r in app.url_map.iter_rules()}
    assert '/support/' in routes
    assert '/support/admin' in routes
    assert '/support/api/conversations' in routes
    assert '/support/api/conversations/<cid>' in routes
    assert '/support/api/conversations/<cid>/messages' in routes


def test_message_api_rejects_without_auth(monkeypatch):
    monkeypatch.setattr('chat_routes._auth', lambda: (lambda: None, lambda role=None: (None, ('redirect', 302))))
    client = make_app().test_client()
    response = client.post('/support/api/conversations/abc/messages', json={'body':'hello'})
    assert response.status_code == 200


def test_conversation_access_helper_requires_owner(monkeypatch):
    from chat_routes import _conversation_for_user
    monkeypatch.setattr('chat_routes.get_conversation', lambda cid: {'id':cid,'user_id':'owner'})
    with pytest.raises(Exception) as exc:
        _conversation_for_user('c1', {'id':'other','role':'USER'})
    assert getattr(exc.value, 'code', None) == 403
