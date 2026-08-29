from functools import wraps
from flask import request, redirect, url_for, jsonify
from services.auth_service import decode_token


def login_required(f):
    """Decorator: cek JWT dari cookie access_token."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('access_token')
        if not token:
            return _handle_unauthorized(request)

        try:
            payload = decode_token(token)
            request.current_user = payload
        except Exception:
            return _handle_unauthorized(request)

        return f(*args, **kwargs)
    return decorated


def _handle_unauthorized(req):
    """API request → 401 JSON, web request → redirect login."""
    if req.path.startswith('/api/'):
        return jsonify({
            'success': False,
            'message': 'Unauthorized',
            'data': None,
            'errors': None
        }), 401
    return redirect(url_for('web.login_page'))
