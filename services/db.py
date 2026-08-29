import pymysql
import pymysql.cursors
import bcrypt
from flask import g
from config.settings import Config


def get_db_config():
    """Konfigurasi koneksi database MySQL dari Config."""
    config = {
        'host': Config.DB_HOST,
        'user': Config.DB_USER,
        'password': Config.DB_PASSWORD,
        'database': Config.DB_NAME,
        'port': Config.DB_PORT,
        'cursorclass': pymysql.cursors.DictCursor
    }

    if Config.DB_SSL:
        config['ssl'] = {'ssl': {}}

    return config


def get_db_connection():
    """Koneksi database aktif untuk context request berjalan."""
    if 'db' not in g:
        g.db = pymysql.connect(**get_db_config())
    return g.db


def close_db_connection(e=None):
    """Menutup koneksi database setelah request selesai."""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    """Inisialisasi skema tabel dan migrasi password ke bcrypt."""
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
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tb_login (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) NOT NULL,
                    password VARCHAR(255) NOT NULL
                );
            """)

            # Migrasi: perbesar kolom password jika masih VARCHAR(50)
            cursor.execute("""
                ALTER TABLE tb_login MODIFY COLUMN password VARCHAR(255) NOT NULL
            """)

            # Auto-hash password plaintext atau hash terpotong (< 60 chars) ke bcrypt
            cursor.execute("SELECT id, password FROM tb_login")
            rows = cursor.fetchall()
            for row in rows:
                pw = row['password']
                is_valid = (
                    isinstance(pw, str)
                    and len(pw) == 60
                    and (pw.startswith('$2b$') or pw.startswith('$2a$') or pw.startswith('$2y$'))
                )
                if not is_valid:
                    pw_bytes = str(pw).encode('utf-8')[:72]
                    hashed = bcrypt.hashpw(
                        pw_bytes, bcrypt.gensalt()
                    ).decode('utf-8')
                    cursor.execute(
                        "UPDATE tb_login SET password = %s WHERE id = %s",
                        (hashed, row['id'])
                    )

            # Jika tb_login kosong, seed user admin default dengan password admin123
            if not rows:
                default_hash = bcrypt.hashpw(b'admin123', bcrypt.gensalt()).decode('utf-8')
                cursor.execute(
                    "INSERT INTO tb_login (username, password) VALUES (%s, %s)",
                    ('admin', default_hash)
                )

            conn.commit()
        conn.close()
        print("[DB] Terhubung ke database. Skema dan password siap.")
    except Exception as e:
        print(f"[DB Error] Gagal koneksi database: {e}")
