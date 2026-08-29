import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from config.settings import Config


def is_valid_bcrypt_hash(hash_str):
    """Cek apakah string merupakan bcrypt hash yang valid (60 karakter)."""
    if not isinstance(hash_str, str):
        return False
    return (
        len(hash_str) == 60
        and (hash_str.startswith('$2b$') or hash_str.startswith('$2a$') or hash_str.startswith('$2y$'))
    )


def hash_password(plain_password):
    """Hash password dengan bcrypt (max 72 bytes UTF-8)."""
    pw_bytes = plain_password.encode('utf-8')[:72]
    return bcrypt.hashpw(
        pw_bytes,
        bcrypt.gensalt()
    ).decode('utf-8')


def verify_password(plain_password, hashed_password):
    """Verifikasi password terhadap bcrypt hash, dengan fallback plaintext yang aman."""
    if not hashed_password or not plain_password:
        return False

    if is_valid_bcrypt_hash(hashed_password):
        try:
            pw_bytes = plain_password.encode('utf-8')[:72]
            return bcrypt.checkpw(
                pw_bytes,
                hashed_password.encode('utf-8')
            )
        except Exception:
            pass

    # Fallback jika password di DB masih plaintext
    return plain_password == hashed_password


def generate_token(user_id, username):
    """Generate JWT token dengan expiry."""
    payload = {
        'user_id': user_id,
        'username': username,
        'exp': datetime.now(timezone.utc) + timedelta(hours=Config.JWT_EXPIRY_HOURS),
        'iat': datetime.now(timezone.utc)
    }
    return jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm='HS256')


def decode_token(token):
    """Decode dan validasi JWT token. Raise exception jika invalid/expired."""
    return jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
