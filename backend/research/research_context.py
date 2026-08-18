"""Context engineering for the Personal AI Research Intern.

Builds a bounded, user-scoped research context from persisted Career Twin evidence,
Skill Graph state, behavioral competencies, and roadmap signals. This layer is
structured context, not a claim generator: it preserves evidence state labels and
never turns gaps/inferences into candidate experience.
"""
from __future__ import annotations
import hashlib
import json
import re


def _text(value, limit=600):
    return str(value or "").strip()[:limit]


def _skills(graph):
    nodes = graph.get("nodes", []) if isinstance(graph, dict) else []
    result = []
    for node in nodes if isinstance(nodes, list) else []:
        if not isinstance(node, dict):
            continue
        skill = _text(node.get("skill"), 120).lower()
        state = _text(node.get("state"), 40).lower()
        if skill and state in {"evidenced", "gap", "transferable"}:
            result.append({
                "skill": skill,
                "state": state,
                "priority": _text(node.get("priority", "medium"), 30),
                "evidence": _text(node.get("evidence", ""), 500),
            })
    return sorted(result, key=lambda item: (item["state"], item["skill"]))[:40]


def build_context(twin=None, skill_graph=None, behavioral=None, roadmap=None, max_chars=9000):
    twin = twin if isinstance(twin, dict) else {}
    graph = skill_graph if isinstance(skill_graph, dict) else (twin.get("skill_graph") or {})
    behavioral = behavioral if isinstance(behavioral, dict) else {}
    roadmap = roadmap if isinstance(roadmap, dict) else {}

    context = {
        "version": 1,
        "role": _text(twin.get("role"), 160),
        "required_skills": [str(x).strip().lower() for x in twin.get("required_skills", []) if str(x).strip()][:30],
        "evidenced_skills": [str(x).strip().lower() for x in twin.get("evidenced_skills", []) if str(x).strip()][:30],
        "skill_gaps": [str(x).strip().lower() for x in twin.get("skill_gaps", []) if str(x).strip()][:30],
        "skill_graph": _skills(graph),
        "behavioral_competencies": {},
        "roadmap": [],
        "target": {
            "company": _text(twin.get("company"), 160),
            "role": _text(twin.get("role"), 160),
        },
    }

    competencies = behavioral.get("competencies", behavioral) if isinstance(behavioral, dict) else {}
    if isinstance(competencies, dict):
        for name, value in list(competencies.items())[:12]:
            if not isinstance(value, dict):
                continue
            context["behavioral_competencies"][_text(name, 80)] = {
                "score": value.get("score"),
                "confidence": value.get("confidence"),
                "evidence_count": value.get("evidence_count", value.get("evidenceCount", 0)),
            }

    milestones = roadmap.get("milestones", []) if isinstance(roadmap, dict) else []
    if isinstance(milestones, list):
        for item in milestones[:10]:
            if not isinstance(item, dict):
                continue
            context["roadmap"].append({
                "title": _text(item.get("title"), 160),
                "skill": _text(item.get("skill", item.get("target_skill")), 100).lower(),
                "status": _text(item.get("status", "planned"), 40).lower(),
                "deliverable": _text(item.get("deliverable"), 240),
            })

    encoded = json.dumps(context, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    if len(encoded) > max(1000, int(max_chars)):
        # Preserve graph states and high-value fields first; trim only verbose evidence.
        for node in context["skill_graph"]:
            node["evidence"] = node["evidence"][:180]
        encoded = json.dumps(context, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        if len(encoded) > max(1000, int(max_chars)):
            encoded = encoded[:int(max_chars)]
    return {
        "context": context,
        "context_text": encoded,
        "context_fingerprint": hashlib.sha256(encoded.encode("utf-8")).hexdigest(),
    }
