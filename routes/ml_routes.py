from flask import Blueprint, request, jsonify
from services.db import get_db_connection
from services.ml_service import prediksi_nominal_stacking

ml_bp = Blueprint('ml', __name__)

def hitung_total_tabungan():
    """
    Menghitung sisa saldo tabungan bersih dari akumulasi uang masuk dikurangi uang keluar.
    """
    with get_db_connection().cursor() as cursor:
        cursor.execute("SELECT COALESCE(SUM(uang_masuk), 0) AS total_masuk FROM tb_tabungan")
        masuk = int(cursor.fetchone()['total_masuk'])
        
        cursor.execute("SELECT COALESCE(SUM(uang_keluar), 0) AS total_keluar FROM tb_uang_keluar")
        keluar = int(cursor.fetchone()['total_keluar'])
        
        return masuk - keluar

@ml_bp.route('/prediksi', methods=['POST'])
def prediksi():
    """
    Menerima input nilai warna Red Green Blue dari sensor perangkat,
    menjalankan prediksi pecahan nominal uang, dan mencatat transaksi ke database.
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Payload JSON tidak ditemukan'}), 400

    for field in ['red', 'green', 'blue']:
        if field not in data:
            return jsonify({'error': f'Field required missing: {field}'}), 400

    red, green, blue = data['red'], data['green'], data['blue']

    try:
        nominal = prediksi_nominal_stacking(red, green, blue)
    except Exception as e:
        return jsonify({'error': f'Gagal melakukan prediksi ML: {str(e)}'}), 500

    try:
        with get_db_connection().cursor() as cursor:
            cursor.execute(
                "INSERT INTO tb_tabungan (uang_masuk, tanggal, waktu) VALUES (%s, CURDATE(), CURTIME())",
                (nominal,)
            )
            get_db_connection().commit()
            total = hitung_total_tabungan()
    except Exception as e:
        return jsonify({'error': f'Gagal menyimpan ke database: {str(e)}'}), 500

    return jsonify({'nominal': nominal, 'total_tabungan': total}), 200

@ml_bp.route('/total_tabungan', methods=['GET'])
def total_tabungan_ml():
    """
    Mengambil data total sisa tabungan aktif.
    """
    try:
        total = hitung_total_tabungan()
        return jsonify({'total_tabungan': total}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
