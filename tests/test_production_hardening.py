from production_hardening import rate_limit, security_headers


def test_rate_limit_blocks_after_limit():
    key='test-rate-limit'
    assert rate_limit(key, limit=2, window=60)[0]
    assert rate_limit(key, limit=2, window=60)[0]
    allowed, retry = rate_limit(key, limit=2, window=60)
    assert not allowed
    assert retry >= 1


def test_security_headers_are_present(app):
    with app.test_request_context('/'):
        response=app.make_response('ok')
        response=security_headers(response)
        assert response.headers['X-Content-Type-Options']=='nosniff'
        assert response.headers['X-Frame-Options']=='DENY'
        assert 'frame-ancestors' in response.headers['Content-Security-Policy']
