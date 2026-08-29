from datetime import datetime
from services.db import get_db_connection
from utils.formatters import (
    BULAN_INDONESIA,
    format_tanggal_indonesia,
    format_waktu_wib
)


def get_uang_masuk_harian():
    """Total akumulasi uang masuk hari ini."""
    with get_db_connection().cursor() as cursor:
        cursor.execute("""
            SELECT COALESCE(SUM(uang_masuk), 0) AS total
            FROM tb_tabungan
            WHERE DATE(tanggal) = CURDATE()
        """)
        result = cursor.fetchone()
        return int(result['total']) if result else 0


def get_uang_masuk_bulanan():
    """Total akumulasi uang masuk bulan berjalan + update tabel bulanan."""
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT COALESCE(SUM(uang_masuk), 0) AS total
            FROM tb_tabungan
            WHERE MONTH(tanggal) = MONTH(CURDATE())
            AND YEAR(tanggal) = YEAR(CURDATE())
        """)
        result = cursor.fetchone()
        total = int(result['total']) if result else 0

        now = datetime.now()
        bulan = f"{BULAN_INDONESIA.get(now.month, '')} {now.year}"
        cursor.execute("SELECT id FROM tb_bulanan WHERE bulan = %s", (bulan,))
        existing = cursor.fetchone()

        if existing:
            cursor.execute(
                "UPDATE tb_bulanan SET jumlah_uang = %s WHERE bulan = %s",
                (total, bulan)
            )
        else:
            cursor.execute(
                "INSERT INTO tb_bulanan (bulan, jumlah_uang) VALUES (%s, %s)",
                (bulan, total)
            )
        conn.commit()

    return {'total': total, 'bulan': bulan}


def get_total_tabungan():
    """Sisa saldo: total masuk - total keluar."""
    return hitung_total_tabungan()


def hitung_total_tabungan():
    """Menghitung sisa saldo tabungan bersih."""
    with get_db_connection().cursor() as cursor:
        cursor.execute(
            "SELECT COALESCE(SUM(uang_masuk), 0) AS total_masuk FROM tb_tabungan"
        )
        masuk = int(cursor.fetchone()['total_masuk'])

        cursor.execute(
            "SELECT COALESCE(SUM(uang_keluar), 0) AS total_keluar FROM tb_uang_keluar"
        )
        keluar = int(cursor.fetchone()['total_keluar'])

        return masuk - keluar


def proses_pengurangan(jumlah):
    """Catat transaksi pengeluaran."""
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            "INSERT INTO tb_uang_keluar (uang_keluar, tanggal, waktu) "
            "VALUES (%s, CURDATE(), CURTIME())",
            (jumlah,)
        )
        conn.commit()


def ambil_semua_tabungan():
    """Reset seluruh data tabungan."""
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM tb_tabungan")
        cursor.execute("DELETE FROM tb_bulanan")
        cursor.execute("DELETE FROM tb_uang_keluar")
        conn.commit()


def get_riwayat_masuk():
    """Daftar riwayat uang masuk."""
    with get_db_connection().cursor() as cursor:
        cursor.execute(
            "SELECT id, tanggal, waktu, uang_masuk "
            "FROM tb_tabungan ORDER BY id DESC"
        )
        rows = cursor.fetchall()
        return [_format_row_masuk(r) for r in rows]


def get_riwayat_keluar():
    """Daftar riwayat uang keluar."""
    with get_db_connection().cursor() as cursor:
        cursor.execute(
            "SELECT id, tanggal, waktu, uang_keluar "
            "FROM tb_uang_keluar ORDER BY id DESC"
        )
        rows = cursor.fetchall()
        return [_format_row_keluar(r) for r in rows]


def get_chart_data():
    """Agregasi data bulanan untuk chart."""
    with get_db_connection().cursor() as cursor:
        cursor.execute(
            "SELECT bulan, jumlah_uang FROM tb_bulanan ORDER BY id ASC"
        )
        rows = cursor.fetchall()
        return {
            'labels': [r['bulan'] for r in rows],
            'data': [int(r['jumlah_uang']) for r in rows]
        }


def simpan_uang_masuk(nominal):
    """Simpan transaksi uang masuk dan return total tabungan."""
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            "INSERT INTO tb_tabungan (uang_masuk, tanggal, waktu) "
            "VALUES (%s, CURDATE(), CURTIME())",
            (nominal,)
        )
        conn.commit()
    return hitung_total_tabungan()


def _format_row_masuk(row):
    tgl = format_tanggal_indonesia(row.get('tanggal'))
    wkt = format_waktu_wib(row.get('waktu'))
    return {
        'id': row['id'],
        'tanggal': tgl,
        'waktu': wkt,
        'uang_masuk': int(row['uang_masuk'])
    }


def _format_row_keluar(row):
    tgl = format_tanggal_indonesia(row.get('tanggal'))
    wkt = format_waktu_wib(row.get('waktu'))
    return {
        'id': row['id'],
        'tanggal': tgl,
        'waktu': wkt,
        'uang_keluar': int(row['uang_keluar'])
    }
