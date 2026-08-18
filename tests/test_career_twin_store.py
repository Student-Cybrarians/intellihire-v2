from backend.intelligence.career_twin_store import _fingerprint


def test_fingerprint_is_stable_and_non_reversible():
    value = 'Python React PostgreSQL'
    first = _fingerprint(value)
    second = _fingerprint(value)
    assert first == second
    assert len(first) == 64
    assert value not in first


def test_different_inputs_have_different_fingerprints():
    assert _fingerprint('resume A') != _fingerprint('resume B')
