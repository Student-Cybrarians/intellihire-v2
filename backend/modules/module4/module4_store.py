import json
from backend.auth.auth_db import db_connect, init_db

SCHEMA = """
CREATE TABLE IF NOT EXISTS module4_sessions (
 id TEXT PRIMARY KEY,
 user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
 role TEXT NOT NULL,
 interviewer TEXT NOT NULL,
 duration_minutes INTEGER NOT NULL CHECK(duration_minutes BETWEEN 1 AND 120),
 question_index INTEGER NOT NULL DEFAULT 0,
 events JSONB NOT NULL DEFAULT '[]'::jsonb,
 status TEXT NOT NULL DEFAULT 'IN_PROGRESS' CHECK(status IN ('IN_PROGRESS','COMPLETED','ABANDONED')),
 created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
 updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
 completed_at TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_module4_sessions_user ON module4_sessions(user_id, updated_at DESC);
"""

def ensure_schema():
    init_db()
    with db_connect() as conn:
        with conn.cursor() as cur:
            cur.execute(SCHEMA)

def create_session(user_id, state):
    ensure_schema()
    with db_connect() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO module4_sessions(id,user_id,role,interviewer,duration_minutes,question_index,events,status) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)", (state['id'], user_id, state['role'], state['interviewer'], int(state['duration']), int(state.get('question_index',0)), json.dumps(state.get('events',[])), state.get('status','IN_PROGRESS')))

def get_session(user_id, session_id):
    ensure_schema()
    with db_connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id,role,interviewer,duration_minutes,question_index,events,status,created_at FROM module4_sessions WHERE id=%s AND user_id=%s", (session_id,user_id))
            row=cur.fetchone()
    if not row:return None
    return {'id':row[0],'role':row[1],'interviewer':row[2],'duration':row[3],'question_index':row[4],'events':row[5] or [],'status':row[6],'created_at':row[7].isoformat() if row[7] else None,'user_id':user_id}

def save_session(user_id, state):
    ensure_schema()
    with db_connect() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE module4_sessions SET question_index=%s,events=%s,status=%s,updated_at=NOW(),completed_at=CASE WHEN %s='COMPLETED' THEN NOW() ELSE completed_at END WHERE id=%s AND user_id=%s", (int(state.get('question_index',0)),json.dumps(state.get('events',[])),state.get('status','IN_PROGRESS'),state.get('status','IN_PROGRESS'),state['id'],user_id))
            if cur.rowcount != 1: raise LookupError('session_not_found')

def list_sessions(user_id, limit=50):
    ensure_schema()
    with db_connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id,role,status,created_at,question_index FROM module4_sessions WHERE user_id=%s ORDER BY updated_at DESC LIMIT %s", (user_id,min(int(limit),100)))
            return [{'id':r[0],'role':r[1],'status':r[2],'created_at':r[3].isoformat() if r[3] else None,'questions':r[4]} for r in cur.fetchall()]
