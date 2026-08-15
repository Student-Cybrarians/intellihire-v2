import csv
import io
import json
import os
import re
import time
from typing import Any, Dict, List
import requests

SKILL_ALIASES = {"javascript":["javascript","js"],"typescript":["typescript","ts"],"node.js":["node.js","nodejs","node"],"react":["react","react.js"],"rest api":["rest api","restful","rest services"],"postgresql":["postgresql","postgres"],"machine learning":["machine learning","ml"],"deep learning":["deep learning"],"scikit-learn":["scikit-learn","sklearn"],"power bi":["power bi","powerbi"],"ci/cd":["ci/cd","cicd","continuous integration","continuous delivery"]}
COMMON_SKILLS=["python","java","javascript","typescript","react","node.js","sql","postgresql","mongodb","rest api","docker","kubernetes","aws","azure","gcp","fastapi","flask","django","pytorch","tensorflow","nlp","machine learning","deep learning","scikit-learn","pandas","numpy","system design","microservices","git","linux","data analysis","statistics","power bi","tableau","ci/cd","terraform","redis","graphql","spark","airflow","kafka","computer vision"]

def _tokens(text:str)->List[str]: return re.findall(r"[a-z0-9+#./-]+",(text or "").lower())
def extract_skills(text:str)->List[str]:
    lower=(text or "").lower(); found=[]
    for skill in COMMON_SKILLS:
        aliases=SKILL_ALIASES.get(skill,[skill])
        if any(re.search(r"(?<![a-z0-9])"+re.escape(a)+r"(?![a-z0-9])",lower) for a in aliases): found.append(skill)
    return found

def _chat(endpoint,api_key,model,system,user,timeout=None):
    """Call a chat-completions provider with a hard network timeout.

    Timeout is deliberately bounded because Module 1 is a synchronous request in
    the web app. A provider that stalls must yield quickly to the next provider
    or the deterministic fallback instead of consuming the whole server budget.
    """
    timeout = float(timeout if timeout is not None else os.getenv("MODULE1_AI_PROVIDER_TIMEOUT_SECONDS", "10"))
    payload={"model":model,"messages":[{"role":"system","content":system},{"role":"user","content":user}],"temperature":0.15,"max_tokens":2600,"stream":False}
    r=requests.post(endpoint,headers={"Authorization":f"Bearer {api_key}","Content-Type":"application/json"},json=payload,timeout=max(1.0,timeout))
    r.raise_for_status()
    body=r.json()
    return body["choices"][0]["message"]["content"]

def _extract_json(text):
    cleaned=re.sub(r"^```(?:json)?\s*","",(text or "").strip(),flags=re.I); cleaned=re.sub(r"\s*```$","",cleaned)
    try:return json.loads(cleaned)
    except json.JSONDecodeError:
        match=re.search(r"\{.*\}",cleaned,re.S)
        if match:return json.loads(match.group(0))
        raise

def _deterministic_metrics(resume,jd):
    rs=set(extract_skills(resume)); js=set(extract_skills(jd)); matched=sorted(rs&js); missing=sorted(js-rs); skill_score=round(100*len(matched)/max(1,len(js))); rt,jt=set(_tokens(resume)),set(_tokens(jd)); keyword=round(100*len(rt&jt)/max(1,len(jt)))
    sections={"contact":bool(re.search(r"@|\+?\d[\d ()-]{7,}",resume or "")),"summary":bool(re.search(r"summary|profile|objective",resume or "",re.I)),"experience":bool(re.search(r"experience|employment|worked",resume or "",re.I)),"education":bool(re.search(r"education|degree|university|college|b.tech|bachelor|master",resume or "",re.I)),"skills":bool(re.search(r"skills|technologies|technical skills",resume or "",re.I))}
    ats=round(.55*skill_score+.25*keyword+20*sum(sections.values())/len(sections)); return {"matched_skills":matched,"missing_skills":missing,"skill_match":skill_score,"keyword_match":keyword,"ats_baseline":min(100,ats),"sections":sections}

def _sanitize_resume(resume,missing,matched,role):
    out=dict(resume or {}); out["name"]=out.get("name") or "Candidate"; out["headline"]=out.get("headline") or role or "Target Role"; out["summary"]=out.get("summary") or ""
    skills=out.get("skills") or []; skills=[str(x) for x in (skills if isinstance(skills,list) else [skills]) if str(x).strip()]; existing={x.lower() for x in skills}
    for skill in missing:
        marker=f"[VERIFY] {skill}"
        if skill.lower() not in existing and marker.lower() not in existing: skills.append(marker)
    out["skills"]=skills
    keywords=out.get("keywords") or []; keywords=[str(x) for x in (keywords if isinstance(keywords,list) else [keywords]) if str(x).strip()]; seen={x.lower() for x in keywords}
    for skill in matched+missing:
        if skill.lower() not in seen: keywords.append(skill); seen.add(skill.lower())
    out["keywords"]=keywords
    for key in ("experience","education","projects","certifications"):
        value=out.get(key) or []; out[key]=value if isinstance(value,list) else [value]
    return out

def analyze_with_ai(resume_text,jd_text,company="",role=""):
    metrics=_deterministic_metrics(resume_text,jd_text)
    try:
        from ai import get_orchestrator
        from ai.schemas import MODULE1_SCHEMA
        ai_result=get_orchestrator().generate_structured(user_id="module1",feature="module1_ats",task="Explain the deterministic ATS baseline, strengths, contextual matches, gaps, weak evidence and resume improvements. Never invent candidate facts.",context={"resume":resume_text[:18000],"job_description":jd_text[:14000],"company":company,"role":role,"deterministic_metrics":metrics},schema=MODULE1_SCHEMA,reasoning=True,max_tokens=2200,retries=1,cache=False)
        ai=ai_result["data"]
        return {"provider":ai_result["provider"],"model":ai_result["model"],"is_ai":True,"ai_metadata":{k:ai_result[k] for k in ("requestId","latencyMs","usage","promptVersion")},"baseline":metrics,"ats_score":metrics["ats_baseline"],"overall_match":metrics["ats_baseline"],"keyword_match":metrics["keyword_match"],"semantic_match":metrics["keyword_match"],"skills_match":metrics["skill_match"],"matched_skills":metrics["matched_skills"],"missing_skills":metrics["missing_skills"],"strengths":ai.get("strengths",[]),"risks":ai.get("weakEvidence",[]),"recommendations":ai.get("recommendations",[]),"recruiter_feedback":ai.get("summary",""),"feedback":ai.get("summary",""),"learning_plan":ai.get("recommendations",[]),"recommended_certifications":[],"tailored_resume":{"name":"Candidate","headline":role or "Target Role","summary":ai.get("summary",""),"skills":ai.get("matchedSkills",[]),"experience":[],"education":[],"projects":[],"certifications":[],"keywords":metrics["matched_skills"]},"company":company,"role":role,"shortlist":"NOT_A_DECISION","ai_insights":ai}
    except Exception:
        pass
    try:
        from ai import get_orchestrator
        from ai.schemas import MODULE1_SCHEMA
        ai_result=get_orchestrator().generate_structured(
            user_id="module1", feature="module1_ats",
            task="Explain the deterministic ATS baseline, strengths, contextual matches, gaps, weak evidence and resume improvements. Never invent candidate facts.",
            context={"resume":resume_text[:18000],"job_description":jd_text[:14000],"company":company,"role":role,"deterministic_metrics":metrics},
            schema=MODULE1_SCHEMA, reasoning=True, max_tokens=2200, retries=1, cache=False)
        ai=ai_result["data"]
        return {"provider":ai_result["provider"],"model":ai_result["model"],"is_ai":True,"ai_metadata":{k:ai_result[k] for k in ("requestId","latencyMs","usage","promptVersion")},"baseline":metrics,"ats_score":metrics["ats_baseline"],"overall_match":metrics["ats_baseline"],"keyword_match":metrics["keyword_match"],"semantic_match":metrics["keyword_match"],"skills_match":metrics["skill_match"],"matched_skills":metrics["matched_skills"],"missing_skills":metrics["missing_skills"],"strengths":ai.get("strengths",[]),"risks":ai.get("weakEvidence",[]),"recommendations":ai.get("recommendations",[]),"recruiter_feedback":ai.get("summary",""),"feedback":ai.get("summary",""),"learning_plan":ai.get("recommendations",[]),"recommended_certifications":[],"tailored_resume":{"name":"Candidate","headline":role or "Target Role","summary":ai.get("summary",""),"skills":ai.get("matchedSkills",[]),"experience":[],"education":[],"projects":[],"certifications":[],"keywords":metrics["matched_skills"]},"company":company,"role":role,"shortlist":"NOT_A_DECISION","ai_insights":ai}
    except Exception:
        pass
    system="""You are IntelliHire's senior ATS/recruitment intelligence engine. Analyze a candidate resume strictly against the supplied job description and target role. Never invent candidate experience, education, employment, projects, certifications, employers, metrics, or skills. You may recommend skills/certifications as learning targets, but label them as recommendations. Return ONLY valid JSON with these keys: candidate, job, ats_score, overall_match, keyword_match, semantic_match, skills_match, matched_skills, missing_skills, strengths, risks, recommendations, recruiter_feedback, learning_plan, recommended_certifications, tailored_resume. tailored_resume must contain name, headline, summary, skills, experience, education, projects, certifications, keywords. Preserve factual candidate content. Never put an unverified JD skill into candidate-claimed experience. If you include a target skill in the resume skills section, prefix it with [VERIFY]."""
    prompt=f"""TARGET COMPANY: {company}\nTARGET ROLE: {role}\n\nJOB DESCRIPTION:\n{jd_text[:14000]}\n\nCANDIDATE RESUME:\n{resume_text[:18000]}\n\nDeterministic baseline metrics: {json.dumps(metrics)}\nProvide rigorous evidence-based ATS analysis and a clean ATS-friendly resume. Optimize for the JD's responsibilities and keywords while preserving candidate truth. Separate demonstrated skills from target/missing skills. Recommend certifications only when relevant; label all recommendations as recommendations."""
    providers=[]
    if os.getenv("OPENAI_API_KEY"): providers.append((os.getenv("OPENAI_BASE_URL","https://api.openai.com/v1/chat/completions"),os.getenv("OPENAI_MODEL","gpt-5-mini"),os.getenv("OPENAI_API_KEY"),"openai"))
    if os.getenv("NVIDIA_API_KEY"): providers.append((os.getenv("NVIDIA_API_URL","https://integrate.api.nvidia.com/v1/chat/completions"),os.getenv("NVIDIA_MODEL","nvidia/nemotron-3-nano-30b-a3b-reasoning"),os.getenv("NVIDIA_API_KEY"),"nvidia"))
    last_error=None
    total_budget=float(os.getenv("MODULE1_AI_TOTAL_TIMEOUT_SECONDS","22"))
    started=time.monotonic()
    for endpoint,model,key,provider in providers:
        remaining=total_budget-(time.monotonic()-started)
        if remaining <= 0:
            last_error="Module 1 AI total timeout budget exhausted"
            break
        provider_timeout=min(float(os.getenv("MODULE1_AI_PROVIDER_TIMEOUT_SECONDS","10")),remaining)
        try:
            data=_extract_json(_chat(endpoint,key,model,system,prompt,timeout=provider_timeout)); data.update({"provider":provider,"model":model,"is_ai":True,"baseline":metrics}); return _normalize(data,metrics,company,role)
        except (requests.Timeout,requests.ConnectionError) as exc:
            last_error=f"{provider} unavailable: {type(exc).__name__}: {exc}"
        except (requests.RequestException,KeyError,ValueError,TypeError, json.JSONDecodeError) as exc:
            last_error=f"{provider} response error: {type(exc).__name__}: {exc}"
        except Exception as exc:
            last_error=f"{provider} unexpected error: {type(exc).__name__}: {exc}"
    return _fallback(metrics,company,role,last_error)

def _normalize(data,metrics,company,role):
    for key,default in [("ats_score",metrics["ats_baseline"]),("overall_match",metrics["ats_baseline"]),("keyword_match",metrics["keyword_match"]),("semantic_match",metrics["keyword_match"]),("skills_match",metrics["skill_match"])]: data[key]=max(0,min(100,int(float(data.get(key,default)))))
    for key,default in [("matched_skills",metrics["matched_skills"]),("missing_skills",metrics["missing_skills"]),("recommended_certifications",[]),("learning_plan",[]),("recommendations",[])]:data[key]=data.get(key) or default
    data["matched_skills"]=sorted(set(map(str,data["matched_skills"]))); data["missing_skills"]=sorted(set(map(str,data["missing_skills"])))
    data["company"]=company; data["role"]=role; data["tailored_resume"]=_sanitize_resume(data.get("tailored_resume") or {},data["missing_skills"],data["matched_skills"],role); data["shortlist"]="SHORTLISTED" if data["ats_score"]>=80 else ("CONSIDER" if data["ats_score"]>=60 else "NEEDS_IMPROVEMENT"); data["feedback"]=data.get("recruiter_feedback",""); return data

def _fallback(metrics,company,role,error=None):
    resume=_sanitize_resume({"name":"Candidate","headline":role or "Target Role","summary":"","skills":metrics["matched_skills"],"experience":[],"education":[],"projects":[],"certifications":[]},metrics["missing_skills"],metrics["matched_skills"],role)
    return {"provider":"deterministic-fallback","model":None,"is_ai":False,"ai_error":error,"ats_score":metrics["ats_baseline"],"overall_match":round((metrics["skill_match"]+metrics["keyword_match"]+metrics["ats_baseline"])/3),"keyword_match":metrics["keyword_match"],"semantic_match":metrics["keyword_match"],"skills_match":metrics["skill_match"],"matched_skills":metrics["matched_skills"],"missing_skills":metrics["missing_skills"],"strengths":metrics["matched_skills"],"risks":metrics["missing_skills"],"recommendations":[f"Build evidence for: {x}" for x in metrics["missing_skills"]],"recruiter_feedback":"AI provider unavailable; deterministic ATS analysis was used.","feedback":"AI provider unavailable; deterministic ATS analysis was used.","learning_plan":[f"Learn and demonstrate {x}" for x in metrics["missing_skills"]],"recommended_certifications":[],"tailored_resume":resume,"company":company,"role":role,"shortlist":"SHORTLISTED" if metrics["ats_baseline"]>=80 else "CONSIDER"}

def resume_docx_bytes(resume):
    from docx import Document
    d=Document(); d.add_heading(resume.get("name","Candidate"),0); d.add_paragraph(resume.get("headline","")); d.add_heading("Professional Summary",level=1); d.add_paragraph(resume.get("summary",""))
    for title,key in [("Skills","skills"),("Experience","experience"),("Education","education"),("Projects","projects"),("Certifications","certifications")]:
        d.add_heading(title,level=1); values=resume.get(key,[]); values=[values] if isinstance(values,str) else values
        for value in values:d.add_paragraph(str(value),style="List Bullet")
    out=io.BytesIO(); d.save(out); return out.getvalue()

def resume_pdf_bytes(resume):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer
    out=io.BytesIO(); doc=SimpleDocTemplate(out,pagesize=A4,rightMargin=42,leftMargin=42,topMargin=42,bottomMargin=42); styles=getSampleStyleSheet(); story=[Paragraph(str(resume.get("name","Candidate")),styles["Title"]),Paragraph(str(resume.get("headline","")),styles["Heading2"])]
    for title,key in [("Professional Summary","summary"),("Skills","skills"),("Experience","experience"),("Education","education"),("Projects","projects"),("Certifications","certifications")]:
        story += [Spacer(1,8),Paragraph(title,styles["Heading2"])]
        values=resume.get(key,[]); values=[values] if isinstance(values,str) else values
        for value in values:story.append(Paragraph(str(value).replace("&","&amp;"),styles["BodyText"]))
    doc.build(story); return out.getvalue()

def resume_csv_bytes(resume):
    out=io.StringIO(); w=csv.writer(out); w.writerow(["section","content"])
    for key,value in resume.items():
        values=value if isinstance(value,list) else [value]
        for item in values:w.writerow([key,item])
    return out.getvalue().encode("utf-8-sig")
