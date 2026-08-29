from flask import Blueprint, request
import traceback
from middleware.auth import login_required
from services import tabungan_service
from utils.response import api_response

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/uang_masuk_harian', methods=['GET'])
@login_required
def uang_masuk_harian():
    """Total akumulasi uang masuk hari ini."""
    try:
        total = tabungan_service.get_uang_masuk_harian()
        return api_response(True, 'OK', {'total_uang_masuk': total})
    except Exception as e:
        traceback.print_exc()
        return api_response(False, str(e), status=500)


@api_bp.route('/uang_masuk_bulanan', methods=['GET'])
@login_required
def uang_masuk_bulanan():
    """Total akumulasi uang masuk bulan berjalan."""
    try:
        result = tabungan_service.get_uang_masuk_bulanan()
        return api_response(True, 'OK', {
            'total_uang_masuk_bulanan': result['total'],
            'bulan_sekarang': result['bulan']
        })
    except Exception as e:
        traceback.print_exc()
        return api_response(False, str(e), status=500)


@api_bp.route('/total_tabungan', methods=['GET'])
@login_required
def total_tabungan():
    """Sisa total saldo tabungan."""
    try:
        total = tabungan_service.get_total_tabungan()
        return api_response(True, 'OK', {'total_uang_masuk_seluruh': total})
    except Exception as e:
        traceback.print_exc()
        return api_response(False, str(e), status=500)


@api_bp.route('/proses_pengurangan', methods=['POST'])
@login_required
def proses_pengurangan():
    """Catat transaksi pengeluaran tabungan."""
    try:
        jumlah = request.form.get('jumlah') or (request.get_json() or {}).get('jumlah')
        if not jumlah or int(jumlah) <= 0:
            return api_response(False, 'Jumlah tidak valid.', status=400)

        tabungan_service.proses_pengurangan(int(jumlah))
        return api_response(True, 'Berhasil mengurangi tabungan.')
    except Exception as e:
        traceback.print_exc()
        return api_response(False, f'Gagal: {e}', status=500)


@api_bp.route('/ambil_semua_tabungan', methods=['POST'])
@login_required
def ambil_semua_tabungan():
    """Reset seluruh riwayat data tabungan."""
    try:
        tabungan_service.ambil_semua_tabungan()
        return api_response(True, 'Seluruh tabungan berhasil diambil.')
    except Exception as e:
        traceback.print_exc()
        return api_response(False, f'Gagal: {e}', status=500)


@api_bp.route('/ambil_uang_masuk', methods=['GET'])
@login_required
def ambil_uang_masuk():
    """Daftar riwayat transaksi uang masuk."""
    try:
        data = tabungan_service.get_riwayat_masuk()
        return api_response(True, 'OK', data)
    except Exception as e:
        traceback.print_exc()
        return api_response(False, str(e), status=500)


@api_bp.route('/ambil_uang_keluar', methods=['GET'])
@login_required
def ambil_uang_keluar():
    """Daftar riwayat transaksi uang keluar."""
    try:
        data = tabungan_service.get_riwayat_keluar()
        return api_response(True, 'OK', data)
    except Exception as e:
        traceback.print_exc()
        return api_response(False, str(e), status=500)


@api_bp.route('/chart_data', methods=['GET'])
@login_required
def chart_data():
    """Agregasi data bulanan untuk chart."""
    try:
        data = tabungan_service.get_chart_data()
        return api_response(True, 'OK', data)
    except Exception as e:
        traceback.print_exc()
        return api_response(False, str(e), status=500)
