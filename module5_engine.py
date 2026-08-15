"""Module 5: advisory readiness and career roadmap engine.

This compatibility engine intentionally exposes preparation evidence only.
It must never produce hiring, rejection, ranking, or employment-decision outputs.
"""
from typing import Dict, Any

WEIGHTS = {
    "Module 1": 0.20,
    "Module 2": 0.20,
    "Module 3": 0.25,
    "Module 4": 0.15,
    "Module 5": 0.20,
}


def clamp(x):
    return max(0.0, min(100.0, float(x)))


def evaluate(scores: Dict[str, float] | None = None) -> Dict[str, Any]:
    """Return preparation evidence without an employment decision."""
    scores = scores or {
        "Module 1": 92,
        "Module 2": 84,
        "Module 3": 91,
        "Module 4": 87,
        "Module 5": 88,
    }
    scores = {k: clamp(scores.get(k, 0)) for k in WEIGHTS}
    weighted = round(sum(scores[k] * WEIGHTS[k] for k in WEIGHTS), 1)
    strengths = [k for k, v in scores.items() if v >= 85]
    gaps = [k for k, v in scores.items() if v < 75]
    actions = [
        {"module": k, "action": f"Improve {k} performance using targeted practice and review."}
        for k, v in scores.items() if v < 80
    ]
    if not actions:
        actions = [{"module": "Readiness", "action": "Maintain strengths and run a role-specific full simulation."}]
    return {
        "module_scores": scores,
        "weighted_score": weighted,
        "strengths": strengths,
        "skill_gaps": gaps,
        "next_actions": actions,
        "roadmap": [
            {"phase": "Now", "focus": actions[0]["action"]},
            {"phase": "Next 30 days", "focus": "Complete targeted practice and strengthen role-specific evidence."},
            {"phase": "Interview ready", "focus": "Run a complete IntelliHire simulation and review all module reports."},
        ],
        "integrity": {
            "employment_decision_support_only": True,
            "autonomous_hiring_decision": False,
            "ranking_or_rejection": False,
        },
    }
