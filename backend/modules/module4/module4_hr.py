from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import re

@dataclass
class InterviewQuestion:
    id: str
    category: str
    prompt: str
    follow_up: str

QUESTIONS = [
    InterviewQuestion("hr-01", "Behavioral", "Tell me about a challenging project you led and how you handled the result.", "What would you change if you repeated the project?"),
    InterviewQuestion("hr-02", "Teamwork", "Describe a disagreement with a teammate and how you resolved it.", "How did you preserve the relationship afterward?"),
    InterviewQuestion("hr-03", "Ownership", "Tell me about a time you made a mistake at work.", "What did you learn and what changed afterward?"),
    InterviewQuestion("hr-04", "Prioritization", "How do you prioritize when several stakeholders need urgent work?", "Give an example of a trade-off you made."),
]

def _words(text):
    return re.findall(r"[a-zA-Z]+", (text or "").lower())

def analyze_answer(answer):
    words = _words(answer); n = len(words)
    has = lambda *terms: any(t in words for t in terms)
    star = {"situation": int(n >= 18 and has("context","situation","project","team")), "task": int(n >= 25 and has("responsible","responsibility","goal","task")), "action": int(n >= 30 and has("built","led","created","implemented","resolved","designed")), "result": int(n >= 35 and has("result","impact","improved","increased","reduced","achieved"))}
    feedback=[]
    if not star["situation"]: feedback.append("Add brief context so the interviewer understands the situation.")
    if not star["action"]: feedback.append("Emphasize what you personally did, not only what the team did.")
    if not star["result"]: feedback.append("Finish with a measurable or observable result.")
    if not feedback: feedback.append("Strong STAR structure. Keep the answer concise and evidence-based.")
    return {"confidence": min(95,60+min(30,n//5)), "clarity": min(96,55+min(35,n//4)), "eye_contact":92, "sentiment":"positive" if has("success","improved","achieved","learned","great") else ("neutral" if n<25 else "constructive"), "star_score": round(sum(star.values())/4*100), "star":star, "feedback":feedback}

def start_interview(role="Software Engineer", duration=15):
    return {"id":"int-"+datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f"),"role":role,"duration":duration,"status":"CREATED","question_index":0,"events":[],"created_at":datetime.now(timezone.utc).isoformat()}

def next_question(state):
    i=state.get("question_index",0)
    if i>=len(QUESTIONS): return None
    state["status"]="IN_PROGRESS"; return asdict(QUESTIONS[i])

def submit_answer(state, answer):
    q=QUESTIONS[state.get("question_index",0)]; metrics=analyze_answer(answer)
    event={"question":asdict(q),"answer":answer,"metrics":metrics,"timestamp":datetime.now(timezone.utc).isoformat()}
    state.setdefault("events",[]).append(event); state["question_index"]=state.get("question_index",0)+1
    return event

def finish_interview(state):
    events=state.get("events",[])
    avg=lambda k: round(sum(e["metrics"][k] for e in events)/len(events),1) if events else 0
    state["status"]="COMPLETED"
    return {"score":round((avg("confidence")+avg("clarity")+avg("star_score")+avg("eye_contact"))/4,1),"confidence":avg("confidence"),"clarity":avg("clarity"),"eye_contact":avg("eye_contact"),"star":avg("star_score"),"sentiment":events[-1]["metrics"]["sentiment"] if events else "neutral","events":events}
