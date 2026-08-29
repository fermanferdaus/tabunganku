from unittest.mock import patch


class TestMLEndpoints:
    """ML endpoints — tanpa auth (dipanggil ESP/Arduino)."""

    def test_prediksi_no_payload(self, client):
        """POST /prediksi tanpa JSON → 400."""
        resp = client.post('/prediksi', content_type='application/json')
        assert resp.status_code == 400

    def test_prediksi_missing_field(self, client):
        """POST /prediksi dengan field kurang → 400."""
        resp = client.post('/prediksi', json={'red': 100, 'green': 50})
        assert resp.status_code == 400
        data = resp.get_json()
        assert 'error' in data

    @patch('controllers.ml_controller.tabungan_service')
    @patch('controllers.ml_controller.prediksi_nominal_stacking')
    def test_prediksi_success(self, mock_prediksi, mock_service, client):
        """POST /prediksi dengan RGB valid → 200, return nominal."""
        mock_prediksi.return_value = 50000
        mock_service.simpan_uang_masuk.return_value = 150000

        resp = client.post('/prediksi', json={
            'red': 150, 'green': 80, 'blue': 60
        })
        data = resp.get_json()
        assert resp.status_code == 200
        assert data['nominal'] == 50000
        assert data['total_tabungan'] == 150000

    @patch('controllers.ml_controller.tabungan_service')
    def test_total_tabungan_ml(self, mock_service, client):
        """GET /total_tabungan tanpa auth → 200."""
        mock_service.hitung_total_tabungan.return_value = 250000

        resp = client.get('/total_tabungan')
        data = resp.get_json()
        assert resp.status_code == 200
        assert data['total_tabungan'] == 250000

    def test_prediksi_no_auth_needed(self, client):
        """Prediksi endpoint harus bisa diakses tanpa JWT."""
        resp = client.post('/prediksi', json={
            'red': 100, 'green': 100, 'blue': 100
        })
        # Bisa error karena model belum dimuat, tapi tidak 401
        assert resp.status_code != 401
