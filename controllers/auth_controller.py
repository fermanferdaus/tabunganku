from flask import Blueprint, request, redirect, url_for, render_template, make_response, jsonify
from services.db import get_db_connection
from services.auth_service import verify_password, generate_token, hash_password, is_valid_bcrypt_hash
from middleware.auth import login_required
from validators.auth_validator import validate_login, validate_change_password

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    """Proses login: validasi credentials, set JWT cookie."""
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')

    errors = validate_login(username, password)
    if errors:
        return render_template('login.html', error=errors[0])

    try:
        with get_db_connection().cursor() as cursor:
            cursor.execute(
                "SELECT id, username, password FROM tb_login WHERE username = %s",
                (username,)
            )
            user = cursor.fetchone()

        if not user or not verify_password(password, user['password']):
            return render_template('login.html', error='Username atau password salah!')

        # Auto-upgrade jika password di DB belum berupa 60-character bcrypt hash
        if not is_valid_bcrypt_hash(user['password']):
            try:
                new_hashed = hash_password(password)
                conn = get_db_connection()
                with conn.cursor() as cur:
                    cur.execute(
                        "UPDATE tb_login SET password = %s WHERE id = %s",
                        (new_hashed, user['id'])
                    )
                    conn.commit()
            except Exception as upgrade_err:
                print(f"[Auth Warning] Gagal auto-upgrade password: {upgrade_err}")

        token = generate_token(user['id'], user['username'])
        response = make_response(redirect(url_for('web.dashboard')))
        response.set_cookie(
            'access_token', token,
            httponly=True, samesite='Lax', max_age=86400
        )
        return response

    except Exception as e:
        print(f"[Auth Error] Login: {e}")
        return render_template('login.html', error='Terjadi kesalahan server.')


@auth_bp.route('/logout')
def logout():
    """Clear JWT cookie dan redirect ke login."""
    response = make_response(redirect(url_for('web.login_page')))
    response.delete_cookie('access_token')
    return response


@auth_bp.route('/api/change-password', methods=['POST'])
@login_required
def change_password():
    """Ganti password user yang sedang login."""
    data = request.get_json() or {}
    old_password = data.get('old_password', '')
    new_password = data.get('new_password', '')
    confirm_password = data.get('confirm_password', '')

    errors = validate_change_password(old_password, new_password, confirm_password)
    if errors:
        return jsonify({
            'success': False,
            'message': errors[0],
            'data': None,
            'errors': errors
        }), 400

    try:
        user_id = request.current_user['user_id']
        with get_db_connection().cursor() as cursor:
            cursor.execute(
                "SELECT password FROM tb_login WHERE id = %s", (user_id,)
            )
            user = cursor.fetchone()

        if not user or not verify_password(old_password, user['password']):
            return jsonify({
                'success': False,
                'message': 'Password lama salah.',
                'data': None,
                'errors': ['Password lama salah.']
            }), 400

        hashed = hash_password(new_password)
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE tb_login SET password = %s WHERE id = %s",
                (hashed, user_id)
            )
            conn.commit()

        return jsonify({
            'success': True,
            'message': 'Password berhasil diubah.',
            'data': None,
            'errors': None
        })

    except Exception as e:
        print(f"[Auth Error] Change password: {e}")
        return jsonify({
            'success': False,
            'message': 'Terjadi kesalahan server.',
            'data': None,
            'errors': [str(e)]
        }), 500
