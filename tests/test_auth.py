from unittest.mock import patch, MagicMock
from services.auth_service import hash_password


class TestLoginFlow:
    """Test login, logout, dan akses guard."""

    def test_root_redirects_to_login(self, client):
        """GET / tanpa token harus redirect ke /login."""
        resp = client.get('/', follow_redirects=False)
        assert resp.status_code == 302
        assert '/login' in resp.headers['Location']

    def test_login_page_renders(self, client):
        """GET /login harus render halaman login."""
        resp = client.get('/login')
        assert resp.status_code == 200
        assert b'Login' in resp.data or b'login' in resp.data

    def test_dashboard_without_auth_redirects(self, client):
        """GET /dashboard tanpa login harus redirect ke /login."""
        resp = client.get('/dashboard', follow_redirects=False)
        assert resp.status_code == 302
        assert '/login' in resp.headers['Location']

    @patch('controllers.auth_controller.get_db_connection')
    def test_login_success(self, mock_db, client):
        """POST /login dengan credentials valid (admin / admin123) → set cookie, redirect dashboard."""
        hashed = hash_password('admin123')
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {
            'id': 1, 'username': 'admin', 'password': hashed
        }
        mock_cursor.__enter__ = lambda s: s
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_db.return_value.cursor.return_value = mock_cursor

        resp = client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=False)

        assert resp.status_code == 302
        assert '/dashboard' in resp.headers['Location']
        assert 'access_token' in resp.headers.get('Set-Cookie', '')

    @patch('controllers.auth_controller.get_db_connection')
    def test_login_wrong_password(self, mock_db, client):
        """POST /login dengan password salah → render login dengan error."""
        hashed = hash_password('admin123')
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {
            'id': 1, 'username': 'admin', 'password': hashed
        }
        mock_cursor.__enter__ = lambda s: s
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_db.return_value.cursor.return_value = mock_cursor

        resp = client.post('/login', data={
            'username': 'admin',
            'password': 'wrongpass'
        })

        assert resp.status_code == 200
        assert b'salah' in resp.data

    def test_login_empty_fields(self, client):
        """POST /login dengan field kosong → render login dengan error."""
        resp = client.post('/login', data={
            'username': '',
            'password': ''
        })
        assert resp.status_code == 200
        assert b'wajib' in resp.data.lower() or b'Wajib' in resp.data

    def test_logout_clears_cookie(self, authed_client):
        """GET /logout harus clear cookie dan redirect ke /login."""
        resp = authed_client.get('/logout', follow_redirects=False)
        assert resp.status_code == 302
        assert '/login' in resp.headers['Location']

    @patch('controllers.auth_controller.get_db_connection')
    def test_login_with_plaintext_password_in_db(self, mock_db, client):
        """POST /login dengan password plaintext di DB harus berhasil dan auto-upgrade."""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {
            'id': 1, 'username': 'admin', 'password': 'admin123'
        }
        mock_cursor.__enter__ = lambda s: s
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_db.return_value.cursor.return_value = mock_cursor

        resp = client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=False)

        assert resp.status_code == 302
        assert '/dashboard' in resp.headers['Location']
        assert 'access_token' in resp.headers.get('Set-Cookie', '')

    @patch('controllers.auth_controller.get_db_connection')
    def test_login_with_corrupted_hash(self, mock_db, client):
        """POST /login dengan hash tidak valid/rusak di DB tidak boleh crash dengan invalid salt."""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {
            'id': 1, 'username': 'admin', 'password': '$2b$12$invalid_truncated_hash'
        }
        mock_cursor.__enter__ = lambda s: s
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_db.return_value.cursor.return_value = mock_cursor

        resp = client.post('/login', data={
            'username': 'admin',
            'password': 'wrongpassword'
        })

        assert resp.status_code == 200
        assert b'salah' in resp.data

    def test_dashboard_with_valid_token(self, authed_client):
        """GET /dashboard dengan token valid → 200."""
        resp = authed_client.get('/dashboard')
        assert resp.status_code == 200


class TestChangePassword:
    """Test fitur ganti password."""

    @patch('controllers.auth_controller.get_db_connection')
    def test_change_password_wrong_old(self, mock_db, authed_client):
        """Change password dengan password lama salah → 400."""
        hashed = hash_password('admin123')
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {'password': hashed}
        mock_cursor.__enter__ = lambda s: s
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_db.return_value.cursor.return_value = mock_cursor

        resp = authed_client.post(
            '/api/change-password',
            json={
                'old_password': 'wrongold',
                'new_password': 'newpass123',
                'confirm_password': 'newpass123'
            })
        data = resp.get_json()
        assert resp.status_code == 400
        assert data['success'] is False

    def test_change_password_mismatch_confirm(self, authed_client):
        """Change password dengan confirm tidak cocok → 400."""
        resp = authed_client.post(
            '/api/change-password',
            json={
                'old_password': 'admin123',
                'new_password': 'newpass123',
                'confirm_password': 'different'
            })
        data = resp.get_json()
        assert resp.status_code == 400
        assert data['success'] is False

    def test_change_password_short_new(self, authed_client):
        """Change password baru terlalu pendek → 400."""
        resp = authed_client.post(
            '/api/change-password',
            json={
                'old_password': 'admin123',
                'new_password': 'ab',
                'confirm_password': 'ab'
            })
        data = resp.get_json()
        assert resp.status_code == 400
        assert data['success'] is False

    @patch('controllers.auth_controller.get_db_connection')
    def test_change_password_success(self, mock_db, authed_client):
        """Change password valid → 200, success."""
        hashed = hash_password('admin123')
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {'password': hashed}
        mock_cursor.__enter__ = lambda s: s
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_db.return_value = mock_conn

        resp = authed_client.post(
            '/api/change-password',
            json={
                'old_password': 'admin123',
                'new_password': 'newpass123',
                'confirm_password': 'newpass123'
            })
        data = resp.get_json()
        assert resp.status_code == 200
        assert data['success'] is True

    def test_change_password_without_auth(self, client):
        """Change password tanpa login → 401."""
        resp = client.post(
            '/api/change-password',
            json={
                'old_password': 'admin123',
                'new_password': 'newpass123',
                'confirm_password': 'newpass123'
            })
        assert resp.status_code == 401
