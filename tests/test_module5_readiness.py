from module5_readiness import build_readiness


def test_readiness_is_bounded_and_support_only():
    result = build_readiness(
        {'Module 1': {'score': 90}, 'Module 2': {'score': 80}},
        {'matched_skills': ['python'], 'skill_gaps': ['docker']},
        {'sources': [{'url': 'https://example.com'}]},
        {'milestones': [{'status': 'completed'}]},
        {'competencies': {'Communication': {'score': 85, 'evidence_count': 2}}},
    )
    assert 0 <= result['weighted_score'] <= 100
    assert 0 <= result['confidence'] <= 1
    assert result['integrity']['autonomous_hiring_decision'] is False


def test_missing_evidence_is_not_negative_candidate_evidence():
    result = build_readiness({}, {}, {}, {}, {})
    assert result['confidence'] < 0.45
    assert result['readiness_band'] == 'Insufficient evidence'
    assert result['behavioral_competency_score'] is None


def test_module_scores_only_use_observed_performance_for_weight_denominator():
    result = build_readiness({'Module 1': {'score': 100}}, {}, {}, {}, {})
    assert result['module_scores']['Module 1'] == 100
    assert result['weighted_score'] <= 100
