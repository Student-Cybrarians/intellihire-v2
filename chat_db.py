import json

from auth_db import db_connect, init_db

CHAT_SCHEMA = """
CREATE TABLE IF NOT EXISTS support_conversations (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subject TEXT NOT NULL DEFAULT 'Support request',
    status TEXT NOT NULL DEFAULT 'OPEN' CHECK(status IN ('OPEN','IN_PROGRESS','RESOLVED','CLOSED')),
    priority TEXT NOT NULL DEFAULT 'NORMAL' CHECK(priority IN ('LOW','NORMAL','HIGH','URGENT')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_message_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_support_conversations_user ON support_conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_support_conversations_status ON support_conversations(status);
CREATE INDEX IF NOT EXISTS idx_support_conversations_updated ON support_conversations(updated_at DESC);
CREATE TABLE IF NOT EXISTS support_messages (
    id BIGSERIAL PRIMARY KEY,
    conversation_id UUID NOT NULL REFERENCES support_conversations(id) ON DELETE CASCADE,
    sender_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    sender_role TEXT NOT NULL CHECK(sender_role IN ('USER','ADMIN','ASSISTANT')),
    body TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_support_messages_conversation ON support_messages(conversation_id, created_at);
"""

def init_chat_db():
    init_db()
    with db_connect() as conn:
        with conn.cursor() as cur:
            cur.execute(CHAT_SCHEMA)


def create_conversation(user_id, subject='Support request', priority='NORMAL'):
    import uuid
    init_chat_db()
    priority = priority if priority in {'LOW','NORMAL','HIGH','URGENT'} else 'NORMAL'
    cid = uuid.uuid4()
    with db_connect() as conn:
        with conn.cursor() as cur:
            cur.execute('INSERT INTO support_conversations(id,user_id,subject,priority) VALUES(%s,%s,%s,%s)', (cid, user_id, subject[:200], priority))
    return str(cid)


def list_conversations(user_id=None, status=None, limit=100):
    init_chat_db()
    with db_connect() as conn:
        with conn.cursor() as cur:
            if user_id and status:
                cur.execute('''SELECT c.id,c.user_id,u.name,u.email,c.subject,c.status,c.priority,c.created_at,c.updated_at,c.last_message_at,
                    (SELECT COUNT(*) FROM support_messages m WHERE m.conversation_id=c.id) FROM support_conversations c JOIN users u ON u.id=c.user_id
                    WHERE c.user_id=%s AND c.status=%s ORDER BY c.last_message_at DESC LIMIT %s''', (user_id,status,int(limit)))
            elif user_id:
                cur.execute('''SELECT c.id,c.user_id,u.name,u.email,c.subject,c.status,c.priority,c.created_at,c.updated_at,c.last_message_at,
                    (SELECT COUNT(*) FROM support_messages m WHERE m.conversation_id=c.id) FROM support_conversations c JOIN users u ON u.id=c.user_id
                    WHERE c.user_id=%s ORDER BY c.last_message_at DESC LIMIT %s''', (user_id,int(limit)))
            elif status:
                cur.execute('''SELECT c.id,c.user_id,u.name,u.email,c.subject,c.status,c.priority,c.created_at,c.updated_at,c.last_message_at,
                    (SELECT COUNT(*) FROM support_messages m WHERE m.conversation_id=c.id) FROM support_conversations c JOIN users u ON u.id=c.user_id
                    WHERE c.status=%s ORDER BY c.last_message_at DESC LIMIT %s''', (status,int(limit)))
            else:
                cur.execute('''SELECT c.id,c.user_id,u.name,u.email,c.subject,c.status,c.priority,c.created_at,c.updated_at,c.last_message_at,
                    (SELECT COUNT(*) FROM support_messages m WHERE m.conversation_id=c.id) FROM support_conversations c JOIN users u ON u.id=c.user_id
                    ORDER BY c.last_message_at DESC LIMIT %s''', (int(limit),))
            rows=cur.fetchall()
    return [
        {'id':str(r[0]),'user_id':str(r[1]),'user_name':r[2],'user_email':r[3],'subject':r[4],'status':r[5],'priority':r[6],
         'created_at':r[7].isoformat(),'updated_at':r[8].isoformat(),'last_message_at':r[9].isoformat(),'message_count':r[10]}
        for r in rows
    ]


def get_conversation(conversation_id):
    init_chat_db()
    with db_connect() as conn:
        with conn.cursor() as cur:
            cur.execute('''SELECT c.id,c.user_id,u.name,u.email,c.subject,c.status,c.priority,c.created_at,c.updated_at,c.last_message_at
                          FROM support_conversations c JOIN users u ON u.id=c.user_id WHERE c.id=%s''', (conversation_id,))
            r=cur.fetchone()
    if not r:return None
    return {'id':str(r[0]),'user_id':str(r[1]),'user_name':r[2],'user_email':r[3],'subject':r[4],'status':r[5],'priority':r[6],
            'created_at':r[7].isoformat(),'updated_at':r[8].isoformat(),'last_message_at':r[9].isoformat()}


def get_messages(conversation_id, limit=500):
    init_chat_db()
    with db_connect() as conn:
        with conn.cursor() as cur:
            cur.execute('''SELECT m.id,m.sender_user_id,m.sender_role,m.body,m.metadata,m.created_at,u.name,u.email
                          FROM support_messages m LEFT JOIN users u ON u.id=m.sender_user_id
                          WHERE m.conversation_id=%s ORDER BY m.created_at ASC LIMIT %s''', (conversation_id,int(limit)))
            rows=cur.fetchall()
    return [{'id':r[0],'sender_user_id':str(r[1]) if r[1] else None,'sender_role':r[2],'body':r[3],
             'metadata':r[4] or {},'created_at':r[5].isoformat(),'sender_name':r[6] or r[7] or r[2]} for r in rows]


def add_message(conversation_id, sender_user_id, sender_role, body, metadata=None):
    init_chat_db()
    body = str(body or '').strip()
    if not body or len(body)>8000: raise ValueError('message_length_invalid')
    if sender_role not in {'USER','ADMIN','ASSISTANT'}: raise ValueError('invalid_sender_role')
    with db_connect() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT id FROM support_conversations WHERE id=%s', (conversation_id,))
            if not cur.fetchone(): raise ValueError('conversation_not_found')
            cur.execute('''INSERT INTO support_messages(conversation_id,sender_user_id,sender_role,body,metadata)
                           VALUES(%s,%s,%s,%s,%s) RETURNING id,created_at''', (conversation_id,sender_user_id,sender_role,body,json.dumps(metadata or {})))
            mid,created=cur.fetchone()
            cur.execute('UPDATE support_conversations SET updated_at=NOW(),last_message_at=NOW(),status=CASE WHEN status=''CLOSED'' THEN ''OPEN'' ELSE status END WHERE id=%s', (conversation_id,))
    return {'id':mid,'created_at':created.isoformat()}


def update_conversation(conversation_id, status=None, priority=None, subject=None):
    init_chat_db()
    allowed_status={'OPEN','IN_PROGRESS','RESOLVED','CLOSED'}
    allowed_priority={'LOW','NORMAL','HIGH','URGENT'}
    sets=[];vals=[]
    if status in allowed_status: sets.append('status=%s'); vals.append(status)
    if priority in allowed_priority: sets.append('priority=%s'); vals.append(priority)
    if subject is not None: sets.append('subject=%s'); vals.append(str(subject)[:200])
    if not sets:return get_conversation(conversation_id)
    sets.append('updated_at=NOW()');vals.append(conversation_id)
    with db_connect() as conn:
        with conn.cursor() as cur:cur.execute('UPDATE support_conversations SET '+','.join(sets)+' WHERE id=%s',tuple(vals))
    return get_conversation(conversation_id)
