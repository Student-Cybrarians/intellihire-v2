import os
import time
import uuid
from collections import defaultdict, deque
from threading import Lock

_WINDOW_SECONDS = int(os.getenv('RATE_LIMIT_WINDOW_SECONDS', '60'))
_DEFAULT_LIMIT = int(os.getenv('RATE_LIMIT_REQUESTS', '60'))
_BUCKETS = defaultdict(deque)
_LOCK = Lock()


def request_id():
    return uuid.uuid4().hex


def client_key(request):
    # Prefer an explicitly configured trusted proxy header only when deployment opts in.
    if os.getenv('TRUST_PROXY_HEADERS', '').lower() == 'true':
        forwarded = request.headers.get('X-Forwarded-For', '').split(',')[0].strip()
        if forwarded:
            return forwarded
    return request.remote_addr or 'unknown'


def rate_limit(key, limit=None, window=None):
    limit = limit or _DEFAULT_LIMIT
    window = window or _WINDOW_SECONDS
    now = time.monotonic()
    bucket_key = f'{key}:{limit}:{window}'
    with _LOCK:
        bucket = _BUCKETS[bucket_key]
        cutoff = now - window
        while bucket and bucket[0] <= cutoff:
            bucket.popleft()
        if len(bucket) >= limit:
            retry_after = max(1, int(window - (now - bucket[0])))
            return False, retry_after
        bucket.append(now)
        return True, 0


def security_headers(response):
    response.headers.setdefault('X-Content-Type-Options', 'nosniff')
    response.headers.setdefault('X-Frame-Options', 'DENY')
    response.headers.setdefault('Referrer-Policy', 'strict-origin-when-cross-origin')
    response.headers.setdefault('Permissions-Policy', 'camera=(), microphone=(self), geolocation=()')
    response.headers.setdefault('Content-Security-Policy', "default-src 'self'; base-uri 'self'; frame-ancestors 'none'; object-src 'none'; form-action 'self'; img-src 'self' data: https:; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline' https:; connect-src 'self' https:; font-src 'self' data: https:")
    if os.getenv('FLASK_ENV', '').lower() == 'production' or os.getenv('VERCEL'):
        response.headers.setdefault('Strict-Transport-Security', 'max-age=31536000; includeSubDomains')
    return response
