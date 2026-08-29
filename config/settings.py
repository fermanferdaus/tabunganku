import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_file = os.environ.get('ENV_FILE', '.env')
env_path = os.path.join(BASE_DIR, env_file)
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    load_dotenv(os.path.join(BASE_DIR, '.env'))


class Config:
    """Konfigurasi aplikasi dari environment variables."""

    APP_ENV = os.environ.get('APP_ENV', os.environ.get('FLASK_ENV', 'development'))
    PORT = int(os.environ.get('PORT', 5000))
    SECRET_KEY = os.environ.get(
        'SECRET_KEY',
        'tabunganku-flask-secret-key-min-32chars-default!'
    )

    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = int(os.environ.get('DB_PORT', 3306))
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_NAME = os.environ.get('DB_NAME', 'db_tabungan')
    DB_SSL = os.environ.get('DB_SSL', 'false').lower() == 'true'

    JWT_SECRET_KEY = os.environ.get(
        'JWT_SECRET_KEY',
        'tabunganku-jwt-secret-key-super-secure-32bytes-min!'
    )
    JWT_EXPIRY_HOURS = int(os.environ.get('JWT_EXPIRY_HOURS', 24))

    DEBUG = os.environ.get(
        'FLASK_DEBUG',
        'false' if APP_ENV == 'production' else 'true'
    ).lower() == 'true'
