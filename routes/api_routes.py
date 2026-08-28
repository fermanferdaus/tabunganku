from flask import Blueprint, request, jsonify
from datetime import datetime
import traceback
from services.db import get_db_connection

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/uang_masuk_harian', methods=['GET'])
def uang_masuk_harian():
    """
    Mengambil total akumulasi uang masuk pada tanggal hari ini.
    """
    try:
        with get_db_connection().cursor() as cursor:
            cursor.execute("""
                SELECT COALESCE(SUM(uang_masuk), 0) AS total_uang_masuk 
                FROM tb_tabungan 
                WHERE DATE(tanggal) = CURDATE()
            """)
            result = cursor.fetchone()
            total = int(result['total_uang_masuk']) if result else 0
        return jsonify({'total_uang_masuk': total})
    except Exception as e:
        print("[API Error] /api/uang_masuk_harian:")
        traceback.print_exc()
        return jsonify({'total_uang_masuk': 0, 'error': str(e)}), 500

@api_bp.route('/uang_masuk_bulanan', methods=['GET'])
def uang_masuk_bulanan():
    """
    Mengambil total akumulasi uang masuk pada bulan berjalan dan memperbarui tabel bulanan.
    """
    try:
        with get_db_connection().cursor() as cursor:
            cursor.execute("""
                SELECT COALESCE(SUM(uang_masuk), 0) AS total_uang_masuk_bulanan 
                FROM tb_tabungan 
                WHERE MONTH(tanggal) = MONTH(CURDATE()) 
                AND YEAR(tanggal) = YEAR(CURDATE())
            """)
            result = cursor.fetchone()
            total_bulanan = int(result['total_uang_masuk_bulanan']) if result else 0
            
            bulan_sekarang = datetime.now().strftime('%B %Y')
            
            cursor.execute("SELECT id FROM tb_bulanan WHERE bulan = %s", (bulan_sekarang,))
            existing = cursor.fetchone()
            if existing:
                cursor.execute("UPDATE tb_bulanan SET jumlah_uang = %s WHERE bulan = %s", (total_bulanan, bulan_sekarang))
            else:
                cursor.execute("INSERT INTO tb_bulanan (bulan, jumlah_uang) VALUES (%s, %s)", (bulan_sekarang, total_bulanan))
            get_db_connection().commit()

        return jsonify({
            'total_uang_masuk_bulanan': total_bulanan,
            'bulan_sekarang': bulan_sekarang
        })
    except Exception as e:
        print("[API Error] /api/uang_masuk_bulanan:")
        traceback.print_exc()
        return jsonify({'total_uang_masuk_bulanan': 0, 'bulan_sekarang': '', 'error': str(e)}), 500

@api_bp.route('/total_tabungan', methods=['GET'])
def total_tabungan():
    """
    Mengambil sisa total saldo tabungan dari akumulasi uang masuk dikurangi uang keluar.
    """
    try:
        with get_db_connection().cursor() as cursor:
            cursor.execute("SELECT COALESCE(SUM(uang_masuk), 0) AS total_masuk FROM tb_tabungan")
            masuk = int(cursor.fetchone()['total_masuk'])
            
            cursor.execute("SELECT COALESCE(SUM(uang_keluar), 0) AS total_keluar FROM tb_uang_keluar")
            keluar = int(cursor.fetchone()['total_keluar'])
            
            total_seluruh = masuk - keluar
        return jsonify({'total_uang_masuk_seluruh': total_seluruh})
    except Exception as e:
        print("[API Error] /api/total_tabungan:")
        traceback.print_exc()
        return jsonify({'total_uang_masuk_seluruh': 0, 'error': str(e)}), 500

@api_bp.route('/proses_pengurangan', methods=['POST'])
def proses_pengurangan():
    """
    Mencatat transaksi pengeluaran tabungan ke database.
    """
    try:
        jumlah = request.form.get('jumlah') or (request.get_json() or {}).get('jumlah')
        if not jumlah or int(jumlah) <= 0:
            return jsonify({'status': 'error', 'message': 'Jumlah tidak valid.'}), 400

        jumlah_int = int(jumlah)
        with get_db_connection().cursor() as cursor:
            cursor.execute("""
                INSERT INTO tb_uang_keluar (uang_keluar, tanggal, waktu) 
                VALUES (%s, CURDATE(), CURTIME())
            """, (jumlah_int,))
            get_db_connection().commit()

        return jsonify({'status': 'success'})
    except Exception as e:
        print("[API Error] /api/proses_pengurangan:")
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': f'Gagal mengurangi tabungan: {str(e)}'}), 500

@api_bp.route('/ambil_semua_tabungan', methods=['POST'])
def ambil_semua_tabungan():
    """
    Mereset dan mengosongkan seluruh riwayat data tabungan.
    """
    try:
        with get_db_connection().cursor() as cursor:
            cursor.execute("DELETE FROM tb_tabungan")
            cursor.execute("DELETE FROM tb_bulanan")
            cursor.execute("DELETE FROM tb_uang_keluar")
            get_db_connection().commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        print("[API Error] /api/ambil_semua_tabungan:")
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': f'Gagal mengambil seluruh tabungan: {str(e)}'}), 500

@api_bp.route('/ambil_uang_masuk', methods=['GET'])
def ambil_uang_masuk():
    """
    Mengambil daftar riwayat transaksi uang masuk.
    """
    try:
        with get_db_connection().cursor() as cursor:
            cursor.execute("SELECT id, tanggal, waktu, uang_masuk FROM tb_tabungan ORDER BY id DESC")
            rows = cursor.fetchall()
            
            data = []
            for row in rows:
                tgl = row['tanggal'].strftime('%d/%m/%Y') if hasattr(row['tanggal'], 'strftime') else str(row['tanggal'])
                wkt = str(row['waktu'])[:5] if row['waktu'] else ''
                data.append({
                    'id': row['id'],
                    'tanggal': tgl,
                    'waktu': wkt,
                    'uang_masuk': int(row['uang_masuk'])
                })
        return jsonify(data)
    except Exception as e:
        print("[API Error] /api/ambil_uang_masuk:")
        traceback.print_exc()
        return jsonify([]), 500

@api_bp.route('/ambil_uang_keluar', methods=['GET'])
def ambil_uang_keluar():
    """
    Mengambil daftar riwayat transaksi uang keluar.
    """
    try:
        with get_db_connection().cursor() as cursor:
            cursor.execute("SELECT id, tanggal, waktu, uang_keluar FROM tb_uang_keluar ORDER BY id DESC")
            rows = cursor.fetchall()
            
            data = []
            for row in rows:
                tgl = row['tanggal'].strftime('%d/%m/%Y') if hasattr(row['tanggal'], 'strftime') else str(row['tanggal'])
                wkt = str(row['waktu'])[:5] if row['waktu'] else ''
                data.append({
                    'id': row['id'],
                    'tanggal': tgl,
                    'waktu': wkt,
                    'uang_keluar': int(row['uang_keluar'])
                })
        return jsonify(data)
    except Exception as e:
        print("[API Error] /api/ambil_uang_keluar:")
        traceback.print_exc()
        return jsonify([]), 500

@api_bp.route('/chart_data', methods=['GET'])
def chart_data():
    """
    Mengambil agregasi data bulanan untuk visualisasi grafik.
    """
    try:
        with get_db_connection().cursor() as cursor:
            cursor.execute("SELECT bulan, jumlah_uang FROM tb_bulanan ORDER BY id ASC")
            rows = cursor.fetchall()
            labels = [r['bulan'] for r in rows]
            data = [int(r['jumlah_uang']) for r in rows]
        return jsonify({'labels': labels, 'data': data})
    except Exception as e:
        print("[API Error] /api/chart_data:")
        traceback.print_exc()
        return jsonify({'labels': [], 'data': []}), 500
