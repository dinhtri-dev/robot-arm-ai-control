"""Single-process, loopback-only archive demonstrations; not a deployment layer."""
import base64
import functools
import hashlib
import html
import json
import re
import secrets
import threading
import time
from collections import defaultdict, deque
from flask import abort, request
from flask_socketio import emit

ORIGINS = ['http://127.0.0.1:5000', 'http://localhost:5000']
TOKEN = secrets.token_urlsafe(32)
_hits = defaultdict(deque)
_lock = threading.Lock()

def _local():
    return request.remote_addr in ('127.0.0.1', '::1') and request.host in ('127.0.0.1:5000', 'localhost:5000')

def _allow(key, limit):
    now = time.monotonic()
    with _lock:
        if len(_hits) > 2048:
            _hits.clear()
        bucket = _hits[key]
        while bucket and bucket[0] < now - 60:
            bucket.popleft()
        if len(bucket) >= limit:
            return False
        bucket.append(now)
        return True

def install(app):
    app.config.update(SECRET_KEY=secrets.token_hex(32), MAX_CONTENT_LENGTH=1024*1024,
                      DEBUG=False, PROPAGATE_EXCEPTIONS=False,
                      SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Strict')
    @app.before_request
    def check():
        if not _local() or request.headers.get('Origin', ORIGINS[0]) not in ORIGINS:
            abort(403)
        if not _allow(('http', request.remote_addr), 120):
            abort(429)
        sid = (request.view_args or {}).get('session_id')
        if sid is not None and not re.fullmatch(r'[0-9a-f]{8}', sid):
            abort(400)
    @app.after_request
    def headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'no-referrer'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Cache-Control'] = 'no-store'
        nonce = secrets.token_urlsafe(24)
        hashes = []
        if response.mimetype == 'text/html' and not response.is_streamed:
            content = response.get_data(as_text=True)
            for handler in re.findall(r'\bon\w+="([^"]*)"', content):
                digest = base64.b64encode(hashlib.sha256(html.unescape(handler).encode()).digest()).decode()
                hashes.append("'sha256-" + digest + "'")
            token_script = '<script nonce="' + nonce + '">window.YEAR2_ARCHIVE_TOKEN=' + json.dumps(TOKEN) + ';</script>'
            content = re.sub(r'<script(?=\s|>)', '<script nonce="' + nonce + '"', content)
            content = content.replace('<head>', '<head>' + token_script, 1)
            response.set_data(content)
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; script-src 'self' 'nonce-" + nonce + "' 'unsafe-hashes' " + ' '.join(hashes) +
            " https://cdn.socket.io https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; font-src 'self' https://cdnjs.cloudflare.com; "
            "img-src 'self' data:; connect-src 'self' ws://127.0.0.1:5000 ws://localhost:5000; "
            "object-src 'none'; base-uri 'self'; frame-ancestors 'none'")
        return response

def guarded(event):
    def decorate(fn):
        @functools.wraps(fn)
        def call(*args, **kwargs):
            if not _local() or not _allow(('socket', request.sid), 60):
                emit('status', {'msg': 'Request denied or rate limited'})
                return False
            data = args[0] if args else None
            valid = True
            if event == 'start_session':
                valid = isinstance(data, dict) and type(data.get('camera_id', 0)) is int and 0 <= data.get('camera_id', 0) <= 9
            elif event == 'control_command':
                valid = isinstance(data, dict) and data.get('axis') in ('X', 'Y', 'Z') and type(data.get('val')) is int and abs(data['val']) <= 50
            elif event == 'gripper_command':
                valid = isinstance(data, dict) and data.get('state') in ('open', 'close')
            else:
                valid = not args
            if not valid:
                emit('status', {'msg': 'Invalid request'})
                return False
            return fn(*args, **kwargs)
        return call
    return decorate

def secure_connect(socketio, previous=None):
    @socketio.on('connect')
    def connect(auth=None):
        if not _local() or not isinstance(auth, dict) or not secrets.compare_digest(str(auth.get('token', '')), TOKEN):
            return False
        if previous:
            previous()
