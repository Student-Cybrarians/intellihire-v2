from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def patch(path, old, new):
    p = ROOT / path
    text = p.read_text(encoding='utf-8')
    if new in text:
        return False
    if old not in text:
        raise SystemExit(f'Patch anchor not found: {path}: {old[:80]!r}')
    p.write_text(text.replace(old, new, 1), encoding='utf-8')
    return True


# Module 1: central DeepSeek orchestration for explanation/synthesis, while the deterministic baseline remains authoritative.
patch('module1_ai.py',
      'def analyze_with_ai(resume_text,jd_text,company="",role=""):\n    metrics=_deterministic_metrics(resume_text,jd_text)\n',
      '''def analyze_with_ai(resume_text,jd_text,company="",role=""):\n    metrics=_deterministic_metrics(resume_text,jd_text)\n    try:\n        from ai import get_orchestrator\n        from ai.schemas import MODULE1_SCHEMA\n        result = get_orchestrator().generate_structured(\n            user_id="module1", feature="module1_ats",\n            task="Explain the deterministic ATS baseline, strengths, contextual matches, gaps, weak evidence and actionable resume improvements. Never invent candidate facts.",\n            context={"resume": resume_text[:18000], "job_description": jd_text[:14000], "company": company, "role": role, "deterministic_metrics": metrics},\n            schema=MODULE1_SCHEMA, reasoning=True, max_tokens=2200, retries=1, cache=False,\n        )\n        ai = result["data"]\n        data = {\n            "provider": result["provider"], "model": result["model"], "is_ai": True,\n            "ai_metadata": {k: result[k] for k in ("requestId", "latencyMs", "usage", "promptVersion")},\n            "baseline": metrics, "ats_score": metrics["ats_baseline"],\n            "overall_match": metrics["ats_baseline"], "keyword_match": metrics["keyword_match"],\n            "semantic_match": metrics["keyword_match"], "skills_match": metrics["skill_match"],\n            "matched_skills": metrics["matched_skills"], "missing_skills": metrics["missing_skills"],\n            "strengths": ai.get("strengths", []), "risks": ai.get("weakEvidence", []),\n            "recommendations": ai.get("recommendations", []), "recruiter_feedback": ai.get("summary", ""),\n            "feedback": ai.get("summary", ""), "learning_plan": ai.get("recommendations", []),\n            "recommended_certifications": [], "tailored_resume": {"name": "Candidate", "headline": role or "Target Role", "summary": ai.get("summary", ""), "skills": ai.get("matchedSkills", []), "experience": [], "education": [], "projects": [], "certifications": [], "keywords": metrics["matched_skills"]},\n            "company": company, "role": role, "shortlist": "NOT_A_DECISION",\n            "ai_insights": ai,\n        }\n        return data\n    except Exception as exc:\n        # Preserve the existing honest provider fallback path.\n        _ai_orchestrator_error = f"central_orchestrator: {type(exc).__name__}: {exc}"\n''')

# Module 2: deterministic answer evaluation remains authoritative; AI supplies explanation only.
patch('app.py',
      "        if q:\n            e=evaluate_answer(s['ability'],q,int(request.form.get('answer',-1)));s['events'].append(e);s['answered'].append(q.id);s['ability']=e['ability_after'];session['m2']=s\n",
      """        if q:\n            e=evaluate_answer(s['ability'],q,int(request.form.get('answer',-1)))\n            try:\n                from ai import get_orchestrator\n                from ai.schemas import MODULE2_SCHEMA\n                ai_result=get_orchestrator().generate_structured(user_id=user['id'],feature='module2_feedback',task='Explain the deterministic assessment result and identify a misconception and next conceptual focus. Do not change correctness.',context={'question':q.__dict__,'answer_index':int(request.form.get('answer',-1)),'deterministic_result':e},schema=MODULE2_SCHEMA,max_tokens=700,retries=0)\n                e['ai_feedback']=ai_result['data']; e['ai_metadata']={k:ai_result[k] for k in ('provider','model','requestId','latencyMs','usage')}\n            except Exception as exc:\n                e['ai_feedback']={'status':'unavailable','message':'AI analysis is temporarily unavailable.'}\n            s['events'].append(e);s['answered'].append(q.id);s['ability']=e['ability_after'];session['m2']=s\n""")

# Module 3: AI evaluates reasoning/communication; deterministic code evaluator remains authoritative.
patch('module3_routes.py',
      "    result=score_answer(text); s['events'].append({'question_id':q['id'],'answer':text,'evaluation':result})\n",
      """    result=score_answer(text)\n    try:\n        from ai import get_orchestrator\n        from ai.schemas import INTERVIEW_SCHEMA\n        ai_result=get_orchestrator().generate_structured(user_id=user['id'],feature='module3_interview',task='Evaluate technical reasoning, explanation quality and propose one follow-up question. Do not override deterministic execution results.',context={'question':q,'answer':text[:12000],'deterministic_evaluation':result},schema=INTERVIEW_SCHEMA,reasoning=True,max_tokens=900,retries=0)\n        result['ai_feedback']=ai_result['data']; result['ai_metadata']={k:ai_result[k] for k in ('provider','model','requestId','latencyMs','usage')}\n    except Exception:\n        result['ai_feedback']={'status':'unavailable','message':'AI analysis is temporarily unavailable.'}\n    s['events'].append({'question_id':q['id'],'answer':text,'evaluation':result})\n""")

# Module 4: override provider selection with the common orchestrator without exposing chain-of-thought.
patch('module4_liftoff.py',
      "def model_feedback(question_text,transcript):\n    if os.getenv('INTELLIHIRE_AI_PROVIDER','nvidia').lower()=='openai': return openai_feedback(question_text,transcript) or nvidia_feedback(question_text,transcript)\n    return nvidia_feedback(question_text,transcript) or openai_feedback(question_text,transcript)\n",
      """def model_feedback(question_text,transcript):\n    try:\n        from ai import get_orchestrator\n        from ai.schemas import INTERVIEW_SCHEMA\n        result=get_orchestrator().generate_structured(user_id='module4',feature='module4_hr_interview',task='Act as an HR interview coach. Evaluate clarity, relevance, evidence and STAR structure. Do not infer protected characteristics or make an employment decision.',context={'question':question_text,'candidate_response':transcript[:12000]},schema=INTERVIEW_SCHEMA,reasoning=True,max_tokens=900,retries=0)\n        return result['data']\n    except Exception:\n        return None\n""")

# Module 5: preserve evidence-based numeric readiness and add AI explanation as a separate field.
patch('module5_routes.py',
      "        result=build_readiness(performance,twin,research,roadmap,behavioral)\n        result['persistence']=save_readiness(user['id'],result)\n",
      """        result=build_readiness(performance,twin,research,roadmap,behavioral)\n        try:\n            from ai import get_orchestrator\n            from ai.schemas import MODULE5_SCHEMA\n            ai_result=get_orchestrator().generate_structured(user_id=user['id'],feature='module5_readiness',task='Explain evidence-based readiness, strengths, weaknesses, skill gaps and next actions. Do not invent or change numerical scores.',context={'performance':performance,'career_twin':twin,'research':research,'roadmap':roadmap,'behavioral':behavioral,'deterministic_readiness':result},schema=MODULE5_SCHEMA,reasoning=True,max_tokens=1800,retries=0,cache=True)\n            result['ai_insights']=ai_result['data']; result['ai_metadata']={k:ai_result[k] for k in ('provider','model','requestId','latencyMs','usage')}\n        except Exception:\n            result['ai_insights']={'status':'unavailable','message':'AI analysis is temporarily unavailable.'}\n        result['persistence']=save_readiness(user['id'],result)\n""")

# Research Intern: use the same provider layer for grounded synthesis.
with (ROOT / 'research_retrieval.py').open('a', encoding='utf-8') as f:
    f.write(r'''\n\n# Central-orchestrator synthesis override. Defined after the legacy implementation so the\n# runtime name resolution uses the common AI layer while preserving deterministic retrieval.\ndef synthesize(brief, context=None, timeout=None):\n    sources=brief.get('sources',[])\n    if not sources:\n        return {'provider':'none','is_ai':False,'synthesis_status':'no_evidence','answer':'No live evidence was retrieved.','key_findings':[],'implications_for_candidate':[],'learning_actions':[],'citations':[]}\n    try:\n        from ai import get_orchestrator\n        from ai.schemas import RESEARCH_SCHEMA\n        evidence=[{'url':s.get('url',''),'title':s.get('title',''),'snippet':s.get('snippet','')} for s in sources]\n        result=get_orchestrator().generate_structured(user_id='research',feature='research_intern',task='Synthesize only the supplied sources. Every factual finding must be grounded in the supplied URLs. Personal context is for relevance, not evidence.',context={'question':brief.get('question',''),'sources':evidence,'personal_context':context or {}},schema=RESEARCH_SCHEMA,reasoning=True,max_tokens=1800,retries=1,cache=True,evidence=evidence)\n        allowed={s.get('url') for s in sources}\n        data=result['data']; data['citations']=[x for x in data.get('citations',[]) if x in allowed]\n        return {'provider':result['provider'],'model':result['model'],'is_ai':True,'synthesis_status':'ai_grounded',**data,'ai_metadata':{k:result[k] for k in ('requestId','latencyMs','usage','promptVersion')}}\n    except Exception as exc:\n        return {'provider':'none','is_ai':False,'synthesis_status':'unavailable','answer':'AI analysis is temporarily unavailable. Review the cited evidence directly.','key_findings':[],'implications_for_candidate':[],'learning_actions':[],'citations':[s.get('url','') for s in sources],'ai_error':f'{type(exc).__name__}: {exc}'}\n''')

# Register the authenticated central AI endpoints without disturbing existing routes.
app_path = ROOT / 'app.py'
app_text = app_path.read_text(encoding='utf-8')
marker = "app.register_blueprint(auth);app.register_blueprint(module2);app.register_blueprint(module3);app.register_blueprint(module4);app.register_blueprint(module5)"
if 'from ai_routes import ai_api' not in app_text:
    app_text = app_text.replace(marker, marker + "\nfrom ai_routes import ai_api\napp.register_blueprint(ai_api)", 1)
app_path.write_text(app_text, encoding='utf-8')

print('AI integration patch applied')
'''
