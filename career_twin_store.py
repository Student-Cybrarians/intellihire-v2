import hashlib
import json
from auth_db import db_connect


def _fingerprint(value):
    return hashlib.sha256(str(value or '').strip().encode('utf-8')).hexdigest()


def ensure_schema():
    with db_connect() as conn:
        with conn.cursor() as cur:
            cur.execute('''CREATE TABLE IF NOT EXISTS career_twins (
                id BIGSERIAL PRIMARY KEY,
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                role TEXT NOT NULL DEFAULT '',
                resume_fingerprint TEXT NOT NULL,
                jd_fingerprint TEXT NOT NULL,
                payload JSONB NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                UNIQUE(user_id, resume_fingerprint, jd_fingerprint)
            )''')
            cur.execute('CREATE INDEX IF NOT EXISTS idx_career_twins_user_updated ON career_twins(user_id, updated_at DESC)')


def save(user_id, twin, resume, jd):
    ensure_schema()
    resume_fp = _fingerprint(resume)
    jd_fp = _fingerprint(jd)
    payload = json.dumps(twin, ensure_ascii=False)
    with db_connect() as conn:
        with conn.cursor() as cur:
            cur.execute('''INSERT INTO career_twins
                (user_id, role, resume_fingerprint, jd_fingerprint, payload, updated_at)
                VALUES (%s,%s,%s,%s,%s,NOW())
                ON CONFLICT (user_id, resume_fingerprint, jd_fingerprint)
                DO UPDATE SET role=EXCLUDED.role, payload=EXCLUDED.payload, updated_at=NOW()''',
                (user_id, twin.get('role', ''), resume_fp, jd_fp, payload))
    return {'saved': True, 'resume_fingerprint': resume_fp, 'jd_fingerprint': jd_fp}


def latest(user_id):
    ensure_schema()
    with db_connect() as conn:
        with conn.cursor() as cur:
            cur.execute('''SELECT payload, updated_at FROM career_twins
                           WHERE user_id=%s ORDER BY updated_at DESC LIMIT 1''', (user_id,))
            row = cur.fetchone()
    if not row:
        return None
    payload = row[0] if isinstance(row[0], dict) else json.loads(row[0])
    payload['updated_at'] = row[1].isoformat() if row[1] else None
    return payload
