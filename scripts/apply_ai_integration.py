from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def replace_once(path, old, new):
    p=ROOT/path; text=p.read_text(encoding='utf-8')
    if new in text or old not in text: return
    p.write_text(text.replace(old,new,1),encoding='utf-8')

replace_once('research_retrieval.py',
'''    if os.getenv("OPENAI_API_KEY") and not os.getenv("DEEPSEEK_API_KEY"):
''',
'''    if not os.getenv("DEEPSEEK_API_KEY") and not os.getenv("OPENAI_API_KEY"):
        return {"provider":"deterministic-fallback","is_ai":False,"synthesis_status":"evidence_only","answer":"Evidence was retrieved, but no AI synthesis provider is configured. Review the cited evidence directly.","key_findings":[{"finding":c.get('evidence',''),'citation':c.get('source_url','')} for c in brief.get('claims',[])],"implications_for_candidate":[],"learning_actions":[],"citations":[s.get('url','') for s in sources]}
    if os.getenv("OPENAI_API_KEY") and not os.getenv("DEEPSEEK_API_KEY"):
''')

# Keep the authenticated central AI endpoints registered.
app_path=ROOT/'app.py'; app_text=app_path.read_text(encoding='utf-8')
marker="app.register_blueprint(auth);app.register_blueprint(module2);app.register_blueprint(module3);app.register_blueprint(module4);app.register_blueprint(module5)"
if 'from backend.api.ai_routes import backend.ai_api' not in app_text:
    app_text=app_text.replace(marker,marker+"\nfrom backend.api.ai_routes import backend.ai_api\napp.register_blueprint(ai_api)",1)
app_path.write_text(app_text,encoding='utf-8')
print('AI integration patch applied')
