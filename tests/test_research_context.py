from backend.research.research_context import build_context


def test_context_preserves_skill_graph_states_and_excludes_sensitive_free_text():
    result = build_context(
        {"role": "Software Engineer", "skill_gaps": ["kubernetes"]},
        {"nodes": [
            {"skill": "Python", "state": "evidenced", "priority": "high", "evidence": "Built APIs"},
            {"skill": "Kubernetes", "state": "gap", "priority": "high", "evidence": "Not observed"},
            {"skill": "Cloud", "state": "transferable", "priority": "medium", "evidence": "Related infrastructure work"},
        ]},
        {"competencies": {"Communication": {"score": 82, "confidence": 0.7, "evidence_count": 3}}},
        {"milestones": [{"title": "Containerize API", "skill": "Docker", "status": "planned", "deliverable": "Working container image"}]},
    )
    graph = result["context"]["skill_graph"]
    assert {item["state"] for item in graph} == {"evidenced", "gap", "transferable"}
    assert "Built APIs" in result["context_text"]
    assert "82" in result["context_text"]
    assert result["context_fingerprint"]


def test_context_is_bounded_and_fingerprint_changes_with_context():
    long_evidence = "x" * 5000
    one = build_context({"role": "Engineer"}, {"nodes": [{"skill": "python", "state": "evidenced", "evidence": long_evidence}]}, max_chars=2500)
    two = build_context({"role": "Engineer", "skill_gaps": ["sql"]}, {"nodes": [{"skill": "python", "state": "evidenced", "evidence": long_evidence}]}, max_chars=2500)
    assert len(one["context_text"]) <= 2500
    assert one["context_fingerprint"] != two["context_fingerprint"]
