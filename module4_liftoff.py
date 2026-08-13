"""Liftoff-inspired HR interview intelligence layer for IntelliHire.

Implements browser-recorded interview processing, transcript scoring, STAR analysis,
communication metrics, sentiment heuristics, and optional OpenAI transcription/feedback.
"""
from datetime import datetime, timezone
import os
import re

try:
    import requests
except ImportError:
    requests = None

QUESTIONS = [
    {"id": "hr-01", "category": "Behavioral", "difficulty": "Easy", "prompt": "Tell me about yourself and walk me through the experience that best prepares you for this role."},
    {"id": "hr-02", "category": "Ownership", "difficulty": "Medium", "prompt": "Tell me about a difficult project or responsibility you owned. What happened and what did you learn?"},
    {"id": "hr-03", "category": "Teamwork", "difficulty": "Medium", "prompt": "Describe a disagreement with a teammate or stakeholder and how you resolved it."},
    {"id": "hr-04", "category": "Prioritization", "difficulty": "Hard", "prompt": "Describe a time when several important tasks competed for your attention. How did you decide what to do first?"},
    {"id": "hr-05", "category": "Growth", "difficulty": "Medium", "prompt": "Tell me about a failure or mistake and how it changed the way you work."},
]


def _words(text):
    return re.findall(r"[a-zA-Z']+", (text or "").lower())


def score_transcript(transcript, question):
    words = _words(transcript)
    n = len(words)
    text = " ".join(words)
    has = lambda *terms: any(t in text for t in terms)
    fillers = len(re.findall(r"\b(um|uh|erm|like|you know|basically)\b", transcript or "", re.I))
    star = {
        "situation": int(n >= 25 and has("situation", "context", "project", "team", "when")),
        "task": int(n >= 30 and has("goal", "responsibility", "task", "needed", "asked")),
        "action": int(n >= 35 and has("i led", "i built", "i created", "i implemented", "i resolved", "i designed", "i decided", "i worked")),
        "result": int(n >= 40 and has("result", "impact", "improved", "increased", "reduced", "achieved", "learned", "outcome")),
    }
    relevance_terms = set(_words(question)) & set(words)
    relevance = min(100, 55 + len(relevance_terms) * 5)
    clarity = max(45, min(98, 62 + min(28, n // 7) - fillers * 2))
    confidence = max(40, min(96, 58 + min(32, n // 6) - fillers))
    communication = round((clarity + confidence + relevance) / 3)
    star_score = round(sum(star.values()) / 4 * 100)
    sentiment = "positive" if has("success", "improved", "achieved", "proud", "learned", "great") else ("neutral" if n < 30 else "constructive")
    feedback = []
    if not star["situation"]: feedback.append("Set the context quickly so the interviewer understands the situation.")
    if not star["action"]: feedback.append("Emphasize your personal actions using first-person language and concrete decisions.")
    if not star["result"]: feedback.append("Close with a measurable result, impact, or lesson learned.")
    if fillers >= 4: feedback.append("Reduce filler words and use short pauses instead of verbal fillers.")
    if relevance < 70: feedback.append("Tie the answer more directly to the question before adding background detail.")
    if not feedback: feedback.append("Strong, relevant response with a clear STAR-style structure.")
    return {
        "confidence": confidence, "clarity": clarity, "eye_contact": 0,
        "communication": communication, "relevance": relevance,
        "star_score": star_score, "star": star, "sentiment": sentiment,
        "filler_count": fillers, "word_count": n, "feedback": feedback,
    }


def start(role="Software Engineer", interviewer="AI HR Manager", duration=15):
    return {"id": "int-" + datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f"), "role": role, "interviewer": interviewer, "duration": duration, "question_index": 0, "events": [], "status": "IN_PROGRESS", "created_at": datetime.now(timezone.utc).isoformat()}


def question(state):
    i = state.get("question_index", 0)
    return QUESTIONS[i] if i < len(QUESTIONS) else None


def answer(state, transcript):
    q = question(state)
    if not q: return None
    metrics = score_transcript(transcript, q["prompt"])
    metrics["transcript"] = transcript
    event = {"question": q, "answer": transcript, "metrics": metrics, "timestamp": datetime.now(timezone.utc).isoformat()}
    state.setdefault("events", []).append(event)
    state["question_index"] = state.get("question_index", 0) + 1
    return event


def finish(state):
    events = state.get("events", [])
    state["status"] = "COMPLETED"
    if not events:
        return {"score": 0, "events": [], "status": state["status"]}
    avg = lambda key: round(sum(e["metrics"].get(key, 0) for e in events) / len(events), 1)
    score = round((avg("confidence") + avg("clarity") + avg("communication") + avg("star_score")) / 4, 1)
    return {"score": score, "confidence": avg("confidence"), "clarity": avg("clarity"), "communication": avg("communication"), "star": avg("star_score"), "sentiment": events[-1]["metrics"]["sentiment"], "events": events, "status": state["status"]}


def openai_feedback(question_text, transcript):
    key = os.getenv("OPENAI_API_KEY")
    if not key or requests is None:
        return None
    payload = {"model": os.getenv("INTELLIHIRE_FEEDBACK_MODEL", "gpt-4o-mini"), "messages": [
        {"role": "system", "content": "You are an HR hiring manager. Evaluate only the candidate response. Give concise feedback on relevance, communication, confidence, STAR structure, strengths, and one improvement."},
        {"role": "user", "content": f"Interview question: {question_text}\nCandidate transcript: {transcript}"}
    ], "temperature": 0.2, "max_tokens": 350}
    try:
        r = requests.post("https://api.openai.com/v1/chat/completions", headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"}, json=payload, timeout=30)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    except Exception:
        return None
