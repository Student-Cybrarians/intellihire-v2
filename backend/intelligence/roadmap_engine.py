"""Production roadmap and project generator.

Builds bounded, evidence-linked milestones from a persisted Career Twin and research
brief. It never upgrades a skill gap into claimed candidate experience.
"""
from __future__ import annotations
import hashlib
import re


def _slug(value):
    return re.sub(r"[^a-z0-9]+", "-", str(value or "").lower()).strip("-") or "skill"


def _project_for(skill, role, evidence):
    slug = _slug(skill)
    role_text = role or "target role"
    return {
        "id": f"project-{slug}",
        "title": f"{skill.title()} role-readiness project",
        "objective": f"Demonstrate practical {skill} capability relevant to {role_text}.",
        "deliverables": [
            f"Working implementation using {skill}",
            "README with architecture and trade-offs",
            "Automated tests and reproducible run instructions",
        ],
        "acceptance_criteria": [
            "Implementation runs from a clean environment",
            "Tests cover the primary workflow",
            "README explains design decisions and limitations",
        ],
        "evidence_required": evidence or f"Produce verifiable artifact demonstrating {skill}.",
        "status": "planned",
    }


def generate_roadmap(twin, research=None, weeks=8):
    if not isinstance(twin, dict):
        raise ValueError("career_twin_required")
    weeks = max(1, min(int(weeks), 24))
    gaps = [str(x).strip() for x in twin.get("skill_gaps", []) if str(x).strip()]
    role = str(twin.get("role", "")).strip()
    research = research if isinstance(research, dict) else {}
    sources = research.get("sources", []) if isinstance(research.get("sources", []), list) else []
    source_urls = [str(s.get("url", "")) for s in sources if isinstance(s, dict) and str(s.get("url", "")).startswith(("http://", "https://"))]
    milestones = []
    for index, skill in enumerate(gaps[:weeks]):
        graph_item = next((x for x in twin.get("skill_graph", []) if isinstance(x, dict) and x.get("skill") == skill), {})
        milestones.append({
            "week": index + 1,
            "skill": skill,
            "state": "gap",
            "objective": f"Build demonstrable {skill} competency for {role or 'the target role'}",
            "project": _project_for(skill, role, graph_item.get("evidence", "")),
            "research_sources": source_urls[:4],
            "status": "planned",
        })
    if not milestones:
        milestones.append({
            "week": 1,
            "skill": "validation",
            "state": "validation",
            "objective": "Validate target-role readiness with one verifiable artifact and assessment.",
            "project": _project_for("validation", role, "Complete and review a role-specific artifact."),
            "research_sources": source_urls[:4],
            "status": "planned",
        })
    fingerprint = hashlib.sha256(repr([(m["week"], m["skill"]) for m in milestones]).encode()).hexdigest()[:16]
    return {
        "role": role,
        "weeks": weeks,
        "milestones": milestones,
        "source_urls": source_urls[:10],
        "integrity": {"fabricated_candidate_experience": False, "fabricated_sources": False},
        "plan_fingerprint": fingerprint,
    }
