from pathlib import Path


def test_module5_ui_uses_readiness_and_skill_graph_contracts():
    html = Path('templates/module5.html').read_text(encoding='utf-8')
    assert "fetch('/api/module5/summary'" in html
    assert "fetch('/api/module5/career-twin/skill-graph'" in html
    assert 'x.weighted_score' in html
    assert 'x.confidence' in html
    assert 'x.skill_coverage' in html
    assert 'x.roadmap_completion' in html
    assert 'x.integrity' in html
    assert 'x.next_actions' in html
    assert 'x.behavioral_competencies' in html
    assert 'graph.nodes' in html
    assert 'hiring_probability' not in html
    assert 'autonomous hiring outcome' in html


def test_module5_ui_handles_service_failure_without_hiring_claim():
    html = Path('templates/module5.html').read_text(encoding='utf-8')
    assert 'Readiness service temporarily unavailable' in html
    assert 'No autonomous hiring outcome is produced while readiness evidence is unavailable.' in html
    assert 'Skill graph temporarily unavailable.' in html
