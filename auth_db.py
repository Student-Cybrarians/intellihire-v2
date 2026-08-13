import hashlib
import hmac
import json
import os
import secrets
import uuid
from datetime import datetime, timedelta, timezone
try:
    import psycopg
except ImportError:
    psycopg=None
SCHEMA="""CREATE TABLE IF NOT EXISTS users(id UUID PRIMARY KEY,name TEXT,email TEXT NOT NULL UNIQUE,picture TEXT,provider TEXT NOT NULL,provider_id TEXT NOT NULL,role TEXT NOT NULL DEFAULT 'USER' CHECK(role IN ('USER','ADMIN')),status TEXT NOT NULL DEFAULT 'ACTIVE' CHECK(status IN ('ACTIVE','SUSPENDED','DISABLED')),created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),last_login_at TIMESTAMPTZ,UNIQUE(provider,provider_id));CREATE TABLE IF NOT EXISTS sessions(id UUID PRIMARY KEY,user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,session_token_hash TEXT NOT NULL UNIQUE,expires_at TIMESTAMPTZ NOT NULL,created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),last_used_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),ip_address TEXT,user_agent TEXT,revoked_at TIMESTAMPTZ);CREATE TABLE IF NOT EXISTS audit_logs(id BIGSERIAL PRIMARY KEY,event TEXT NOT NULL,actor_user_id UUID REFERENCES users(id) ON DELETE SET NULL,target_user_id UUID REFERENCES users(id) ON DELETE SET NULL,created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),ip_address TEXT,user_agent TEXT,metadata JSONB NOT NULL DEFAULT '{}'::jsonb);CREATE TABLE IF NOT EXISTS module_performance(id BIGSERIAL PRIMARY KEY,user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,module TEXT NOT NULL CHECK(module IN ('module1','module2','module3','module4','module5')),score DOUBLE PRECISION NOT NULL CHECK(score>=0 AND score<=100),payload JSONB NOT NULL DEFAULT '{}'::jsonb,completed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),UNIQUE(user_id,module));CREATE INDEX IF NOT EXISTS idx_module_performance_user ON module_performance(user_id);CREATE INDEX IF NOT EXISTS idx_module_performance_module ON module_performance(module);"""
def db_connect():
    if psycopg is None: raise RuntimeError('PostgreSQL driver is not installed')
    url=os.getenv('DATABASE_URL')
    if not url: raise RuntimeError('DATABASE_URL is not configured')
    return psycopg.connect(url)
def init_db():
    with db_connect() as conn:
        with conn.cursor() as cur: cur.execute(SCHEMA)
def token_hash(token): return hashlib.sha256(token.encode()).hexdigest()
def _is_admin_email(email):
    configured=os.getenv('ADMIN_EMAIL','').strip().lower()
    return bool(configured and email and hmac.compare_digest(configured,email.strip().lower()))
def get_or_create_google_user(sub,email,name,picture):
    init_db()
    with db_connect() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT id,email,name,picture,role,status FROM users WHERE provider=%s AND provider_id=%s',('google',sub)); row=cur.fetchone()
            desired_role='ADMIN' if _is_admin_email(email) else 'USER'
            if row:
                if row[5]!='ACTIVE': return {'id':str(row[0]),'email':row[1],'name':row[2],'picture':row[3],'role':row[4],'status':row[5]}
                if row[4]=='ADMIN' or desired_role=='ADMIN': desired_role='ADMIN'
                cur.execute('UPDATE users SET name=%s,picture=%s,role=%s,last_login_at=NOW(),updated_at=NOW() WHERE id=%s',(name,picture,desired_role,row[0]));return {'id':str(row[0]),'email':row[1],'name':name,'picture':picture,'role':desired_role,'status':row[5]}
            uid=uuid.uuid4();cur.execute('INSERT INTO users(id,name,email,picture,provider,provider_id,role,last_login_at) VALUES(%s,%s,%s,%s,%s,%s,%s,NOW())',(uid,name,email,picture,'google',sub,desired_role));return {'id':str(uid),'email':email,'name':name,'picture':picture,'role':desired_role,'status':'ACTIVE'}
def create_session(user_id,ip,user_agent,days=7):
    raw=secrets.token_urlsafe(48);sid=uuid.uuid4();expires=datetime.now(timezone.utc)+timedelta(days=days)
    with db_connect() as conn:
        with conn.cursor() as cur:
            cur.execute('UPDATE sessions SET revoked_at=NOW() WHERE user_id=%s AND revoked_at IS NULL',(user_id,));cur.execute('INSERT INTO sessions(id,user_id,session_token_hash,expires_at,ip_address,user_agent) VALUES(%s,%s,%s,%s,%s,%s)',(sid,user_id,token_hash(raw),expires,ip,user_agent))
    return raw,expires
def get_session(raw):
    if not raw:return None
    h=token_hash(raw)
    try:
        with db_connect() as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT u.id,u.email,u.name,u.picture,u.role,u.status,s.expires_at FROM sessions s JOIN users u ON u.id=s.user_id WHERE s.session_token_hash=%s AND s.revoked_at IS NULL AND s.expires_at>NOW()',(h,));row=cur.fetchone()
                if not row:return None
                cur.execute('UPDATE sessions SET last_used_at=NOW() WHERE session_token_hash=%s',(h,));return {'id':str(row[0]),'email':row[1],'name':row[2],'picture':row[3],'role':row[4],'status':row[5],'expires_at':row[6].isoformat()}
    except Exception:return None
def revoke_session(raw):
    if not raw:return
    with db_connect() as conn:
        with conn.cursor() as cur:cur.execute('UPDATE sessions SET revoked_at=NOW() WHERE session_token_hash=%s',(token_hash(raw),))
def audit(event,actor_user_id=None,target_user_id=None,ip_address=None,user_agent=None,metadata=None):
    with db_connect() as conn:
        with conn.cursor() as cur:cur.execute('INSERT INTO audit_logs(event,actor_user_id,target_user_id,ip_address,user_agent,metadata) VALUES(%s,%s,%s,%s,%s,%s)',(event,actor_user_id,target_user_id,ip_address,user_agent,json.dumps(metadata or {})))
def record_performance(user_id,module,score,payload=None):
    if module not in {'module1','module2','module3','module4','module5'}: raise ValueError('invalid_module')
    value=max(0.0,min(100.0,float(score)))
    with db_connect() as conn:
        with conn.cursor() as cur:cur.execute('INSERT INTO module_performance(user_id,module,score,payload,completed_at) VALUES(%s,%s,%s,%s,NOW()) ON CONFLICT(user_id,module) DO UPDATE SET score=EXCLUDED.score,payload=EXCLUDED.payload,completed_at=NOW()', (user_id,module,value,json.dumps(payload or {})))
def get_user_performance(user_id):
    result={m:None for m in ('module1','module2','module3','module4','module5')}
    with db_connect() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT module,score,payload,completed_at FROM module_performance WHERE user_id=%s',(user_id,))
            for module,score,payload,completed_at in cur.fetchall():result[module]={'score':float(score),'payload':payload or {},'completed_at':completed_at.isoformat() if completed_at else None}
    return result
def list_user_summaries(search=None):
    init_db()
    with db_connect() as conn:
        with conn.cursor() as cur:
            if search:
                like=f'%{search}%';cur.execute('SELECT id,name,email,role,status,created_at,last_login_at FROM users WHERE name ILIKE %s OR email ILIKE %s ORDER BY created_at DESC',(like,like))
            else:cur.execute('SELECT id,name,email,role,status,created_at,last_login_at FROM users ORDER BY created_at DESC')
            rows=cur.fetchall()
    result=[]
    for row in rows:
        scores=get_user_performance(str(row[0]));vals=[v['score'] for v in scores.values() if v]
        result.append({'id':str(row[0]),'name':row[1],'email':row[2],'role':row[3],'status':row[4],'created_at':row[5].isoformat() if row[5] else None,'last_login_at':row[6].isoformat() if row[6] else None,'scores':scores,'overall':round(sum(vals)/len(vals),1) if vals else None})
    return result
def get_user_activity(user_id=None,limit=100):
    init_db()
    with db_connect() as conn:
        with conn.cursor() as cur:
            if user_id:cur.execute('SELECT event,actor_user_id,target_user_id,created_at,metadata FROM audit_logs WHERE actor_user_id=%s OR target_user_id=%s ORDER BY created_at DESC LIMIT %s',(user_id,user_id,int(limit)))
            else:cur.execute('SELECT event,actor_user_id,target_user_id,created_at,metadata FROM audit_logs ORDER BY created_at DESC LIMIT %s',(int(limit),))
            rows=cur.fetchall()
    return [{'event':r[0],'actor_user_id':str(r[1]) if r[1] else None,'target_user_id':str(r[2]) if r[2] else None,'created_at':r[3].isoformat() if r[3] else None,'metadata':r[4] or {}} for r in rows]
