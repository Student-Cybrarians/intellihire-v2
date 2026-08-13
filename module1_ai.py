import csv
import io
import json
import os
import re
from typing import Any, Dict, List

import requests

SKILL_ALIASES = {
    "javascript": ["javascript", "js"], "typescript": ["typescript", "ts"],
    "node.js": ["node.js", "nodejs", "node"], "react": ["react", "react.js"],
    "rest api": ["rest api", "restful", "rest services"], "postgresql": ["postgresql", "postgres"],
    "machine learning": ["machine learning", "ml"], "deep learning": ["deep learning"],
    "scikit-learn": ["scikit-learn", "sklearn"], "power bi": ["power bi", "powerbi"],
    "ci/cd": ["ci/cd", "cicd", "continuous integration", "continuous delivery"],
}
COMMON_SKILLS = [
    "python", "java", "javascript", "typescript", "react", "node.js", "sql", "postgresql", "mongodb",
    "rest api", "docker", "kubernetes", "aws", "azure", "gcp", "fastapi", "flask", "django",
    "pytorch", "tensorflow", "nlp", "machine learning", "deep learning", "scikit-learn", "pandas", "numpy",
    "system design", "microservices", "git", "linux", "data analysis", "statistics", "power bi", "tableau",
    "ci/cd", "terraform", "redis", "graphql", "spark", "airflow", "kafka", "computer vision",
]


def _tokens(text: str) -> List[str]:
    return re.findall(r"[a-z0-9+#./-]+", (text or "").lower())


def extract_skills(text: str) -> List[str]:
    lower = (text or "").lower()
    found = []
    for skill in COMMON_SKILLS:
        aliases = SKILL_ALIASES.get(skill, [skill])
        if any(re.search(r"(?<![a-z0-9])" + re.escape(a) + r"(?![a-z0-9])", lower) for a in aliases):
            found.append(skill)
    return found


def _chat(endpoint: str, api_key: str, model: str, system: str, user: str, timeout: int = 45) -> str:
    r = requests.post(endpoint, headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}, json={
        "model": model,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "temperature": 0.15,
        "max_tokens": 5000,
        "stream": False,
    }, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    return data["choices"][0]["message"]["content"]


def _extract_json(text: str) -> Dict[str, Any]:
    cleaned = (text or "").strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.I)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, re.S)
        if match:
            return json.loads(match.group(0))
        raise


def _deterministic_metrics(resume: str, jd: str) -> Dict[str, Any]:
    rs = set(extract_skills(resume)); js = set(extract_skills(jd))
    matched = sorted(rs & js); missing = sorted(js - rs)
    skill_score = round(100 * len(matched) / max(1, len(js)))
    rt, jt = set(_tokens(resume)), set(_tokens(jd))
    keyword = round(100 * len(rt & jt) / max(1, len(jt)))
    sections = {
        "contact": bool(re.search(r"@|\+?\d[\d ()-]{7,}", resume or "")),
        "summary": bool(re.search(r"summary|profile|objective", resume or "", re.I)),
        "experience": bool(re.search(r"experience|employment|worked", resume or "", re.I)),
        "education": bool(re.search(r"education|degree|university|college|b.tech|bachelor|master", resume or "", re.I)),
        "skills": bool(re.search(r"skills|technologies|technical skills", resume or "", re.I)),
    }
    ats = round(0.55 * skill_score + 0.25 * keyword + 20 * sum(sections.values()) / len(sections))
    return {"matched_skills": matched, "missing_skills": missing, "skill_match": skill_score, "keyword_match": keyword, "ats_baseline": min(100, ats), "sections": sections}


def analyze_with_ai(resume_text: str, jd_text: str, company: str = "", role: str = "") -> Dict[str, Any]:
    metrics = _deterministic_metrics(resume_text, jd_text)
    system = """You are IntelliHire's senior ATS/recruitment intelligence engine. Analyze a candidate resume strictly against the supplied job description and target role. Never invent candidate experience, education, employment, projects, certificates, metrics, employers, or skills. You may recommend skills/certifications as learning targets, but label them as recommendations. Return ONLY valid JSON with these keys: candidate, job, ats_score, overall_match, keyword_match, semantic_match, skills_match, matched_skills, missing_skills, strengths, risks, recommendations, recruiter_feedback, learning_plan, recommended_certifications, tailored_resume. tailored_resume must contain name, headline, summary, skills, experience, education, projects, certifications, keywords. Preserve factual candidate content and mark any suggested additions as [VERIFY]."""
    prompt = f"""TARGET COMPANY: {company}\nTARGET ROLE: {role}\n\nJOB DESCRIPTION:\n{jd_text[:18000]}\n\nCANDIDATE RESUME:\n{resume_text[:22000]}\n\nDeterministic baseline metrics for cross-checking: {json.dumps(metrics)}\nProvide a rigorous, evidence-based ATS analysis and a tailored ATS-friendly resume. Match the JD's responsibilities and skills. Explain gaps and give an actionable preparation plan. Do not claim a certification is required unless the JD explicitly requires it."""

    providers = []
    if os.getenv("OPENAI_API_KEY"):
        providers.append((os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1/chat/completions"), os.getenv("OPENAI_MODEL", "gpt-5-mini"), os.getenv("OPENAI_API_KEY"), "openai"))
    if os.getenv("NVIDIA_API_KEY"):
        providers.append((os.getenv("NVIDIA_API_URL", "https://integrate.api.nvidia.com/v1/chat/completions"), os.getenv("NVIDIA_MODEL", "nvidia/nemotron-3-nano-30b-a3b"), os.getenv("NVIDIA_API_KEY"), "nvidia"))

    last_error = None
    for endpoint, model, key, provider in providers:
        try:
            raw = _chat(endpoint, key, model, system, prompt)
            data = _extract_json(raw)
            data["provider"] = provider
            data["model"] = model
            data["is_ai"] = True
            data["baseline"] = metrics
            return _normalize(data, metrics, company, role)
        except Exception as exc:
            last_error = str(exc)

    # A deterministic result is retained only as a controlled degraded mode.
    return _fallback(metrics, company, role, last_error)


def _normalize(data: Dict[str, Any], metrics: Dict[str, Any], company: str, role: str) -> Dict[str, Any]:
    data["ats_score"] = max(0, min(100, int(float(data.get("ats_score", metrics["ats_baseline"])))) )
    data["overall_match"] = max(0, min(100, int(float(data.get("overall_match", data["ats_score"])))) )
    data["keyword_match"] = max(0, min(100, int(float(data.get("keyword_match", metrics["keyword_match"])))) )
    data["semantic_match"] = max(0, min(100, int(float(data.get("semantic_match", data["ats_score"])))) )
    data["skills_match"] = max(0, min(100, int(float(data.get("skills_match", metrics["skill_match"])))) )
    data["matched_skills"] = data.get("matched_skills") or metrics["matched_skills"]
    data["missing_skills"] = data.get("missing_skills") or metrics["missing_skills"]
    data["recommended_certifications"] = data.get("recommended_certifications") or []
    data["learning_plan"] = data.get("learning_plan") or []
    data["recommendations"] = data.get("recommendations") or []
    data["company"] = company; data["role"] = role
    data["shortlist"] = "SHORTLISTED" if data["ats_score"] >= 80 else ("CONSIDER" if data["ats_score"] >= 60 else "NEEDS_IMPROVEMENT")
    data["feedback"] = data.get("recruiter_feedback", "")
    return data


def _fallback(metrics: Dict[str, Any], company: str, role: str, error: str = None) -> Dict[str, Any]:
    return {"provider": "deterministic-fallback", "model": None, "is_ai": False, "ai_error": error,
            "ats_score": metrics["ats_baseline"], "overall_match": round((metrics["skill_match"] + metrics["keyword_match"] + metrics["ats_baseline"]) / 3),
            "keyword_match": metrics["keyword_match"], "semantic_match": metrics["keyword_match"], "skills_match": metrics["skill_match"],
            "matched_skills": metrics["matched_skills"], "missing_skills": metrics["missing_skills"], "strengths": metrics["matched_skills"],
            "risks": metrics["missing_skills"], "recommendations": [f"Build evidence for: {x}" for x in metrics["missing_skills"]],
            "recruiter_feedback": "AI provider unavailable; deterministic ATS analysis was used.", "feedback": "AI provider unavailable; deterministic ATS analysis was used.",
            "learning_plan": [f"Learn and demonstrate {x}" for x in metrics["missing_skills"]], "recommended_certifications": [],
            "tailored_resume": {"name": "Candidate", "headline": role or "Target Role", "summary": "Tailor this summary after reviewing the evidence gaps.", "skills": metrics["matched_skills"], "experience": [], "education": [], "projects": [], "certifications": [], "keywords": metrics["matched_skills"]},
            "company": company, "role": role, "shortlist": "SHORTLISTED" if metrics["ats_baseline"] >= 80 else "CONSIDER"}


def resume_docx_bytes(resume: Dict[str, Any]) -> bytes:
    from docx import Document
    d = Document(); d.add_heading(resume.get("name", "Candidate"), 0); d.add_paragraph(resume.get("headline", "")); d.add_heading("Professional Summary", level=1); d.add_paragraph(resume.get("summary", ""))
    for title, key in [("Skills", "skills"), ("Experience", "experience"), ("Education", "education"), ("Projects", "projects"), ("Certifications", "certifications")]:
        d.add_heading(title, level=1)
        values = resume.get(key, [])
        if isinstance(values, str): values = [values]
        for value in values: d.add_paragraph(str(value), style="List Bullet")
    return _save_docx(d)


def _save_docx(doc) -> bytes:
    out = io.BytesIO(); doc.save(out); return out.getvalue()


def resume_pdf_bytes(resume: Dict[str, Any]) -> bytes:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    out = io.BytesIO(); doc = SimpleDocTemplate(out, pagesize=A4, rightMargin=42, leftMargin=42, topMargin=42, bottomMargin=42); styles = getSampleStyleSheet(); story = [Paragraph(str(resume.get("name", "Candidate")), styles["Title"]), Paragraph(str(resume.get("headline", "")), styles["Heading2"])]
    for title, key in [("Professional Summary", "summary"), ("Skills", "skills"), ("Experience", "experience"), ("Education", "education"), ("Projects", "projects"), ("Certifications", "certifications")]:
        story += [Spacer(1, 8), Paragraph(title, styles["Heading2"])]
        values = resume.get(key, []); values = [values] if isinstance(values, str) else values
        for value in values: story.append(Paragraph(str(value).replace("&", "&amp;"), styles["BodyText"]))
    doc.build(story); return out.getvalue()


def resume_csv_bytes(resume: Dict[str, Any]) -> bytes:
    out = io.StringIO(); w = csv.writer(out); w.writerow(["section", "content"])
    for key, value in resume.items():
        values = value if isinstance(value, list) else [value]
        for item in values: w.writerow([key, item])
    return out.getvalue().encode("utf-8-sig")
