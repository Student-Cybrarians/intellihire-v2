"""Deterministic behavioral competency aggregation for Module 4.

Turns persisted interview events into bounded, evidence-backed competency
signals. It never treats an inferred gap as candidate evidence.
"""
from statistics import mean

COMPETENCIES = ("communication", "ownership", "teamwork", "prioritization", "growth")
QUESTION_TO_COMPETENCY = {
    "hr-01": "communication",
    "hr-02": "ownership",
    "hr-03": "teamwork",
    "hr-04": "prioritization",
    "hr-05": "growth",
}

def _clamp(value):
    return round(max(0.0, min(100.0, float(value))), 1)

def _event_score(event):
    metrics = event.get("metrics") or {}
    values = [metrics.get(k) for k in ("communication", "confidence", "clarity", "relevance", "star_score")]
    values = [float(v) for v in values if isinstance(v, (int, float))]
    return _clamp(mean(values)) if values else 0.0

def aggregate(events):
    evidence = {key: [] for key in COMPETENCIES}
    for event in events or []:
        question = event.get("question") or {}
        competency = QUESTION_TO_COMPETENCY.get(question.get("id"))
        if not competency:
            continue
        metrics = event.get("metrics") or {}
        evidence[competency].append({
            "question_id": question.get("id"),
            "score": _event_score(event),
            "star_score": _clamp(metrics.get("star_score", 0)),
            "communication": _clamp(metrics.get("communication", 0)),
            "feedback": list(metrics.get("feedback") or [])[:3],
        })
    dimensions = {}
    for competency in COMPETENCIES:
        rows = evidence[competency]
        score = _clamp(mean([r["score"] for r in rows])) if rows else 0.0
        dimensions[competency] = {
            "score": score,
            "evidence_count": len(rows),
            "confidence": _clamp(min(100, len(rows) * 50)),
            "status": "evidenced" if rows else "insufficient_evidence",
        }
    strengths = [k for k, v in dimensions.items() if v["evidence_count"] and v["score"] >= 80]
    gaps = [k for k, v in dimensions.items() if v["evidence_count"] and v["score"] < 70]
    return {
        "dimensions": dimensions,
        "strengths": strengths,
        "development_areas": gaps,
        "evidence": evidence,
        "integrity": {"candidate_evidence_only": True, "fabrication": False},
    }
