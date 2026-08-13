from flask import Flask, jsonify, request, render_template
import re, math
from collections import Counter
from module2_routes import module2
app=Flask(__name__,static_folder='static',template_folder='templates'); app.register_blueprint(module2)
SKILLS=['python','javascript','typescript','react','node.js','express.js','java','sql','mongodb','postgresql','rest api','graphql','docker','kubernetes','aws','azure','gcp','ci/cd','fastapi','flask','django','pytorch','tensorflow','nlp','machine learning','deep learning','scikit-learn','system design','microservices','git','linux','pandas','numpy']
DEMO={'name':'Alex Johnson','role':'Software Engineer','company':'TechNova','skills':['Python','React','JavaScript','Node.js','Express.js','MongoDB','REST API','Git','DSA','Pandas','NumPy'],'experience':3,'education':'B.Tech Computer Science','summary':'Software engineer building scalable web applications and data-driven products.','projects':['Recruitment analytics platform','Real-time collaboration dashboard']}
JOB={'company':'TechNova','role':'Software Engineer','required':['Python','React','Node.js','REST API','Git','Data Structures'],'preferred':['Docker','AWS','CI/CD','Kubernetes','System Design','Microservices']}
def toks(s): return re.findall(r'[a-z0-9+#./-]+',str(s).lower())
def skillset(s):
 t=' '.join(toks(s)); return [x for x in SKILLS if re.search(r'(?<![a-z0-9])'+re.escape(x)+r'(?![a-z0-9])',t)]
def cosine(a,b):
 keys=set(a)|set(b); dot=sum(a.get(k,0)*b.get(k,0) for k in keys); na=math.sqrt(sum(v*v for v in a.values())); nb=math.sqrt(sum(v*v for v in b.values())); return dot/(na*nb) if na and nb else 0
def analyze(p):
 r=p.get('resume',DEMO); j=p.get('job',JOB); rt=' '.join(map(str,r.values())); jt=' '.join(map(str,j.values())); rs=set(skillset(rt)); req=skillset(jt); found=[x for x in req if x in rs]; missing=[x for x in req if x not in rs]; rv=Counter(toks(rt)); jv=Counter(toks(jt)); tr=sum(rv.values()) or 1; tj=sum(jv.values()) or 1; sim=cosine({k:v/tr for k,v in rv.items()},{k:v/tj for k,v in jv.items()})*100; kw=len(set(toks(jt))&set(toks(rt)))/max(len(set(toks(jt))),1)*100; sm=len(found)/max(len(req),1)*100; exp=min(100,70+int(r.get('experience',0))*8); ats=round(.25*kw+.25*sm+.15*exp+.15*sim+.10*94+.05*96+.05*95); status='SHORTLISTED' if ats>=80 else ('CONSIDER' if ats>=65 else 'REJECTED'); return {'atsScore':ats,'overallMatch':round((ats+sm+sim)/3),'keywordMatch':round(kw),'semanticSimilarity':round(sim),'skillsMatch':round(sm),'experienceMatch':exp,'educationMatch':95,'keywordCoverage':round(kw),'companyFit':92,'missingSkills':missing or ['No critical gaps'],'keywordsFound':list(set(toks(jt))&set(toks(rt)))[:20],'shortlist':status,'confidence':min(99,max(70,ats+4)),'isSimulated':True,'candidate':r,'job':j,'recommendations':['Add measurable outcomes to experience bullets.','Add relevant missing skills only when truthful.','Keep ATS-friendly headings and consistent dates.','Mirror important JD terminology naturally.'],'feedback':'Strong technical foundation and relevant project experience. Improve measurable impact and close the highest-priority skill gaps.'}
@app.get('/')
def home(): return render_template('index.html')
@app.get('/app/<path:path>')
def shell(path): return render_template('module2.html') if path.startswith('module2') else render_template('index.html')
@app.get('/api/health')
def health(): return jsonify({'status':'ok','engine':'IntelliHire Python ML Engine','version':'2.2','modules':['module1','module2']})
@app.get('/api/demo')
def demo(): return jsonify({'resume':DEMO,'job':JOB,'result':analyze({})})
@app.post('/api/analyze')
def api_analyze(): return jsonify(analyze(request.get_json(silent=True) or {}))
if __name__=='__main__': app.run(host='0.0.0.0',port=5000)
