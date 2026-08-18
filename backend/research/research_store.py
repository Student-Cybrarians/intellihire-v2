"""PostgreSQL persistence for Personal AI Research Intern briefs."""
import json
from backend.auth.auth_db import db_connect

SCHEMA="""CREATE TABLE IF NOT EXISTS research_briefs(id BIGSERIAL PRIMARY KEY,user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,question TEXT NOT NULL,brief JSONB NOT NULL,created_at TIMESTAMPTZ NOT NULL DEFAULT NOW());CREATE INDEX IF NOT EXISTS idx_research_briefs_user ON research_briefs(user_id,created_at DESC);"""

def init_research_db():
    with db_connect() as conn:
        with conn.cursor() as cur: cur.execute(SCHEMA)

def save(user_id, question, brief):
    init_research_db()
    with db_connect() as conn:
        with conn.cursor() as cur:
            cur.execute('INSERT INTO research_briefs(user_id,question,brief) VALUES(%s,%s,%s) RETURNING id,created_at',(user_id,question,json.dumps(brief)))
            row=cur.fetchone()
    return {'id':int(row[0]),'created_at':row[1].isoformat() if row[1] else None}

def latest(user_id,limit=10):
    init_research_db()
    with db_connect() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT id,question,brief,created_at FROM research_briefs WHERE user_id=%s ORDER BY created_at DESC LIMIT %s',(user_id,max(1,min(int(limit),20))))
            rows=cur.fetchall()
    return [{'id':int(r[0]),'question':r[1],'brief':r[2] or {},'created_at':r[3].isoformat() if r[3] else None} for r in rows]
