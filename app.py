from flask import Flask,jsonify,request,render_template,session,redirect,render_template_string
import os,re,math
from collections import Counter
from module2_routes import module2
from module2_engine import QUESTION_BANK,evaluate_answer,select_next,score_assessment
from module3_routes import module3
from module4_routes import module4
from module5_routes import module5
from auth_routes import auth,current_user,require_auth

app=Flask(__name__,static_folder='static',template_folder='templates')
app.secret_key=os.getenv('FLASK_SECRET_KEY','dev-only-change-me')
app.config.update(SESSION_COOKIE_HTTPONLY=True,SESSION_COOKIE_SECURE=True,SESSION_COOKIE_SAMESITE='Lax')
app.register_blueprint(auth);app.register_blueprint(module2);app.register_blueprint(module3);app.register_blueprint(module4);app.register_blueprint(module5)
SKILLS=['python','javascript','react','node.js','java','sql','mongodb','postgresql','rest api','docker','kubernetes','aws','fastapi','flask','django','pytorch','tensorflow','nlp','machine learning','deep learning','scikit-learn','system design','microservices','git','linux','pandas','numpy']
DEMO={'name':'Alex Johnson','role':'Software Engineer','company':'TechNova','skills':['Python','React','JavaScript','Node.js','MongoDB','REST API','Git','Pandas','NumPy'],'experience':3}
JOB={'company':'TechNova','role':'Software Engineer','required':['Python','React','Node.js','REST API','Git'],'preferred':['Docker','AWS','System Design']}
def toks(s):return re.findall(r'[a-z0-9+#./-]+',str(s).lower())
def skillset(s):
 t=' '.join(toks(s));return[x for x in SKILLS if re.search(r'(?<![a-z0-9])'+re.escape(x)+r'(?![a-z0-9])',t)]
def cosine(a,b):
 k=set(a)|set(b);d=sum(a.get(x,0)*b.get(x,0) for x in k);na=math.sqrt(sum(v*v for v in a.values()));nb=math.sqrt(sum(v*v for v in b.values()));return d/(na*nb) if na and nb else 0
def analyze(p):
 r=p.get('resume',DEMO);j=p.get('job',JOB);rt=' '.join(map(str,r.values()));jt=' '.join(map(str,j.values()));rs=set(skillset(rt));req=skillset(jt);found=[x for x in req if x in rs];missing=[x for x in req if x not in rs];rv=Counter(toks(rt));jv=Counter(toks(jt));sim=cosine(rv,jv)*100;sm=len(found)/max(len(req),1)*100;kw=len(set(toks(jt))&set(toks(rt)))/max(len(set(toks(jt))),1)*100;ats=round(.3*kw+.3*sm+.2*sim+.2*95);return{'atsScore':ats,'overallMatch':round((ats+sm+sim)/3),'skillsMatch':round(sm),'keywordMatch':round(kw),'semanticSimilarity':round(sim),'missingSkills':missing,'shortlist':'SHORTLISTED' if ats>=80 else 'CONSIDER','candidate':r,'job':j,'isSimulated':True}

SIGNIN_HTML='''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Sign in · IntelliHire</title><style>body{margin:0;min-height:100vh;display:grid;place-items:center;background:linear-gradient(135deg,#071426,#10274b 55%,#0b1230);font-family:system-ui,sans-serif;color:#fff}.card{width:min(420px,calc(100vw - 40px));padding:42px;border:1px solid rgba(255,255,255,.12);border-radius:24px;background:rgba(8,18,38,.86);text-align:center;box-shadow:0 24px 80px rgba(0,0,0,.35)}.brand{font-size:28px;font-weight:800}.eyebrow{color:#6fe7ff;font-size:12px;letter-spacing:.14em}.sub{color:#b7c6da;margin:10px 0 28px}.btn{display:block;padding:14px 18px;border-radius:12px;background:#fff;color:#132238;text-decoration:none;font-weight:700}</style></head><body><main class="card"><div class="eyebrow">AI-BASED PLACEMENT TRAINER</div><div class="brand">✦ INTELLIHIRE</div><h1>Welcome Back!</h1><div class="sub">Sign in to continue your placement journey.</div><a class="btn" href="/auth/google">Continue with Google</a></main></body></html>'''
DASH_HTML='''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Dashboard · IntelliHire</title><style>body{margin:0;background:#071426;color:#fff;font-family:system-ui,sans-serif}.wrap{max-width:1100px;margin:auto;padding:36px}.top{display:flex;justify-content:space-between;align-items:center}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px;margin-top:28px}.card{padding:24px;border:1px solid #203552;border-radius:18px;background:#0d1c33}.muted{color:#9db0c8}.btn{display:inline-block;margin:6px 8px 0 0;padding:12px 16px;border-radius:10px;background:#16345c;color:#fff;text-decoration:none}</style></head><body><div class="wrap"><div class="top"><div><div class="muted">INTELLIHIRE</div><h1>Welcome, {{ user.name or user.email }}</h1></div><a class="btn" href="/auth/logout">Sign out</a></div><div class="cards"><div class="card"><h2>Module 1</h2><p class="muted">ATS Resume Intelligence</p><a class="btn" href="/app/module1/overview">Open</a></div><div class="card"><h2>Module 2</h2><p class="muted">Adaptive Assessment</p><a class="btn" href="/app/module2/overview">Open</a></div><div class="card"><h2>Module 3</h2><p class="muted">Technical Interview</p><a class="btn" href="/app/module3">Open</a></div><div class="card"><h2>Module 4</h2><p class="muted">HR & Behavioral Interview</p><a class="btn" href="/app/module4">Open</a></div><div class="card"><h2>Module 5</h2><p class="muted">Hiring Committee & Readiness</p><a class="btn" href="/app/module5">Open</a></div></div></div></body></html>'''

@app.get('/')
def home():
    if current_user(): return redirect('/app/dashboard')
    return render_template_string(SIGNIN_HTML)

@app.get('/app/dashboard')
def dashboard():
    user,response=require_auth('USER')
    if response:return response
    return render_template_string(DASH_HTML,user=user)

@app.get('/app/<path:path>')
def shell(path):
    user=current_user()
    if not user:return redirect('/')
    if path.startswith('module2'): return render_template('module2.html')
    if path.startswith('module3'): return render_template('module3.html')
    if path.startswith('module4'): return render_template('module4.html')
    if path.startswith('module5'): return render_template('module5.html')
    if path.startswith('module1'): return render_template('index.html')
    return redirect('/app/dashboard')

@app.post('/app/module2/start')
def start_m2():
    user,response=require_auth('USER')
    if response:return response
    session['m2']={'ability':0.0,'answered':[],'events':[],'section':request.form.get('section',''),'count':int(request.form.get('count',8))};return redirect('/app/module2/assessment')
@app.route('/app/module2/assessment',methods=['GET','POST'])
def assessment():
    user,response=require_auth('USER')
    if response:return response
    s=session.get('m2',{'ability':0.0,'answered':[],'events':[],'section':'','count':8})
    if request.method=='POST':
        q=next((x for x in QUESTION_BANK if x.id==request.form.get('question_id')),None)
        if q:
            e=evaluate_answer(s['ability'],q,int(request.form.get('answer',-1)));s['events'].append(e);s['answered'].append(q.id);s['ability']=e['ability_after'];session['m2']=s
    if len(s['events'])>=s['count']:return redirect('/app/module2/results')
    q=select_next(s['ability'],s['answered'],s['section'] or None);return render_template('module2_assessment.html',question=q,ability=s['ability'],progress=len(s['events']),total=s['count'])
@app.get('/app/module2/results')
def m2_results():
    user,response=require_auth('USER')
    if response:return response
    return render_template('module2_results.html',result=score_assessment(session.get('m2',{}).get('events',[])))
@app.get('/api/health')
def health():return jsonify({'status':'ok','engine':'IntelliHire Python ML Engine','version':'2.6','modules':['module1','module2','module3','module4','module5'],'auth':'enabled'})
@app.get('/api/demo')
def demo():return jsonify({'resume':DEMO,'job':JOB,'result':analyze({})})
@app.post('/api/analyze')
def api_analyze():
    user,response=require_auth('USER')
    if response:return response
    return jsonify(analyze(request.get_json(silent=True) or {}))
if __name__=='__main__':app.run(host='0.0.0.0',port=int(os.getenv('PORT','5000')))
