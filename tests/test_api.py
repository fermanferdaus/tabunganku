from unittest.mock import patch, MagicMock


class TestAPIWithoutAuth:
    """API endpoints tanpa login harus return 401."""

    def test_uang_masuk_harian_no_auth(self, client):
        resp = client.get('/api/uang_masuk_harian')
        assert resp.status_code == 401

    def test_uang_masuk_bulanan_no_auth(self, client):
        resp = client.get('/api/uang_masuk_bulanan')
        assert resp.status_code == 401

    def test_total_tabungan_no_auth(self, client):
        resp = client.get('/api/total_tabungan')
        assert resp.status_code == 401

    def test_proses_pengurangan_no_auth(self, client):
        resp = client.post('/api/proses_pengurangan', json={'jumlah': 1000})
        assert resp.status_code == 401

    def test_ambil_semua_no_auth(self, client):
        resp = client.post('/api/ambil_semua_tabungan')
        assert resp.status_code == 401

    def test_ambil_uang_masuk_no_auth(self, client):
        resp = client.get('/api/ambil_uang_masuk')
        assert resp.status_code == 401

    def test_ambil_uang_keluar_no_auth(self, client):
        resp = client.get('/api/ambil_uang_keluar')
        assert resp.status_code == 401

    def test_chart_data_no_auth(self, client):
        resp = client.get('/api/chart_data')
        assert resp.status_code == 401


class TestAPIWithAuth:
    """API endpoints dengan JWT valid."""

    @patch('services.tabungan_service.get_db_connection')
    def test_uang_masuk_harian(self, mock_db, authed_client):
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {'total': 50000}
        mock_cursor.__enter__ = lambda s: s
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_db.return_value.cursor.return_value = mock_cursor

        resp = authed_client.get('/api/uang_masuk_harian')
        data = resp.get_json()
        assert resp.status_code == 200
        assert data['success'] is True
        assert 'total_uang_masuk' in data['data']

    @patch('services.tabungan_service.get_db_connection')
    def test_ambil_uang_masuk(self, mock_db, authed_client):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_cursor.__enter__ = lambda s: s
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_db.return_value.cursor.return_value = mock_cursor

        resp = authed_client.get('/api/ambil_uang_masuk')
        data = resp.get_json()
        assert resp.status_code == 200
        assert data['success'] is True
        assert isinstance(data['data'], list)

    @patch('services.tabungan_service.get_db_connection')
    def test_ambil_uang_keluar(self, mock_db, authed_client):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_cursor.__enter__ = lambda s: s
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_db.return_value.cursor.return_value = mock_cursor

        resp = authed_client.get('/api/ambil_uang_keluar')
        data = resp.get_json()
        assert resp.status_code == 200
        assert data['success'] is True
        assert isinstance(data['data'], list)

    @patch('services.tabungan_service.get_db_connection')
    def test_chart_data(self, mock_db, authed_client):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_cursor.__enter__ = lambda s: s
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_db.return_value.cursor.return_value = mock_cursor

        resp = authed_client.get('/api/chart_data')
        data = resp.get_json()
        assert resp.status_code == 200
        assert data['success'] is True
        assert 'labels' in data['data']
        assert 'data' in data['data']

    def test_proses_pengurangan_invalid(self, authed_client):
        """Jumlah 0 atau negatif → 400."""
        resp = authed_client.post('/api/proses_pengurangan', json={'jumlah': 0})
        data = resp.get_json()
        assert resp.status_code == 400
        assert data['success'] is False

    @patch('services.tabungan_service.get_db_connection')
    def test_proses_pengurangan_valid(self, mock_db, authed_client):
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = lambda s: s
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_db.return_value.cursor.return_value = mock_cursor

        resp = authed_client.post('/api/proses_pengurangan', json={'jumlah': 10000})
        data = resp.get_json()
        assert resp.status_code == 200
        assert data['success'] is True

    @patch('services.tabungan_service.get_db_connection')
    def test_ambil_semua_tabungan(self, mock_db, authed_client):
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = lambda s: s
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_db.return_value.cursor.return_value = mock_cursor

        resp = authed_client.post('/api/ambil_semua_tabungan')
        data = resp.get_json()
        assert resp.status_code == 200
        assert data['success'] is True

    @patch('services.tabungan_service.get_db_connection')
    def test_ambil_uang_masuk_format_tanggal_waktu(self, mock_db, authed_client):
        """Format tanggal harus '12 November 2020' dan waktu berakhiran 'WIB'."""
        from datetime import date, time
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [{
            'id': 1,
            'tanggal': date(2020, 11, 12),
            'waktu': time(14, 30, 0),
            'uang_masuk': 50000
        }]
        mock_cursor.__enter__ = lambda s: s
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_db.return_value.cursor.return_value = mock_cursor

        resp = authed_client.get('/api/ambil_uang_masuk')
        data = resp.get_json()
        assert resp.status_code == 200
        assert data['success'] is True
        row = data['data'][0]
        assert row['tanggal'] == '12 November 2020'
        assert row['waktu'] == '14:30 WIB'

