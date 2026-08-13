import re
from collections import Counter
from math import sqrt

SKILLS = [
    "python","java","javascript","typescript","react","node.js","sql","postgresql","mongodb",
    "machine learning","deep learning","nlp","computer vision","tensorflow","pytorch","scikit-learn",
    "pandas","numpy","flask","django","fastapi","docker","kubernetes","aws","azure","gcp",
    "git","linux","rest api","data analysis","statistics","power bi","tableau"
]

DEMO = [
 {"id":"IH-1042","name":"Aarav Sharma","role":"ML Engineer","skills":["Python","PyTorch","NLP","FastAPI"],"experience":3.8,"education":"B.Tech Computer Science","location":"Bengaluru","availability":"Immediate"},
 {"id":"IH-1098","name":"Meera Nair","role":"Data Scientist","skills":["Python","Scikit-learn","Pandas","Statistics"],"experience":4.5,"education":"M.Tech Data Science","location":"Bengaluru","availability":"15 days"},
 {"id":"IH-1134","name":"Rohan Verma","role":"AI Engineer","skills":["Python","TensorFlow","Computer Vision","Docker"],"experience":5.2,"education":"B.E. Information Science","location":"Hyderabad","availability":"Immediate"},
 {"id":"IH-1181","name":"Ishita Rao","role":"Software Engineer","skills":["Python","React","Node.js","SQL"],"experience":2.9,"education":"B.Tech IT","location":"Pune","availability":"30 days"},
 {"id":"IH-1207","name":"Kabir Singh","role":"ML Engineer","skills":["Python","PyTorch","Docker","Kubernetes"],"experience":6.1,"education":"M.S. AI","location":"Mumbai","availability":"15 days"}
]

def _tokens(text):
    return set(re.findall(r"[a-zA-Z][a-zA-Z0-9+#.-]*", (text or "").lower()))

def _tfidf_similarity(a, b):
    ta, tb = _tokens(a), _tokens(b)
    if not ta or not tb: return 0.0
    inter = len(ta & tb)
    return inter / sqrt(len(ta) * len(tb))

def extract_skills(text):
    lower = (text or "").lower()
    return [s for s in SKILLS if s in lower]

def analyze_resume(text):
    skills = extract_skills(text)
    tokens = _tokens(text)
    sections = {"contact": bool(re.search(r"@|\+?\d[\d ()-]{7,}", text or "")),
                "experience": bool(re.search(r"experience|employment|worked|engineer|developer", (text or "").lower())),
                "education": bool(re.search(r"education|b.tech|bachelor|master|degree|university", (text or "").lower()))}
    return {"skills": skills, "skill_count": len(skills), "word_count": len(tokens), "sections": sections,
            "score": round(min(100, 35 + len(skills)*4 + sum(sections.values())*8), 1)}

def rank_candidates(job, candidates):
    required = extract_skills(job)
    out = []
    for c in candidates:
        cskills = {s.lower() for s in c.get("skills", [])}
        matches = sorted(cskills & set(required))
        skill_score = (len(matches) / max(1, len(required))) * 70
        exp = min(15, float(c.get("experience", 0)) * 2.5)
        semantic = _tfidf_similarity(job, " ".join(c.get("skills", [])) + " " + c.get("role", "")) * 15
        score = round(min(99.9, skill_score + exp + semantic), 1)
        out.append({**c, "match_score": score, "matched_skills": matches, "reason": f"{len(matches)}/{len(required) or 1} required skills matched; {c.get('experience',0)} years experience."})
    return sorted(out, key=lambda x: x["match_score"], reverse=True)

def demo_candidates(): return DEMO
