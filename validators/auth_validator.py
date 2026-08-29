def validate_login(username, password):
    """Validasi input login. Return list of errors."""
    errors = []
    if not username or not username.strip():
        errors.append('Username wajib diisi.')
    if not password:
        errors.append('Password wajib diisi.')
    return errors


def validate_change_password(old_password, new_password, confirm_password):
    """Validasi input ganti password. Return list of errors."""
    errors = []
    if not old_password:
        errors.append('Password lama wajib diisi.')
    if not new_password:
        errors.append('Password baru wajib diisi.')
    elif len(new_password) < 4:
        errors.append('Password baru minimal 4 karakter.')
    if not confirm_password:
        errors.append('Konfirmasi password wajib diisi.')
    elif new_password and new_password != confirm_password:
        errors.append('Konfirmasi password tidak cocok.')
    return errors
