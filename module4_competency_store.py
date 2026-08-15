import json
from auth_db import db_connect, init_db

SCHEMA = """
CREATE TABLE IF NOT EXISTS module4_competencies (
 user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
 payload JSONB NOT NULL DEFAULT '{}'::jsonb,
 updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""

def ensure_schema():
    init_db()
    with db_connect() as conn:
        with conn.cursor() as cur:
            cur.execute(SCHEMA)

def save_competencies(user_id, payload):
    ensure_schema()
    with db_connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO module4_competencies(user_id,payload) VALUES(%s,%s) ON CONFLICT(user_id) DO UPDATE SET payload=EXCLUDED.payload,updated_at=NOW()",
                (user_id, json.dumps(payload or {})),
            )

def get_competencies(user_id):
    ensure_schema()
    with db_connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT payload,updated_at FROM module4_competencies WHERE user_id=%s", (user_id,))
            row = cur.fetchone()
    if not row:
        return None
    payload = row[0] or {}
    payload["updated_at"] = row[1].isoformat() if row[1] else None
    return payload
