from career_intelligence import build_career_twin
from research_context import build_context
from roadmap_engine import generate_roadmap
from module5_readiness import build_readiness


def test_career_twin_to_research_to_roadmap_to_readiness_pipeline():
    resume = "Python Flask REST API Git Docker experience building production services."
    job_description = "Software Engineer requiring Python Flask Docker Kubernetes and system design."

    twin = build_career_twin(resume, job_description, "Software Engineer")
    assert "python" in twin["matched_skills"]
    assert "kubernetes" in twin["skill_gaps"]
    assert twin["integrity"]["fabrication"] is False

    graph = {
        "nodes": twin["skill_graph"],
        "role": twin["role"],
    }
    behavioral = {
        "competencies": {
            "Communication": {"score": 84, "confidence": 0.8, "evidence_count": 3},
        }
    }
    context = build_context(twin, graph, behavioral, {"milestones": []})
    assert context["context"]["skill_gaps"] == ["kubernetes", "system design"]
    assert any(node["state"] == "evidenced" for node in context["context"]["skill_graph"])
    assert any(node["state"] == "gap" for node in context["context"]["skill_graph"])
    assert context["context_fingerprint"]

    research = {
        "sources": [
            {
                "url": "https://example.com/kubernetes",
                "title": "Kubernetes guide",
                "snippet": "Deployment and service fundamentals",
            }
        ]
    }
    roadmap = generate_roadmap(twin, research, weeks=4)
    assert roadmap["milestones"]
    assert roadmap["milestones"][0]["state"] == "gap"
    assert roadmap["source_urls"] == ["https://example.com/kubernetes"]
    assert roadmap["integrity"]["fabricated_candidate_experience"] is False

    readiness = build_readiness(
        {
            "Module 1": {"score": 82},
            "Module 2": {"score": 78},
            "Module 3": {"score": 88},
            "Module 4": {"score": 84},
        },
        twin,
        research,
        roadmap,
        behavioral,
    )
    assert 0 <= readiness["weighted_score"] <= 100
    assert readiness["research_evidence_count"] == 1
    assert readiness["skill_coverage"] < 100
    assert readiness["integrity"]["employment_decision_support_only"] is True
    assert readiness["integrity"]["autonomous_hiring_decision"] is False


def test_pipeline_never_turns_skill_gaps_into_candidate_evidence():
    twin = build_career_twin(
        "Python developer building APIs.",
        "Software Engineer requiring Python and Kubernetes.",
        "Software Engineer",
    )
    gap = next(item for item in twin["skill_graph"] if item["skill"] == "kubernetes")
    assert gap["state"] == "gap"
    assert gap["evidence"] == ""

    context = build_context(twin, {"nodes": twin["skill_graph"]})
    gap_context = next(item for item in context["context"]["skill_graph"] if item["skill"] == "kubernetes")
    assert gap_context["state"] == "gap"
    assert gap_context["evidence"] == ""
