"""Module 5: hiring committee, readiness, and career roadmap engine."""
from math import exp
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
    scores = scores or {
        "Module 1": 92,
        "Module 2": 84,
        "Module 3": 91,
        "Module 4": 87,
        "Module 5": 88,
    }

    scores = {k: clamp(scores.get(k, 0)) for k in WEIGHTS}

    weighted = round(
        sum(scores[k] * WEIGHTS[k] for k in WEIGHTS),
        1,
    )

    probability = round(
        100 / (1 + exp(-(weighted - 72) / 8)),
        1,
    )

    if probability >= 80:
        decision = "Strong Hire"
    elif probability >= 65:
        decision = "Hire"
    elif probability >= 50:
        decision = "Consider"
    else:
        decision = "No Hire"

    strengths = [
        k for k, v in scores.items()
        if v >= 85
    ]

    gaps = [
        k for k, v in scores.items()
        if v < 75
    ]

    actions = []

    for k, v in scores.items():
        if v < 80:
            actions.append({
                "module": k,
                "action": (
                    f"Improve {k} performance using "
                    "targeted practice and review."
                ),
            })

    if not actions:
        actions = [{
            "module": "Readiness",
            "action": (
                "Maintain strengths and run a "
                "role-specific full simulation."
            ),
        }]

    return {
        "module_scores": scores,
        "weighted_score": weighted,
        "hiring_probability": probability,
        "decision": decision,
        "strengths": strengths,
        "skill_gaps": gaps,
        "next_actions": actions,
        "roadmap": [
            {
                "phase": "Now",
                "focus": actions[0]["action"],
            },
            {
                "phase": "Next 30 days",
                "focus": (
                    "Complete targeted practice and "
                    "strengthen role-specific evidence."
                ),
            },
            {
                "phase": "Interview ready",
                "focus": (
                    "Run a complete IntelliHire simulation "
                    "and review all module reports."
                ),
            },
        ],
    }
