from flask import Blueprint, jsonify, request, render_template, abort

from chat_db import create_conversation, list_conversations, get_conversation, get_messages, add_message, update_conversation

support = Blueprint('support', __name__, url_prefix='/support')


def _auth():
    # Lazy import prevents the auth_routes <-> support blueprint import cycle.
    from auth_routes import current_user, require_auth
    return current_user, require_auth


def _audit(event, user_id, target=None, metadata=None):
    try:
        from auth_db import audit
        audit(event, user_id, target, request.remote_addr, request.headers.get('User-Agent',''), metadata or {})
    except Exception:
        pass


def _conversation_for_user(cid, user):
    conversation=get_conversation(cid)
    if not conversation: abort(404)
    if user.get('role') != 'ADMIN' and conversation['user_id'] != user['id']: abort(403)
    return conversation


@support.get('/')
def support_home():
    current_user, require_auth = _auth()
    user=current_user()
    if not user: return render_template('support.html', user=None)
    if user.get('role')=='ADMIN': return render_template('support_admin.html', user=user)
    return render_template('support.html', user=user)


@support.get('/api/conversations')
def conversations_api():
    current_user, require_auth = _auth()
    user,response=require_auth()
    if response:return response
    status=request.args.get('status')
    rows=list_conversations(None if user.get('role')=='ADMIN' else user['id'], status=status)
    return jsonify({'conversations':rows})


@support.post('/api/conversations')
def create_conversation_api():
    current_user, require_auth = _auth()
    user,response=require_auth('USER')
    if response:return response
    data=request.get_json(silent=True) or {}
    subject=str(data.get('subject') or 'Support request').strip()
    message=str(data.get('message') or '').strip()
    priority=str(data.get('priority') or 'NORMAL').upper()
    if not message:return jsonify({'error':'message_required'}),400
    cid=create_conversation(user['id'],subject,priority)
    add_message(cid,user['id'],'USER',message,{'channel':'dashboard_support'})
    _audit('SUPPORT_CONVERSATION_CREATED',user['id'],user['id'],{'conversation_id':cid,'subject':subject})
    # A deterministic assistant acknowledgement makes the support flow immediately visible while keeping the admin as the human responder.
    add_message(cid,None,'ASSISTANT','Thanks — your request is saved. An IntelliHire admin can review it and reply here. Please include the affected module, expected behavior, and what you observed when relevant.',{'type':'acknowledgement'})
    return jsonify({'conversation':get_conversation(cid),'messages':get_messages(cid)}),201


@support.get('/api/conversations/<cid>')
def conversation_api(cid):
    current_user, require_auth = _auth()
    user,response=require_auth()
    if response:return response
    c=_conversation_for_user(cid,user)
    return jsonify({'conversation':c,'messages':get_messages(cid)})


@support.post('/api/conversations/<cid>/messages')
def message_api(cid):
    current_user, require_auth = _auth()
    user,response=require_auth()
    if response:return response
    c=_conversation_for_user(cid,user)
    data=request.get_json(silent=True) or {}
    body=str(data.get('body') or '').strip()
    if not body:return jsonify({'error':'message_required'}),400
    result=add_message(cid,user['id'], 'ADMIN' if user.get('role')=='ADMIN' else 'USER', body, {'channel':'dashboard_support'})
    _audit('SUPPORT_MESSAGE_SENT',user['id'],c['user_id'],{'conversation_id':cid,'message_id':result['id']})
    return jsonify({'message':result,'conversation':get_conversation(cid)})


@support.patch('/api/conversations/<cid>')
def update_conversation_api(cid):
    current_user, require_auth = _auth()
    user,response=require_auth('ADMIN')
    if response:return response
    data=request.get_json(silent=True) or {}
    c=update_conversation(cid,data.get('status'),data.get('priority'),data.get('subject'))
    if not c:return jsonify({'error':'conversation_not_found'}),404
    _audit('SUPPORT_CONVERSATION_UPDATED',user['id'],c['user_id'],{'conversation_id':cid,'status':c['status'],'priority':c['priority']})
    return jsonify({'conversation':c})


@support.get('/admin')
def admin_support_page():
    current_user, require_auth = _auth()
    user,response=require_auth('ADMIN')
    if response:return response
    return render_template('support_admin.html',user=user)
