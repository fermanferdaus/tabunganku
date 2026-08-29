from flask import Blueprint, render_template, redirect, url_for, request
from middleware.auth import login_required
from services.auth_service import decode_token

web_bp = Blueprint('web', __name__)


@web_bp.route('/')
def root():
    """Redirect ke dashboard jika sudah login, ke login jika belum."""
    token = request.cookies.get('access_token')
    if token:
        try:
            decode_token(token)
            return redirect(url_for('web.dashboard'))
        except Exception:
            pass
    return redirect(url_for('web.login_page'))


@web_bp.route('/login')
def login_page():
    """Render halaman login. Skip jika sudah login."""
    token = request.cookies.get('access_token')
    if token:
        try:
            decode_token(token)
            return redirect(url_for('web.dashboard'))
        except Exception:
            pass
    return render_template('login.html')


@web_bp.route('/dashboard')
@login_required
def dashboard():
    """Halaman dashboard utama."""
    return render_template('index.html', user=request.current_user)
