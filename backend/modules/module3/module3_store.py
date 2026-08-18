import json
import uuid
from backend.auth.auth_db import db_connect

SCHEMA = """
CREATE TABLE IF NOT EXISTS module3_sessions(
 id UUID PRIMARY KEY,
 user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
 role TEXT NOT NULL,
 state JSONB NOT NULL,
 created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
 updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
 completed_at TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_module3_sessions_user ON module3_sessions(user_id, updated_at DESC);
"""

def init_module3_db():
    with db_connect() as conn:
        with conn.cursor() as cur:
            cur.execute(SCHEMA)

def create_session(user_id, role, state):
    sid = uuid.uuid4()
    with db_connect() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO module3_sessions(id,user_id,role,state) VALUES(%s,%s,%s,%s)", (sid, user_id, role, json.dumps(state)))
    return str(sid)

def get_session(session_id, user_id):
    try: sid = uuid.UUID(str(session_id))
    except (ValueError, TypeError, AttributeError): return None
    with db_connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id,role,state,completed_at FROM module3_sessions WHERE id=%s AND user_id=%s", (sid, user_id))
            row = cur.fetchone()
    if not row: return None
    state = row[2] or {}
    state['id'] = str(row[0]); state['role'] = row[1]; state['completed_at'] = row[3].isoformat() if row[3] else None
    return state

def save_session(session_id, user_id, state, completed=False):
    try: sid = uuid.UUID(str(session_id))
    except (ValueError, TypeError, AttributeError): raise ValueError('invalid_session_id')
    with db_connect() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE module3_sessions SET state=%s,updated_at=NOW(),completed_at=CASE WHEN %s THEN COALESCE(completed_at,NOW()) ELSE completed_at END WHERE id=%s AND user_id=%s", (json.dumps(state), completed, sid, user_id))
            if cur.rowcount != 1: raise LookupError('session_not_found')

def latest_session(user_id):
    with db_connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id,role,state,completed_at FROM module3_sessions WHERE user_id=%s ORDER BY updated_at DESC LIMIT 1", (user_id,))
            row = cur.fetchone()
    if not row: return None
    state = row[2] or {}; state['id']=str(row[0]); state['role']=row[1]; state['completed_at']=row[3].isoformat() if row[3] else None
    return state
