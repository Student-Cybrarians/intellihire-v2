from __future__ import annotations

from typing import Any, Dict


def build_context(*, user_profile=None, career_goal=None, target_role=None, target_company=None,
                  resume=None, job_description=None, skill_profile=None, skill_evidence=None,
                  assessment_history=None, technical_interview_history=None, hr_interview_history=None,
                  projects=None, learning_history=None, roadmap=None, research=None, activity=None) -> Dict[str, Any]:
    """Return a bounded, feature-ready context object; never dump the whole database."""
    return {
        "user_profile": user_profile or {},
        "career_goal": career_goal or "",
        "target_role": target_role or "",
        "target_company": target_company or "",
        "resume": str(resume or "")[:18000],
        "job_description": str(job_description or "")[:14000],
        "skill_profile": skill_profile or {},
        "skill_evidence": (skill_evidence or [])[:30],
        "assessment_history": (assessment_history or [])[-10:],
        "technical_interview_history": (technical_interview_history or [])[-8:],
        "hr_interview_history": (hr_interview_history or [])[-8:],
        "projects": (projects or [])[:20],
        "learning_history": (learning_history or [])[-20:],
        "roadmap": roadmap or {},
        "research": research or {},
        "recent_activity": (activity or [])[-20:],
    }
