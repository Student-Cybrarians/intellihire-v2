"""Deterministic Career Digital Twin foundation.

Builds an evidence-based skill graph from a candidate resume and target JD.
It never invents candidate experience: inferred/required skills are explicitly
separated from evidenced skills. The result is suitable for persistence and
later AI/RAG enrichment.
"""
import re
from collections import Counter

SKILL_ALIASES = {
    "python": ["python"], "javascript": ["javascript", "js"], "typescript": ["typescript", "ts"],
    "react": ["react", "react.js"], "node.js": ["node.js", "nodejs", "node"], "java": ["java"],
    "sql": ["sql"], "postgresql": ["postgresql", "postgres"], "mongodb": ["mongodb", "mongo"],
    "docker": ["docker"], "kubernetes": ["kubernetes", "k8s"], "aws": ["aws", "amazon web services"],
    "azure": ["azure"], "gcp": ["gcp", "google cloud"], "git": ["git", "github"],
    "linux": ["linux"], "flask": ["flask"], "fastapi": ["fastapi"], "django": ["django"],
    "pandas": ["pandas"], "numpy": ["numpy"], "scikit-learn": ["scikit-learn", "sklearn"],
    "pytorch": ["pytorch"], "tensorflow": ["tensorflow"], "machine learning": ["machine learning", "ml"],
    "deep learning": ["deep learning"], "nlp": ["nlp", "natural language processing"],
    "rest api": ["rest api", "restful api"], "graphql": ["graphql"], "system design": ["system design"],
    "microservices": ["microservices", "microservice"], "ci/cd": ["ci/cd", "continuous integration", "continuous deployment"],
    "terraform": ["terraform"], "redis": ["redis"], "rabbitmq": ["rabbitmq"],
}

def _tokens(text):
    return re.findall(r"[a-z0-9+#./-]+", str(text or "").lower())

def extract_skills(text):
    normalized = " ".join(_tokens(text))
    found = []
    for canonical, aliases in SKILL_ALIASES.items():
        if any(re.search(r"(?<![a-z0-9])" + re.escape(alias) + r"(?![a-z0-9])", normalized) for alias in aliases):
            found.append(canonical)
    return sorted(found)

def evidence_for_skill(skill, resume):
    text = str(resume or "")
    low = text.lower()
    aliases = SKILL_ALIASES.get(skill, [skill])
    for alias in aliases:
        match = re.search(r".{0,90}" + re.escape(alias) + r".{0,90}", low, re.I)
        if match:
            return match.group(0).strip()
    return ""

def build_career_twin(resume, jd, role=""):
    resume_text = str(resume or "")
    jd_text = str(jd or "")
    evidenced = extract_skills(resume_text)
    required = extract_skills(jd_text)
    evidenced_set, required_set = set(evidenced), set(required)
    matched = sorted(evidenced_set & required_set)
    gaps = sorted(required_set - evidenced_set)
    adjacent = sorted((evidenced_set - required_set))
    graph = []
    for skill in matched:
        graph.append({"skill": skill, "state": "evidenced", "priority": "maintain", "evidence": evidence_for_skill(skill, resume_text)})
    for skill in gaps:
        graph.append({"skill": skill, "state": "gap", "priority": "high", "evidence": ""})
    for skill in adjacent:
        graph.append({"skill": skill, "state": "transferable", "priority": "medium", "evidence": evidence_for_skill(skill, resume_text)})
    total = len(required_set)
    match_score = round((len(matched) / total) * 100, 1) if total else 0.0
    return {
        "role": role,
        "evidenced_skills": sorted(evidenced),
        "required_skills": sorted(required),
        "matched_skills": matched,
        "skill_gaps": gaps,
        "transferable_skills": adjacent,
        "match_score": match_score,
        "skill_graph": graph,
        "integrity": {"fabrication": False, "missing_skills_are_claimed": False},
    }

def build_roadmap(twin, weeks=8):
    gaps = list(twin.get("skill_gaps", []))
    weeks = max(1, min(int(weeks), 24))
    plan = []
    for index, skill in enumerate(gaps[:weeks]):
        plan.append({"week": index + 1, "skill": skill, "objective": f"Build demonstrable {skill} competency", "evidence": f"Create one verifiable project artifact using {skill}", "status": "planned"})
    if not plan:
        plan.append({"week": 1, "skill": "validation", "objective": "Validate target-role readiness", "evidence": "Complete one role-specific project and assessment", "status": "planned"})
    return plan
