from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path, old, new):
    p = ROOT / path
    text = p.read_text(encoding='utf-8')
    if new in text:
        return
    if old not in text:
        return
    p.write_text(text.replace(old, new, 1), encoding='utf-8')

# Production integrations. These replacements are idempotent.
replace_once('research_retrieval.py','''def synthesize(brief, context=None, timeout=None):\n    return synthesize_via_central_orchestrator(brief, context, timeout)\n''','''def synthesize(brief, context=None, timeout=None):\n    sources=brief.get("sources",[])\n    if not sources:\n        return {"provider":"deterministic-fallback","is_ai":False,"synthesis_status":"no_evidence","answer":"No live evidence was retrieved. Configure retrieval before relying on this research.","key_findings":[],"implications_for_candidate":[],"learning_actions":[],"citations":[]}\n    if os.getenv("OPENAI_API_KEY") and not os.getenv("DEEPSEEK_API_KEY"):\n        try:\n            system=("You are IntelliHire Personal AI Research Intern. Synthesize ONLY from supplied evidence. Do not invent facts, URLs, employers, skills or claims. Return JSON with answer, key_findings, implications_for_candidate, learning_actions, citations.")\n            evidence='\\n\\n'.join(f"SOURCE {i+1}: {s.get('title','')}\\nURL: {s.get('url','')}\\nEVIDENCE: {s.get('snippet','')}" for i,s in enumerate(sources))\n            content=_chat('https://api.openai.com/v1/chat/completions',os.getenv('OPENAI_API_KEY'),os.getenv('OPENAI_MODEL','gpt-5-mini'),system,f"Research question: {brief.get('question','')}\\n\\nEvidence:\\n{evidence}",float(os.getenv('RESEARCH_AI_PROVIDER_TIMEOUT_SECONDS','8')))\n            data=_json(content); allowed={s.get('url') for s in sources}; data['citations']=[x for x in data.get('citations',[]) if x in allowed]\n            return {"provider":"openai","model":os.getenv('OPENAI_MODEL','gpt-5-mini'),"is_ai":True,"synthesis_status":"ai_grounded",**data}\n        except Exception:\n            return {"provider":"deterministic-fallback","is_ai":False,"synthesis_status":"evidence_only","answer":"Evidence was retrieved, but the configured synthesis provider was unavailable. Review the cited evidence directly.","key_findings":[{"finding":c.get('evidence',''),'citation':c.get('source_url','')} for c in brief.get('claims',[])],"implications_for_candidate":[],"learning_actions":[],"citations":[s.get('url','') for s in sources]}\n    return synthesize_via_central_orchestrator(brief, context, timeout)\n''')

# Register authenticated AI endpoints during Flask module import.
app_path=ROOT / 'app.py'
app_text=app_path.read_text(encoding='utf-8')
marker="app.register_blueprint(auth);app.register_blueprint(module2);app.register_blueprint(module3);app.register_blueprint(module4);app.register_blueprint(module5)"
if 'from ai_routes import ai_api' not in app_text:
    app_text=app_text.replace(marker,marker+"\nfrom ai_routes import ai_api\napp.register_blueprint(ai_api)",1)
app_path.write_text(app_text,encoding='utf-8')
print('AI integration patch applied')
