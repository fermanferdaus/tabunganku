import os
import pymysql
import pymysql.cursors
from flask import g
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, '.env'))

def get_db_config():
    """
    Mengambil konfigurasi koneksi database MySQL dari environment variables.
    """
    config = {
        'host': os.environ['DB_HOST'],
        'user': os.environ['DB_USER'],
        'password': os.environ['DB_PASSWORD'],
        'database': os.environ['DB_NAME'],
        'port': int(os.environ['DB_PORT']),
        'cursorclass': pymysql.cursors.DictCursor
    }
    
    if os.environ.get('DB_SSL', 'false').lower() == 'true':
        config['ssl'] = {'ssl': {}}
        
    return config

def get_db_connection():
    """
    Membuka dan mengembalikan koneksi database aktif untuk context request berjalan.
    """
    if 'db' not in g:
        g.db = pymysql.connect(**get_db_config())
    return g.db

def close_db_connection(e=None):
    """
    Menutup koneksi database aktif setelah siklus request selesai.
    """
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """
    Memastikan inisialisasi skema tabel tabungan, uang keluar, dan rekap bulanan pada database.
    """
    try:
        conn = pymysql.connect(**get_db_config())
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tb_tabungan (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    uang_masuk INT NOT NULL,
                    tanggal DATE DEFAULT (CURRENT_DATE),
                    waktu TIME DEFAULT (CURRENT_TIME),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tb_uang_keluar (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    uang_keluar INT NOT NULL,
                    tanggal DATE DEFAULT (CURRENT_DATE),
                    waktu TIME DEFAULT (CURRENT_TIME),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tb_bulanan (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    bulan VARCHAR(50) NOT NULL,
                    jumlah_uang INT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()
        conn.close()
        print("[DB] Berhasil terhubung ke database.")
    except Exception as e:
        print(f"[DB Error] Gagal koneksi database: {e}")
