import json
import uuid
from backend.auth.auth_db import db_connect

SCHEMA = """
CREATE TABLE IF NOT EXISTS module2_assessments(
 id UUID PRIMARY KEY,
 user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
 section TEXT NOT NULL DEFAULT '',
 target_questions INTEGER NOT NULL CHECK(target_questions BETWEEN 1 AND 100),
 ability DOUBLE PRECISION NOT NULL DEFAULT 0,
 answered_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
 events JSONB NOT NULL DEFAULT '[]'::jsonb,
 status TEXT NOT NULL DEFAULT 'ACTIVE' CHECK(status IN ('ACTIVE','COMPLETED','ABANDONED')),
 created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
 updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
 completed_at TIMESTAMPTZ,
 UNIQUE(user_id, id)
);
CREATE INDEX IF NOT EXISTS idx_module2_assessments_user_updated ON module2_assessments(user_id, updated_at DESC);
"""

def init_module2_store():
    with db_connect() as conn:
        with conn.cursor() as cur:
            cur.execute(SCHEMA)

def _decode(value):
    if isinstance(value, str):
        return json.loads(value)
    return value

def create_assessment(user_id, section='', target_questions=8):
    target_questions = int(target_questions)
    if not 1 <= target_questions <= 100:
        raise ValueError('invalid_target_questions')
    init_module2_store()
    assessment_id = uuid.uuid4()
    with db_connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO module2_assessments(id,user_id,section,target_questions) VALUES(%s,%s,%s,%s)",
                (assessment_id, user_id, section or '', target_questions),
            )
    return get_assessment(user_id, str(assessment_id))

def _row_to_assessment(row):
    return {
        'id': str(row[0]), 'section': row[1], 'target_questions': row[2],
        'ability': float(row[3]), 'answered_ids': _decode(row[4]) or [],
        'events': _decode(row[5]) or [], 'status': row[6],
        'created_at': row[7].isoformat() if row[7] else None,
        'updated_at': row[8].isoformat() if row[8] else None,
        'completed_at': row[9].isoformat() if row[9] else None,
    }

def get_assessment(user_id, assessment_id):
    try:
        aid = uuid.UUID(str(assessment_id))
    except (ValueError, TypeError):
        return None
    with db_connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id,section,target_questions,ability,answered_ids,events,status,created_at,updated_at,completed_at FROM module2_assessments WHERE id=%s AND user_id=%s",
                (aid, user_id),
            )
            row = cur.fetchone()
    return _row_to_assessment(row) if row else None

def save_answer(user_id, assessment_id, event):
    try:
        aid = uuid.UUID(str(assessment_id))
    except (ValueError, TypeError):
        raise LookupError('assessment_not_found')
    qid = event.get('question', {}).get('id')
    if not qid:
        raise ValueError('invalid_event')
    with db_connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id,section,target_questions,ability,answered_ids,events,status,created_at,updated_at,completed_at FROM module2_assessments WHERE id=%s AND user_id=%s FOR UPDATE",
                (aid, user_id),
            )
            row = cur.fetchone()
            if not row:
                raise LookupError('assessment_not_found')
            assessment = _row_to_assessment(row)
            if assessment['status'] != 'ACTIVE':
                raise ValueError('assessment_not_active')
            if qid in assessment['answered_ids']:
                raise ValueError('question_already_answered')
            answered = assessment['answered_ids'] + [qid]
            events = assessment['events'] + [event]
            ability = float(event.get('ability_after', assessment['ability']))
            completed = len(events) >= assessment['target_questions']
            status = 'COMPLETED' if completed else 'ACTIVE'
            cur.execute(
                "UPDATE module2_assessments SET ability=%s,answered_ids=%s,events=%s,status=%s,updated_at=NOW(),completed_at=CASE WHEN %s THEN NOW() ELSE completed_at END WHERE id=%s AND user_id=%s",
                (ability, json.dumps(answered), json.dumps(events), status, completed, aid, user_id),
            )
    return get_assessment(user_id, str(aid))

def abandon_assessment(user_id, assessment_id):
    try:
        aid = uuid.UUID(str(assessment_id))
    except (ValueError, TypeError):
        raise ValueError('assessment_not_found')
    with db_connect() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE module2_assessments SET status='ABANDONED',updated_at=NOW() WHERE id=%s AND user_id=%s AND status='ACTIVE'", (aid, user_id))
    return get_assessment(user_id, assessment_id)

def latest_assessment(user_id):
    with db_connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM module2_assessments WHERE user_id=%s ORDER BY updated_at DESC LIMIT 1", (user_id,))
            row = cur.fetchone()
    return get_assessment(user_id, row[0]) if row else None
