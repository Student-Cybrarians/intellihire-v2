from backend.modules.module4.module4_competency import aggregate


def _event(qid, score=85):
    return {
        'question': {'id': qid, 'prompt': 'test'},
        'metrics': {
            'communication': score,
            'confidence': score,
            'clarity': score,
            'relevance': score,
            'star_score': score,
            'feedback': ['keep evidence-based examples'],
        },
    }


def test_competencies_are_bounded_and_evidence_backed():
    result = aggregate([_event('hr-02', 90), _event('hr-03', 60)])
    assert result['dimensions']['ownership']['score'] == 90.0
    assert result['dimensions']['teamwork']['score'] == 60.0
    assert result['dimensions']['ownership']['evidence_count'] == 1
    assert 'ownership' in result['strengths']
    assert 'teamwork' in result['development_areas']
    assert result['integrity']['candidate_evidence_only'] is True
    assert result['integrity']['fabrication'] is False


def test_missing_competencies_are_not_claimed_as_gaps():
    result = aggregate([_event('hr-01', 85)])
    assert result['dimensions']['ownership']['status'] == 'insufficient_evidence'
    assert result['dimensions']['ownership']['evidence_count'] == 0
    assert 'ownership' not in result['development_areas']


def test_unknown_question_is_ignored():
    result = aggregate([_event('unknown', 100)])
    assert all(v['evidence_count'] == 0 for v in result['dimensions'].values())
