"""PostgreSQL persistence for user roadmap plans."""
from __future__ import annotations
import json
from backend.auth.auth_db import db_connect, init_db

SCHEMA = """CREATE TABLE IF NOT EXISTS career_roadmaps(id BIGSERIAL PRIMARY KEY,user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,plan_fingerprint TEXT NOT NULL,role TEXT NOT NULL DEFAULT '',payload JSONB NOT NULL,created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),UNIQUE(user_id,plan_fingerprint));CREATE INDEX IF NOT EXISTS idx_career_roadmaps_user ON career_roadmaps(user_id,updated_at DESC);"""

def _init():
    init_db()
    with db_connect() as conn:
        with conn.cursor() as cur: cur.execute(SCHEMA)

def save(user_id, plan):
    _init()
    with db_connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""INSERT INTO career_roadmaps(user_id,plan_fingerprint,role,payload) VALUES(%s,%s,%s,%s) ON CONFLICT(user_id,plan_fingerprint) DO UPDATE SET payload=EXCLUDED.payload,role=EXCLUDED.role,updated_at=NOW() RETURNING id,updated_at""",(user_id,plan.get('plan_fingerprint',''),plan.get('role',''),json.dumps(plan)))
            row=cur.fetchone()
    return {'id': int(row[0]), 'updated_at': row[1].isoformat() if row[1] else None}

def latest(user_id):
    _init()
    with db_connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT payload FROM career_roadmaps WHERE user_id=%s ORDER BY updated_at DESC LIMIT 1",(user_id,))
            row=cur.fetchone()
    return row[0] if row else None
