import re
from collections import Counter
from math import sqrt
from typing import Dict, Iterable, List

SKILL_ALIASES = {
    "javascript": ["javascript", "js", "ecmascript"],
    "typescript": ["typescript", "ts"],
    "node.js": ["node.js", "nodejs", "node"],
    "react": ["react", "react.js", "reactjs"],
    "rest api": ["rest api", "restful", "rest services"],
    "postgresql": ["postgresql", "postgres"],
    "machine learning": ["machine learning", "ml"],
    "deep learning": ["deep learning", "dl"],
    "scikit-learn": ["scikit-learn", "sklearn"],
    "power bi": ["power bi", "powerbi"],
}

SKILLS = [
    "python", "java", "javascript", "typescript", "react", "node.js", "sql", "postgresql", "mongodb",
    "machine learning", "deep learning", "nlp", "computer vision", "tensorflow", "pytorch", "scikit-learn",
    "pandas", "numpy", "flask", "django", "fastapi", "docker", "kubernetes", "aws", "azure", "gcp",
    "git", "linux", "rest api", "data analysis", "statistics", "power bi", "tableau", "system design",
    "microservices", "redis", "graphql", "spark", "airflow", "kafka", "terraform", "ci/cd"
]

SKILL_GRAPH = {
    "backend engineer": ["python", "java", "rest api", "sql", "postgresql", "docker", "system design"],
    "ml engineer": ["python", "machine learning", "pytorch", "tensorflow", "scikit-learn", "docker", "mlops"],
    "data scientist": ["python", "pandas", "numpy", "statistics", "machine learning", "scikit-learn", "sql"],
    "frontend engineer": ["javascript", "typescript", "react", "git", "rest api"],
}

DEMO = [
    {"id": "IH-1042", "name": "Aarav Sharma", "role": "ML Engineer", "skills": ["Python", "PyTorch", "NLP", "FastAPI"], "experience": 3.8, "education": "B.Tech Computer Science", "location": "Bengaluru", "availability": "Immediate"},
    {"id": "IH-1098", "name": "Meera Nair", "role": "Data Scientist", "skills": ["Python", "Scikit-learn", "Pandas", "Statistics"], "experience": 4.5, "education": "M.Tech Data Science", "location": "Bengaluru", "availability": "15 days"},
    {"id": "IH-1134", "name": "Rohan Verma", "role": "AI Engineer", "skills": ["Python", "TensorFlow", "Computer Vision", "Docker"], "experience": 5.2, "education": "B.E. Information Science", "location": "Hyderabad", "availability": "Immediate"},
    {"id": "IH-1181", "name": "Ishita Rao", "role": "Software Engineer", "skills": ["Python", "React", "Node.js", "SQL"], "experience": 2.9, "education": "B.Tech IT", "location": "Pune", "availability": "30 days"},
    {"id": "IH-1207", "name": "Kabir Singh", "role": "ML Engineer", "skills": ["Python", "PyTorch", "Docker", "Kubernetes"], "experience": 6.1, "education": "M.S. AI", "location": "Mumbai", "availability": "15 days"},
]


def _tokens(text: str) -> set:
    return set(re.findall(r"[a-zA-Z][a-zA-Z0-9+#./-]*", (text or "").lower()))


def normalize_skill(skill: str) -> str:
    value = re.sub(r"\s+", " ", (skill or "").strip().lower())
    for canonical, aliases in SKILL_ALIASES.items():
        if value in aliases:
            return canonical
    return value


def extract_skills(text: str) -> List[str]:
    lower = (text or "").lower()
    found = []
    for skill in SKILLS:
        aliases = SKILL_ALIASES.get(skill, [skill])
        if any(re.search(r"(?<![a-z0-9])" + re.escape(alias) + r"(?![a-z0-9])", lower) for alias in aliases):
            found.append(skill)
    return sorted(set(found))


def _tfidf_similarity(a: str, b: str) -> float:
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        matrix = TfidfVectorizer(ngram_range=(1, 2), min_df=1).fit_transform([a or "", b or ""])
        return float(cosine_similarity(matrix[0:1], matrix[1:2])[0][0])
    except Exception:
        ta, tb = _tokens(a), _tokens(b)
        if not ta or not tb:
            return 0.0
        return len(ta & tb) / sqrt(len(ta) * len(tb))


def bm25_score(query: str, document: str, k1: float = 1.5, b: float = 0.75) -> float:
    q = _tokens(query)
    d = _tokens(document)
    if not q or not d:
        return 0.0
    counts = Counter(d)
    avgdl = max(1.0, len(d))
    score = 0.0
    for term in q:
        tf = counts.get(term, 0)
        if not tf:
            continue
        idf = 1.0
        denom = tf + k1 * (1 - b + b * len(d) / avgdl)
        score += idf * ((tf * (k1 + 1)) / denom)
    return score


def analyze_resume(text: str) -> Dict:
    skills = extract_skills(text)
    tokens = _tokens(text)
    sections = {
        "contact": bool(re.search(r"@|\+?\d[\d ()-]{7,}", text or "")),
        "summary": bool(re.search(r"summary|profile|objective", text or "", re.I)),
        "experience": bool(re.search(r"experience|employment|worked|engineer|developer", text or "", re.I)),
        "education": bool(re.search(r"education|b.tech|bachelor|master|degree|university", text or "", re.I)),
        "skills": bool(re.search(r"skills|technologies|technical skills", text or "", re.I)),
    }
    return {
        "skills": skills,
        "skill_count": len(skills),
        "word_count": len(tokens),
        "sections": sections,
        "score": round(min(100, 30 + len(skills) * 4 + sum(sections.values()) * 8), 1),
    }


def match_resume_to_job(resume: str, job: str) -> Dict:
    resume_skills = set(extract_skills(resume))
    job_skills = set(extract_skills(job))
    matched = sorted(resume_skills & job_skills)
    missing = sorted(job_skills - resume_skills)
    skill_match = round(100 * len(matched) / max(1, len(job_skills)))
    semantic = round(_tfidf_similarity(resume, job) * 100)
    lexical = round(100 * len(_tokens(resume) & _tokens(job)) / max(1, len(_tokens(job))))
    bm25 = round(bm25_score(job, resume), 3)
    score = round(0.45 * skill_match + 0.30 * semantic + 0.20 * lexical + 0.05 * min(100, bm25 * 10))
    return {
        "atsScore": min(100, score),
        "skillsMatch": skill_match,
        "semanticSimilarity": semantic,
        "keywordMatch": lexical,
        "matchedSkills": matched,
        "missingSkills": missing,
        "bm25": bm25,
        "method": "skill+TFIDF+BM25",
        "isSimulated": False,
    }


def build_career_context(profile: Dict, performance: Iterable[Dict] = (), goal: str = "") -> Dict:
    profile = profile or {}
    performance = list(performance or [])
    resume = str(profile.get("resume", ""))
    explicit_skills = [normalize_skill(x) for x in (profile.get("skills") or [])]
    resume_skills = extract_skills(resume)
    return {
        "goal": goal or profile.get("target_role") or profile.get("role") or "",
        "profile": {
            "name": profile.get("name", "Candidate"),
            "education": profile.get("education", ""),
            "experience": profile.get("experience", ""),
            "skills": sorted(set(explicit_skills + resume_skills)),
            "projects": profile.get("projects", []),
            "certifications": profile.get("certifications", []),
        },
        "performance": performance,
        "context_policy": "user-provided facts first; recommendations are not candidate claims",
    }


def career_gap_analysis(profile: Dict, target_role: str) -> Dict:
    current = set(normalize_skill(x) for x in (profile.get("skills") or [])) | set(extract_skills(profile.get("resume", "")))
    required = set(SKILL_GRAPH.get((target_role or "").lower(), extract_skills(target_role)))
    missing = sorted(required - current)
    matched = sorted(required & current)
    return {
        "targetRole": target_role,
        "requiredSkills": sorted(required),
        "matchedSkills": matched,
        "missingSkills": missing,
        "coverage": round(100 * len(matched) / max(1, len(required))),
        "priority": [{"skill": s, "priority": "critical" if i < 2 else "high"} for i, s in enumerate(missing)],
    }


def research_plan(profile: Dict, target_role: str) -> Dict:
    gap = career_gap_analysis(profile, target_role)
    actions = []
    for item in gap["priority"]:
        skill = item["skill"]
        actions.append({
            "skill": skill,
            "action": f"Build and document one project demonstrating {skill}.",
            "evidence": f"Portfolio project + interview explanation for {skill}.",
        })
    return {
        "targetRole": target_role,
        "summary": f"Close the highest-priority evidence gaps for {target_role}.",
        "actions": actions,
        "sources": [],
        "sourcePolicy": "External research must attach a real URL and retrieval timestamp.",
    }


def rank_candidates(job, candidates):
    required = set(extract_skills(job))
    out = []
    for candidate in candidates:
        cskills = {normalize_skill(s) for s in candidate.get("skills", [])}
        matches = sorted(cskills & required)
        skill_score = (len(matches) / max(1, len(required))) * 70
        exp = min(15, float(candidate.get("experience", 0)) * 2.5)
        semantic = _tfidf_similarity(job, " ".join(candidate.get("skills", [])) + " " + candidate.get("role", "")) * 15
        score = round(min(99.9, skill_score + exp + semantic), 1)
        out.append({
            **candidate,
            "match_score": score,
            "matched_skills": matches,
            "reason": f"{len(matches)}/{len(required) or 1} required skills matched; {candidate.get('experience', 0)} years experience.",
            "decision": "career-discovery-only",
        })
    return sorted(out, key=lambda x: x["match_score"], reverse=True)


def demo_candidates():
    return DEMO
