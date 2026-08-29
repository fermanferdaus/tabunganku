from datetime import date, time, datetime
from utils.formatters import (
    format_tanggal_indonesia,
    format_waktu_wib,
    format_rupiah,
    BULAN_INDONESIA
)
from utils.response import api_response


class TestFormatters:
    def test_format_tanggal_date_object(self):
        d = date(2020, 11, 12)
        assert format_tanggal_indonesia(d) == '12 November 2020'

    def test_format_tanggal_datetime_object(self):
        dt = datetime(2024, 8, 17, 10, 0, 0)
        assert format_tanggal_indonesia(dt) == '17 Agustus 2024'

    def test_format_tanggal_iso_string(self):
        assert format_tanggal_indonesia('2026-08-29') == '29 Agustus 2026'

    def test_format_tanggal_slash_string(self):
        assert format_tanggal_indonesia('12/11/2020') == '12 November 2020'

    def test_format_tanggal_empty_or_invalid(self):
        assert format_tanggal_indonesia(None) == ''
        assert format_tanggal_indonesia('invalid-date') == 'invalid-date'

    def test_format_waktu_time_object(self):
        t = time(14, 30, 0)
        assert format_waktu_wib(t) == '14:30 WIB'

    def test_format_waktu_string(self):
        assert format_waktu_wib('23:09:31') == '23:09 WIB'
        assert format_waktu_wib('08:05') == '08:05 WIB'

    def test_format_waktu_empty(self):
        assert format_waktu_wib(None) == ''

    def test_format_rupiah(self):
        assert format_rupiah(50000) == 'Rp 50.000'
        assert format_rupiah(1500000) == 'Rp 1.500.000'
        assert format_rupiah(0) == 'Rp 0'
        assert format_rupiah(None) == 'Rp 0'

    def test_bulan_indonesia_dictionary(self):
        assert len(BULAN_INDONESIA) == 12
        assert BULAN_INDONESIA[1] == 'Januari'
        assert BULAN_INDONESIA[12] == 'Desember'


class TestApiResponse:
    def test_api_response_structure(self, app):
        with app.app_context():
            resp, status = api_response(True, 'Sukses', {'count': 5}, None, 200)
            json_data = resp.get_json()
            assert status == 200
            assert json_data['success'] is True
            assert json_data['message'] == 'Sukses'
            assert json_data['data'] == {'count': 5}
            assert json_data['errors'] is None
