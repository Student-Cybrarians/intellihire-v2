"""Live retrieval + evidence-grounded synthesis for the Personal AI Research Intern.

Retrieval uses a configured Tavily key when available. Synthesis uses the same
OpenAI/NVIDIA provider family as Module 1. If either service is unavailable,
the engine returns a deterministic, citation-preserving brief rather than
inventing evidence. Career Twin context is bounded and evidence-state aware.
"""
from __future__ import annotations
import json
import os
import time
import requests
from research_engine import build_research_brief
from research_context import build_context


def retrieve(question, twin=None, context=None, max_results=6, timeout=None):
    question=str(question or '').strip()
    if not question:
        raise ValueError('research_question_required')
    key=os.getenv('TAVILY_API_KEY','').strip()
    if not key:
        return [], 'not_configured'
    timeout=float(timeout or os.getenv('RESEARCH_RETRIEVAL_TIMEOUT_SECONDS','8'))
    query=question
    gaps=(twin or {}).get('skill_gaps',[]) if isinstance(twin,dict) else []
    if gaps:
        query += ' | skill gaps: ' + ', '.join(map(str,gaps[:8]))
    if isinstance(context,dict):
        graph=context.get('skill_graph',[])
        evidenced=[x.get('skill') for x in graph if isinstance(x,dict) and x.get('state')=='evidenced'][:8]
        target=context.get('role','')
        if target:
            query += ' | target role: ' + str(target)
        if evidenced:
            query += ' | evidenced skills: ' + ', '.join(map(str,evidenced))
    response=requests.post(
        os.getenv('TAVILY_API_URL','https://api.tavily.com/search'),
        json={'api_key':key,'query':query,'search_depth':os.getenv('TAVILY_SEARCH_DEPTH','advanced'),'max_results':max(1,min(int(max_results),10)),'include_answer':False,'include_raw_content':False},
        timeout=max(1.0,timeout),
    )
    response.raise_for_status()
    payload=response.json()
    records=[]
    for item in payload.get('results',[]) if isinstance(payload,dict) else []:
        if not isinstance(item,dict):
            continue
        records.append({'title':str(item.get('title','')).strip(),'url':str(item.get('url','')).strip(),'snippet':str(item.get('content','')).strip(),'publisher':str(item.get('url','')).split('/')[2] if '://' in str(item.get('url','')) else ''})
    return records, 'live'


def _chat(endpoint, key, model, system, user, timeout):
    payload={'model':model,'messages':[{'role':'system','content':system},{'role':'user','content':user}],'temperature':0.1,'max_tokens':1800,'stream':False}
    r=requests.post(endpoint,headers={'Authorization':f'Bearer {key}','Content-Type':'application/json'},json=payload,timeout=max(1.0,timeout))
    r.raise_for_status()
    return r.json()['choices'][0]['message']['content']


def _json(text):
    text=(text or '').strip()
    if text.startswith('```'):
        text=text.split('\n',1)[1] if '\n' in text else text
        text=text.rsplit('```',1)[0]
    return json.loads(text)


def synthesize(brief, context=None, timeout=None):
    sources=brief.get('sources',[])
    if not sources:
        return {'provider':'deterministic-fallback','is_ai':False,'synthesis_status':'no_evidence','answer':'No live evidence was retrieved. Configure TAVILY_API_KEY or provide source records before relying on this research.','key_findings':[],'citations':[]}
    system=('You are IntelliHire Personal AI Research Intern. Synthesize ONLY from the supplied evidence. '
            'The candidate context is personalization context, not evidence. Never present a skill gap, transferable skill, roadmap item, or inferred competency as candidate experience. '
            'Do not invent facts, URLs, quotations, employers, skills, or claims. Every factual finding must cite one or more supplied source URLs. '
            'Return JSON with keys answer, key_findings, implications_for_candidate, learning_actions, citations. citations must contain only supplied URLs.')
    evidence='\n\n'.join(f"SOURCE {i+1}: {s['title']}\nURL: {s['url']}\nEVIDENCE: {s.get('snippet','')}" for i,s in enumerate(sources))
    context_text=(context or {}).get('context_text','') if isinstance(context,dict) else ''
    prompt=f"Research question: {brief['question']}\n\nCandidate context (personalization only; not evidence):\n{context_text}\n\nEvidence:\n{evidence}"
    providers=[]
    if os.getenv('OPENAI_API_KEY'):
        providers.append((os.getenv('OPENAI_BASE_URL','https://api.openai.com/v1/chat/completions'),os.getenv('OPENAI_MODEL','gpt-5-mini'),os.getenv('OPENAI_API_KEY'),'openai'))
    if os.getenv('NVIDIA_API_KEY'):
        providers.append((os.getenv('NVIDIA_API_URL','https://integrate.api.nvidia.com/v1/chat/completions'),os.getenv('NVIDIA_MODEL','nvidia/nemotron-3-nano-30b-a3b-reasoning'),os.getenv('NVIDIA_API_KEY'),'nvidia'))
    total=float(os.getenv('RESEARCH_AI_TOTAL_TIMEOUT_SECONDS','16')); started=time.monotonic(); last=None
    for endpoint,model,key,provider in providers:
        remaining=total-(time.monotonic()-started)
        if remaining<=0: break
        try:
            result=_json(_chat(endpoint,key,model,system,prompt,min(float(os.getenv('RESEARCH_AI_PROVIDER_TIMEOUT_SECONDS','8')),remaining)))
            allowed={s['url'] for s in sources}
            citations=[str(x) for x in result.get('citations',[]) if str(x) in allowed]
            return {'provider':provider,'model':model,'is_ai':True,'synthesis_status':'ai_grounded',**result,'citations':citations}
        except (requests.RequestException,KeyError,TypeError,ValueError,json.JSONDecodeError) as exc:
            last=f'{provider}: {type(exc).__name__}: {exc}'
    return {'provider':'deterministic-fallback','model':None,'is_ai':False,'synthesis_status':'evidence_only','answer':'Evidence was retrieved, but the configured synthesis provider was unavailable. Review the cited evidence directly.','key_findings':[{'finding':c['evidence'],'citation':c['source_url']} for c in brief.get('claims',[])],'implications_for_candidate':[],'learning_actions':[],'citations':[s['url'] for s in sources],'ai_error':last}


def run_research(twin, question, supplied_sources=None, max_results=6, skill_graph=None, behavioral=None, roadmap=None):
    supplied=supplied_sources if isinstance(supplied_sources,list) else []
    context=build_context(twin, skill_graph, behavioral, roadmap)
    status='supplied'
    if not supplied:
        try:
            supplied,status=retrieve(question,twin,context.get('context'),max_results=max_results)
        except (requests.RequestException,ValueError) as exc:
            supplied=[]; status=f'retrieval_unavailable:{type(exc).__name__}'
    brief=build_research_brief(twin or {},question,supplied,max_results)
    synthesis=synthesize(brief,context)
    return {**brief,'retrieval_status':status,'context':context,'synthesis':synthesis,'integrity':{'fabricated_sources':False,'fabricated_claims':not synthesis.get('is_ai',False)}}


def synthesize_via_central_orchestrator(brief, context=None, timeout=None):
    sources=brief.get("sources",[])
    if not sources:
        return {"provider":"none","is_ai":False,"synthesis_status":"no_evidence","answer":"No live evidence was retrieved.","key_findings":[],"implications_for_candidate":[],"learning_actions":[],"citations":[]}
    try:
        from ai import get_orchestrator
        from ai.schemas import RESEARCH_SCHEMA
        evidence=[{"url":s.get("url",""),"title":s.get("title",""),"snippet":s.get("snippet","")} for s in sources]
        result=get_orchestrator().generate_structured(user_id="research",feature="research_intern",task="Synthesize only the supplied sources. Every factual finding must be grounded in supplied URLs.",context={"question":brief.get("question",""),"sources":evidence,"personal_context":context or {}},schema=RESEARCH_SCHEMA,reasoning=True,max_tokens=1800,retries=1,cache=True,evidence=evidence)
        allowed={s.get("url") for s in sources}
        data=result["data"]
        data["citations"]=[x for x in data.get("citations",[]) if x in allowed]
        return {"provider":result["provider"],"model":result["model"],"is_ai":True,"synthesis_status":"ai_grounded",**data}
    except Exception as exc:
        return {"provider":"none","is_ai":False,"synthesis_status":"unavailable","answer":"AI analysis is temporarily unavailable. Review the cited evidence directly.","key_findings":[],"implications_for_candidate":[],"learning_actions":[],"citations":[s.get("url","") for s in sources],"ai_error":f"{type(exc).__name__}: {exc}"}

_original_synthesize=synthesize
def synthesize(brief, context=None, timeout=None):
    sources=brief.get("sources",[])
    if not sources:
        return {"provider":"deterministic-fallback","is_ai":False,"synthesis_status":"no_evidence","answer":"No live evidence was retrieved. Configure retrieval before relying on this research.","key_findings":[],"implications_for_candidate":[],"learning_actions":[],"citations":[]}
    if not os.getenv("DEEPSEEK_API_KEY") and not os.getenv("OPENAI_API_KEY"):
        return {"provider":"deterministic-fallback","is_ai":False,"synthesis_status":"evidence_only","answer":"Evidence was retrieved, but no AI synthesis provider is configured. Review the cited evidence directly.","key_findings":[{"finding":c.get('evidence',''),'citation':c.get('source_url','')} for c in brief.get('claims',[])],"implications_for_candidate":[],"learning_actions":[],"citations":[s.get('url','') for s in sources]}
    if os.getenv("OPENAI_API_KEY") and not os.getenv("DEEPSEEK_API_KEY"):
        try:
            system=("You are IntelliHire Personal AI Research Intern. Synthesize ONLY from supplied evidence. Do not invent facts, URLs, employers, skills or claims. Return JSON with answer, key_findings, implications_for_candidate, learning_actions, citations.")
            evidence='\n\n'.join(f"SOURCE {i+1}: {s.get('title','')}\nURL: {s.get('url','')}\nEVIDENCE: {s.get('snippet','')}" for i,s in enumerate(sources))
            content=_chat('https://api.openai.com/v1/chat/completions',os.getenv('OPENAI_API_KEY'),os.getenv('OPENAI_MODEL','gpt-5-mini'),system,f"Research question: {brief.get('question','')}\n\nEvidence:\n{evidence}",float(os.getenv('RESEARCH_AI_PROVIDER_TIMEOUT_SECONDS','8')))
            data=_json(content); allowed={s.get('url') for s in sources}; data['citations']=[x for x in data.get('citations',[]) if x in allowed]
            return {"provider":"openai","model":os.getenv('OPENAI_MODEL','gpt-5-mini'),"is_ai":True,"synthesis_status":"ai_grounded",**data}
        except Exception:
            return {"provider":"deterministic-fallback","is_ai":False,"synthesis_status":"evidence_only","answer":"Evidence was retrieved, but the configured synthesis provider was unavailable. Review the cited evidence directly.","key_findings":[{"finding":c.get('evidence',''),'citation':c.get('source_url','')} for c in brief.get('claims',[])],"implications_for_candidate":[],"learning_actions":[],"citations":[s.get('url','') for s in sources]}
    return synthesize_via_central_orchestrator(brief, context, timeout)
