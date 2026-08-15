import module3_evaluator as evaluator


def test_python_static_analysis_never_executes_code():
    result=evaluator.evaluate_code('def solve(x):\n    return x + 1', 'python', 'increment x')
    assert result['execution']=='not_run'
    assert result['security_boundary']=='static_analysis_only'
    assert 0 <= result['score'] <= 100


def test_python_syntax_failure_is_scored_safely():
    result=evaluator.evaluate_code('def solve(:', 'python', 'fix syntax')
    assert result['execution']=='not_run'
    assert result['score'] <= 25
    assert result['security_boundary']=='static_analysis_only'


def test_code_size_and_empty_validation():
    try:
        evaluator.evaluate_code('', 'python')
        assert False
    except ValueError as exc:
        assert str(exc)=='code_required'


def test_ai_output_is_optional_and_fallback_is_deterministic(monkeypatch):
    monkeypatch.delenv('OPENAI_API_KEY', raising=False)
    monkeypatch.delenv('NVIDIA_API_KEY', raising=False)
    result=evaluator.evaluate_code('def solve(x):\n    return x', 'python', 'return x')
    assert result['provider']=='deterministic-fallback'
    assert result['is_ai'] is False
    assert result['execution']=='not_run'
