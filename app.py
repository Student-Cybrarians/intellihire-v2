from flask import Flask,jsonify,request,render_template,session,redirect
import re,math
from collections import Counter
from module2_routes import module2
from module2_engine import QUESTION_BANK,evaluate_answer,select_next,score_assessment
from module5_routes import module5
app=Flask(__name__,static_folder='static',template_folder='templates');app.secret_key='intellihire-demo';app.register_blueprint(module2);app.register_blueprint(module5)
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
@app.get('/')
def home():return render_template('index.html')
@app.get('/app/<path:path>')
def shell(path):return render_template('module2.html') if path.startswith('module2') else render_template('index.html')
@app.post('/app/module2/start')
def start_m2():
 session['m2']={'ability':0.0,'answered':[],'events':[],'section':request.form.get('section',''),'count':int(request.form.get('count',8))};return redirect('/app/module2/assessment')
@app.route('/app/module2/assessment',methods=['GET','POST'])
def assessment():
 s=session.get('m2',{'ability':0.0,'answered':[],'events':[],'section':'','count':8})
 if request.method=='POST':
  q=next((x for x in QUESTION_BANK if x.id==request.form.get('question_id')),None)
  if q:
   e=evaluate_answer(s['ability'],q,int(request.form.get('answer',-1)));s['events'].append(e);s['answered'].append(q.id);s['ability']=e['ability_after'];session['m2']=s
 if len(s['events'])>=s['count']:return redirect('/app/module2/results')
 q=select_next(s['ability'],s['answered'],s['section'] or None);return render_template('module2_assessment.html',question=q,ability=s['ability'],progress=len(s['events']),total=s['count'])
@app.get('/app/module2/results')
def m2_results():return render_template('module2_results.html',result=score_assessment(session.get('m2',{}).get('events',[])))
@app.get('/api/health')
def health():return jsonify({'status':'ok','engine':'IntelliHire Python ML Engine','version':'2.3','modules':['module1','module2','module5']})
@app.get('/api/demo')
def demo():return jsonify({'resume':DEMO,'job':JOB,'result':analyze({})})
@app.post('/api/analyze')
def api_analyze():return jsonify(analyze(request.get_json(silent=True) or {}))
if __name__=='__main__':app.run(host='0.0.0.0',port=5000)
