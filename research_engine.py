"""Evidence-backed research planner for IntelliHire.

This module deliberately separates retrieval from generation. It accepts caller-provided
source records, validates URLs/titles, deduplicates evidence, ranks sources against a
career-twin query, and produces a bounded research brief. No fabricated citations are
created. A later web/RAG adapter can populate the source records from live retrieval.
"""
from __future__ import annotations
import re
from collections import Counter
from urllib.parse import urlparse


def _tokens(text):
    return re.findall(r"[a-z0-9+#./-]+", str(text or "").lower())


def _valid_url(value):
    try:
        parsed = urlparse(str(value or ""))
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
    except Exception:
        return False


def _clean_sources(sources):
    result=[]; seen=set()
    for source in sources if isinstance(sources,list) else []:
        if not isinstance(source,dict):
            continue
        url=str(source.get("url","")).strip()
        title=str(source.get("title","")).strip()
        if not _valid_url(url) or not title:
            continue
        key=url.lower()
        if key in seen:
            continue
        seen.add(key)
        result.append({"title":title[:240],"url":url,"snippet":str(source.get("snippet","")).strip()[:1200],"publisher":str(source.get("publisher","")).strip()[:160]})
    return result


def _score_source(source, query_tokens):
    text=" ".join([source.get("title",""),source.get("snippet",""),source.get("publisher","")])
    counts=Counter(_tokens(text))
    return round(sum(counts[t] for t in query_tokens if t in counts),3)


def build_research_brief(twin, question, sources, max_sources=6):
    question=str(question or "").strip()
    if not question:
        raise ValueError("research_question_required")
    clean=_clean_sources(sources)
    query_tokens=set(_tokens(question))
    for skill in twin.get("skill_gaps",[]) if isinstance(twin,dict) else []:
        query_tokens.update(_tokens(skill))
    ranked=[]
    for source in clean:
        ranked.append((source,_score_source(source,query_tokens)))
    ranked.sort(key=lambda item:(item[1],item[0]["title"].lower()),reverse=True)
    selected=[dict(source, relevance_score=score) for source,score in ranked[:max(1,min(int(max_sources),10))]]
    claims=[]
    for source in selected:
        snippet=source.get("snippet","")
        if snippet:
            claims.append({"claim":"Source evidence requires review against the cited snippet.","source_url":source["url"],"evidence":snippet})
    return {
        "question":question,
        "query_terms":sorted(query_tokens),
        "sources":selected,
        "claims":claims,
        "recommendations":[
            "Compare at least two independent sources before treating a claim as established.",
            "Prefer primary documentation, official reports, and peer-reviewed material when available.",
            "Do not convert an uncited inference into candidate experience or a hiring decision."
        ],
        "integrity":{"fabricated_sources":False,"fabricated_claims":False},
        "retrieval_status":"source_records_validated"
    }
