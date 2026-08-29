from flask import Blueprint, request, jsonify
from services.ml_service import prediksi_nominal_stacking
from services import tabungan_service

ml_bp = Blueprint('ml', __name__)


@ml_bp.route('/prediksi', methods=['POST'])
def prediksi():
    """
    Menerima input RGB dari sensor, prediksi nominal uang, simpan ke database.
    Endpoint ini tanpa auth — dipanggil langsung oleh ESP/Arduino.
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Payload JSON tidak ditemukan'}), 400

    for field in ['red', 'green', 'blue']:
        if field not in data:
            return jsonify({'error': f'Field required missing: {field}'}), 400

    try:
        nominal = prediksi_nominal_stacking(data['red'], data['green'], data['blue'])
    except Exception as e:
        return jsonify({'error': f'Gagal prediksi ML: {e}'}), 500

    try:
        total = tabungan_service.simpan_uang_masuk(nominal)
    except Exception as e:
        return jsonify({'error': f'Gagal simpan ke database: {e}'}), 500

    return jsonify({'nominal': nominal, 'total_tabungan': total}), 200


@ml_bp.route('/total_tabungan', methods=['GET'])
def total_tabungan_ml():
    """Total sisa tabungan aktif (tanpa auth untuk ESP)."""
    try:
        total = tabungan_service.hitung_total_tabungan()
        return jsonify({'total_tabungan': total}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
