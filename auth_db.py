import hashlib
import json
import os
import secrets
import uuid
from datetime import datetime, timedelta, timezone
try:
    import psycopg
except ImportError:
    psycopg=None
SCHEMA="""CREATE TABLE IF NOT EXISTS users(id UUID PRIMARY KEY,name TEXT,email TEXT NOT NULL UNIQUE,picture TEXT,provider TEXT NOT NULL,provider_id TEXT NOT NULL,role TEXT NOT NULL DEFAULT 'USER' CHECK(role IN ('USER','ADMIN')),status TEXT NOT NULL DEFAULT 'ACTIVE' CHECK(status IN ('ACTIVE','SUSPENDED','DISABLED')),created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),last_login_at TIMESTAMPTZ,UNIQUE(provider,provider_id));CREATE TABLE IF NOT EXISTS sessions(id UUID PRIMARY KEY,user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,session_token_hash TEXT NOT NULL UNIQUE,expires_at TIMESTAMPTZ NOT NULL,created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),last_used_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),ip_address TEXT,user_agent TEXT,revoked_at TIMESTAMPTZ);CREATE TABLE IF NOT EXISTS audit_logs(id BIGSERIAL PRIMARY KEY,event TEXT NOT NULL,actor_user_id UUID REFERENCES users(id) ON DELETE SET NULL,target_user_id UUID REFERENCES users(id) ON DELETE SET NULL,created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),ip_address TEXT,user_agent TEXT,metadata JSONB NOT NULL DEFAULT '{}'::jsonb);"""
def db_connect():
    if psycopg is None: raise RuntimeError('PostgreSQL driver is not installed')
    url=os.getenv('DATABASE_URL')
    if not url: raise RuntimeError('DATABASE_URL is not configured')
    return psycopg.connect(url)
def init_db():
    with db_connect() as conn:
        with conn.cursor() as cur: cur.execute(SCHEMA)
def token_hash(token): return hashlib.sha256(token.encode()).hexdigest()
def get_or_create_google_user(sub,email,name,picture):
    with db_connect() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT id,email,name,picture,role,status FROM users WHERE provider=%s AND provider_id=%s',('google',sub)); row=cur.fetchone()
            if row:
                if row[5]!='ACTIVE': return {'id':str(row[0]),'email':row[1],'name':row[2],'picture':row[3],'role':row[4],'status':row[5]}
                cur.execute('UPDATE users SET name=%s,picture=%s,last_login_at=NOW(),updated_at=NOW() WHERE id=%s',(name,picture,row[0])); return {'id':str(row[0]),'email':row[1],'name':name,'picture':picture,'role':row[4],'status':row[5]}
            uid=uuid.uuid4();cur.execute('INSERT INTO users(id,name,email,picture,provider,provider_id,last_login_at) VALUES(%s,%s,%s,%s,%s,%s,NOW())',(uid,name,email,picture,'google',sub));return {'id':str(uid),'email':email,'name':name,'picture':picture,'role':'USER','status':'ACTIVE'}
def create_session(user_id,ip,user_agent,days=7):
    raw=secrets.token_urlsafe(48);sid=uuid.uuid4();expires=datetime.now(timezone.utc)+timedelta(days=days)
    with db_connect() as conn:
        with conn.cursor() as cur:
            cur.execute('UPDATE sessions SET revoked_at=NOW() WHERE user_id=%s AND revoked_at IS NULL',(user_id,));cur.execute('INSERT INTO sessions(id,user_id,session_token_hash,expires_at,ip_address,user_agent) VALUES(%s,%s,%s,%s,%s,%s)',(sid,user_id,token_hash(raw),expires,ip,user_agent))
    return raw,expires
def get_session(raw):
    if not raw:return None
    h=token_hash(raw)
    with db_connect() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT u.id,u.email,u.name,u.picture,u.role,u.status,s.expires_at FROM sessions s JOIN users u ON u.id=s.user_id WHERE s.session_token_hash=%s AND s.revoked_at IS NULL AND s.expires_at>NOW()',(h,));row=cur.fetchone()
            if not row:return None
            cur.execute('UPDATE sessions SET last_used_at=NOW() WHERE session_token_hash=%s',(h,));return {'id':str(row[0]),'email':row[1],'name':row[2],'picture':row[3],'role':row[4],'status':row[5],'expires_at':row[6].isoformat()}
def revoke_session(raw):
    if not raw:return
    with db_connect() as conn:
        with conn.cursor() as cur:cur.execute('UPDATE sessions SET revoked_at=NOW() WHERE session_token_hash=%s',(token_hash(raw),))
def audit(event,actor_user_id=None,target_user_id=None,ip_address=None,user_agent=None,metadata=None):
    with db_connect() as conn:
        with conn.cursor() as cur:cur.execute('INSERT INTO audit_logs(event,actor_user_id,target_user_id,ip_address,user_agent,metadata) VALUES(%s,%s,%s,%s,%s,%s)',(event,actor_user_id,target_user_id,ip_address,user_agent,json.dumps(metadata or {})))
