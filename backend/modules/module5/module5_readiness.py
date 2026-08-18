from typing import Any

MODULE_WEIGHTS = {'Module 1':0.20,'Module 2':0.20,'Module 3':0.25,'Module 4':0.20}

def _clamp(value):
    return max(0.0,min(100.0,float(value)))

def _competency_score(behavioral):
    values=[]
    for item in (behavioral or {}).get('competencies',{}).values():
        if isinstance(item,dict) and item.get('score') is not None and item.get('evidence_count',0)>0:
            values.append(_clamp(item['score']))
    return sum(values)/len(values) if values else None

def build_readiness(performance, twin=None, research=None, roadmap=None, behavioral=None):
    module_scores={k:_clamp((performance or {}).get(k,{}).get('score',0) if (performance or {}).get(k) else 0) for k in MODULE_WEIGHTS}
    observed=[v for k,v in module_scores.items() if (performance or {}).get(k)]
    module_weight=sum(MODULE_WEIGHTS[k] for k in module_scores if (performance or {}).get(k))
    weighted_modules=(sum(module_scores[k]*MODULE_WEIGHTS[k] for k in module_scores)/module_weight) if module_weight else 0
    comp=_competency_score(behavioral)
    gap_count=len((twin or {}).get('skill_gaps',[]) or [])
    matched=len((twin or {}).get('matched_skills',[]) or [])
    skill_coverage=100.0*matched/max(1,matched+gap_count) if (twin or {}) else 0.0
    roadmap_items=(roadmap or {}).get('milestones',[]) if isinstance(roadmap,dict) else []
    completed=sum(1 for x in roadmap_items if isinstance(x,dict) and str(x.get('status','')).lower() in {'complete','completed'})
    roadmap_completion=100.0*completed/max(1,len(roadmap_items)) if roadmap_items else 0.0
    research_sources=(research or {}).get('sources',[]) if isinstance(research,dict) else []
    evidence_bonus=min(5.0,len(research_sources))
    components=[('module_performance',weighted_modules,0.65,module_weight>0),('skill_coverage',skill_coverage,0.15,bool(twin)),('behavioral_competencies',comp or 0,0.10,comp is not None),('roadmap_completion',roadmap_completion,0.10,bool(roadmap_items))]
    total=sum(score*weight for _,score,weight,available in components if available)
    denom=sum(weight for _,score,weight,available in components if available)
    readiness=_clamp(total/denom if denom else 0)
    readiness=_clamp(readiness+evidence_bonus)
    evidence_points=sum(1 for _,_,_,available in components if available)+min(3,len(research_sources))
    confidence=min(1.0,evidence_points/7.0)
    if confidence<0.45: band='Insufficient evidence'
    elif readiness>=85: band='High readiness'
    elif readiness>=70: band='Developing readiness'
    else: band='Needs development'
    strengths=[k for k,v in module_scores.items() if v>=85]
    actions=[]
    for k,v in module_scores.items():
        if v<75: actions.append({'area':k,'action':'Target this module with focused practice and another measured assessment.'})
    if gap_count: actions.append({'area':'Skill gaps','action':f'Close {gap_count} role-relevant skill gap(s) using the persisted roadmap.'})
    if comp is None: actions.append({'area':'Behavioral evidence','action':'Complete a behavioral interview to establish competency evidence.'})
    return {'module_scores':module_scores,'weighted_score':round(readiness,1),'readiness_band':band,'confidence':round(confidence,3),'strengths':strengths,'skill_coverage':round(skill_coverage,1),'behavioral_competency_score':round(comp,1) if comp is not None else None,'roadmap_completion':round(roadmap_completion,1),'research_evidence_count':len(research_sources),'next_actions':actions,'integrity':{'employment_decision_support_only':True,'autonomous_hiring_decision':False,'confidence_limited_by_evidence':confidence<0.7}}
