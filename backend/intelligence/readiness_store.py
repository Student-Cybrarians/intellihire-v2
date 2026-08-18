import json
from backend.auth.auth_db import db_connect, init_db

SCHEMA = """
CREATE TABLE IF NOT EXISTS readiness_snapshots (
 id BIGSERIAL PRIMARY KEY,
 user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
 weighted_score DOUBLE PRECISION NOT NULL CHECK(weighted_score >= 0 AND weighted_score <= 100),
 confidence DOUBLE PRECISION NOT NULL CHECK(confidence >= 0 AND confidence <= 1),
 payload JSONB NOT NULL DEFAULT '{}'::jsonb,
 created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_readiness_user_created ON readiness_snapshots(user_id, created_at DESC);
"""

def ensure_schema():
    init_db()
    with db_connect() as conn:
        with conn.cursor() as cur:
            cur.execute(SCHEMA)

def save(user_id, result):
    ensure_schema()
    score=max(0.0,min(100.0,float(result.get('weighted_score',0))))
    confidence=max(0.0,min(1.0,float(result.get('confidence',0))))
    with db_connect() as conn:
        with conn.cursor() as cur:
            cur.execute('INSERT INTO readiness_snapshots(user_id,weighted_score,confidence,payload) VALUES(%s,%s,%s,%s) RETURNING id,created_at', (user_id,score,confidence,json.dumps(result,ensure_ascii=False)))
            row=cur.fetchone()
    return {'saved':True,'id':row[0],'created_at':row[1].isoformat() if row[1] else None}

def latest(user_id):
    ensure_schema()
    with db_connect() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT payload,created_at FROM readiness_snapshots WHERE user_id=%s ORDER BY created_at DESC LIMIT 1',(user_id,))
            row=cur.fetchone()
    if not row:return None
    payload=row[0] if isinstance(row[0],dict) else json.loads(row[0])
    payload['created_at']=row[1].isoformat() if row[1] else None
    return payload
