# Tabunganku — IoT Financial Backend & Dashboard

Web dashboard dan REST API backend berbasis Flask untuk sistem celengan IoT. Menggunakan model Machine Learning Stacking Classifier untuk klasifikasi nominal uang dari sensor warna RGB, database MySQL, dan autentikasi berbasis JWT (HttpOnly cookie) + Bcrypt.

---

## Arsitektur Sistem

Aplikasi menggunakan pola pemisahan modular (Controller-Service-Validator-Utils):

```text
app_render/
├── config/
│   └── settings.py          # Abstraksi environment variable (Config class)
├── controllers/
│   ├── api_controller.py    # Endpoint data transaksi dan agregasi dashboard
│   ├── auth_controller.py   # Auth handler (login, logout, ganti password)
│   ├── ml_controller.py     # Endpoint hardware IoT (prediksi & saldo LCD)
│   └── web_controller.py    # Route template view HTML
├── middleware/
│   └── auth.py              # Decorator @login_required (validasi JWT cookie)
├── models/                  # Pickled ML artifacts
│   ├── stacking_model.pkl
│   ├── label_encoder.pkl
│   └── scaler.pkl
├── services/
│   ├── auth_service.py      # Hash bcrypt, validasi, dan encoding JWT
│   ├── db.py                # Database pool connection & auto-migration skema
│   ├── ml_service.py        # Feature extraction & inference stacking model
│   └── tabungan_service.py  # Query bisnis transaksi dan riwayat tabungan
├── static/
│   ├── img/
│   │   ├── logo.png
│   │   └── profile.svg
│   └── js/
│       └── dashboard.js     # Realtime polling, Chart.js, dan pagination
├── templates/
│   ├── base.html            # Layout utama, floating header, modal profil
│   ├── index.html           # Dashboard KPI, grafik, tabel, form penarikan
│   └── login.html           # View autentikasi login
├── tests/
│   ├── conftest.py          # Pytest fixture & mock context
│   ├── test_api.py          # Unit test API transaksi
│   ├── test_auth.py         # Unit test autentikasi & JWT lifecycle
│   ├── test_ml.py           # Unit test inference ML
│   ├── test_utils.py        # Unit test formatters & response helper
│   └── test_validators.py   # Unit test input validator
├── utils/
│   ├── formatters.py        # Date/time/currency formatter (WIB, Indo date, Rupiah)
│   └── response.py          # Standardized JSON response helper
├── validators/
│   └── auth_validator.py    # Validasi payload login & password
├── .env.example
├── .flake8
├── main.py                  # Entry point aplikasi
├── Procfile                 # Production web process
└── requirements.txt
```

---

## Spesifikasi Teknis

- **Runtime:** Python 3.10+
- **Framework:** Flask 3.1
- **Database:** MySQL 8.0+ (PyMySQL driver, SSL supported)
- **Autentikasi:** JWT (`PyJWT` 2.10+, HMAC-SHA256, secret $\ge 32$ byte) via `HttpOnly` Cookie, password hashing via `bcrypt` (cost 12).
- **Frontend:** TailwindCSS (CDN), Chart.js 4.x, SweetAlert2.
- **ML Estimator:** Scikit-Learn StackingClassifier (Base: Decision Tree, Random Forest, AdaBoost; Meta: Gradient Boosting).

---

## Instalasi & Menjalankan Lokal

### 1. Setup Environment

```bash
# Masuk direktori kerja
cd app_render

# Buat dan aktifkan virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1    # Windows PowerShell
# source venv/bin/activate     # Linux / macOS

# Install dependensi
pip install -r requirements.txt
```

### 2. Konfigurasi Environment Variable

Salin `.env.example` ke `.env`:

```bash
cp .env.example .env          # Linux / macOS
copy .env.example .env        # Windows
```

Konfigurasi parameter database dan secret key:

```env
FLASK_ENV=development
DEBUG=True
PORT=5000
SECRET_KEY=tabunganku-super-secret-key-min-32-chars-long!
JWT_SECRET_KEY=tabunganku-jwt-secret-production-32-bytes-long!
JWT_EXPIRY_HOURS=24

DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=db_tabungan
DB_SSL=false
```

### 3. Inisialisasi Database & Jalankan Server

Database dan tabel akan diinisialisasi otomatis saat server pertama kali berjalan (`init_db()` pada `main.py`).

```bash
python main.py
```

Akses `http://localhost:5000` melalui browser.

**Kredensial Default:**
- Username: `admin`
- Password: `admin123`

---

## Kontrak API

### 1. Hardware IoT (Unauthenticated)

Endpoint ini dipanggil langsung oleh ESP32 / Arduino tanpa token JWT:

#### `POST /prediksi`
Inference nominal uang berdasarkan nilai sensor TCS3200.

- **Request Body:**
  ```json
  {
    "red": 150,
    "green": 210,
    "blue": 95
  }
  ```
- **Response `200 OK`:**
  ```json
  {
    "status": "success",
    "prediksi": 50000,
    "total_tabungan": 250000
  }
  ```

#### `GET /total_tabungan`
Mengambil sisa total saldo tabungan untuk kebutuhan display hardware.

- **Response `200 OK`:**
  ```json
  {
    "status": "success",
    "total_tabungan": 250000
  }
  ```

---

### 2. Autentikasi

#### `POST /login`
- **Request Form:** `username`, `password`
- **Behavior:** Set cookie `access_token` (`HttpOnly`, `SameSite=Lax`, max-age 86400s) dan redirect ke `/dashboard`.

#### `GET /logout`
- **Behavior:** Menghapus cookie `access_token` dan redirect ke `/login`.

#### `POST /api/change-password` (Protected)
- **Headers:** `Content-Type: application/json`
- **Request Body:**
  ```json
  {
    "old_password": "admin",
    "new_password": "newpassword123",
    "confirm_password": "newpassword123"
  }
  ```
- **Response `200 OK`:**
  ```json
  {
    "success": true,
    "message": "Password berhasil diubah.",
    "data": null,
    "errors": null
  }
  ```

---

### 3. Dashboard API (Protected via JWT)

| Method | Endpoint | Deskripsi |
|---|---|---|
| `GET` | `/api/uang_masuk_harian` | Total nominal uang masuk pada tanggal berjalan |
| `GET` | `/api/uang_masuk_bulanan` | Total nominal uang masuk pada bulan berjalan |
| `GET` | `/api/total_tabungan` | Akumulasi total saldo aktif |
| `GET` | `/api/ambil_uang_masuk` | List riwayat transaksi masuk (tanggal, waktu WIB, nominal) |
| `GET` | `/api/ambil_uang_keluar` | List riwayat penarikan saldo (tanggal, waktu WIB, nominal) |
| `GET` | `/api/chart_data` | Data deret waktu per bulan untuk visualisasi grafik |
| `POST` | `/api/proses_pengurangan` | Input penarikan saldo parsial (`{"quantity": 50000}`) |
| `POST` | `/api/ambil_semua_tabungan` | Penarikan seluruh sisa saldo tabungan |

Format standard JSON response:
```json
{
  "success": true,
  "message": "Deskripsi status",
  "data": {},
  "errors": null
}
```

---

## Pengujian & Kualitas Kode

Menjalankan seluruh test suite otomatis dan linting PEP8:

```bash
# Menjalankan Pytest
pytest tests/ -v

# Menjalankan Flake8 linter
flake8 --config .flake8 config/ controllers/ middleware/ services/ utils/ validators/ tests/ main.py
```

Cakupan pengujian (58 test cases):
- Unit test autentikasi: flow login, token signing/decoding, session guard, auto-upgrade password hash, proteksi salt corruption.
- Unit test API: seluruh endpoint Protected & IoT hardware.
- Unit test validators: edge case validasi payload login dan pergantian password.
- Unit test formatters: parsing date object, string ISO, waktu WIB, dan Rupiah.

---

## Deployment Produksi (Docker & GitHub Actions CI/CD)

### 1. Daftar GitHub Secrets (Settings > Secrets and variables > Actions)

Untuk mengaktifkan otomatisasi deployment ke VPS, daftarkan secrets berikut di repositori GitHub:

| Secret Name | Wajib | Deskripsi / Nilai |
|---|---|---|
| `VPS_HOST` | Ya | IP address atau domain server VPS |
| `VPS_USERNAME` | Ya | User login SSH VPS (`root` / `ubuntu`) |
| `VPS_SSH_KEY` | Ya | Private SSH Key (format OpenSSH/RSA/Ed25519) |
| `VPS_PORT` | Opsional | Port SSH server (default: `22`) |
| `VPS_PROJECT_PATH` | Opsional | Lokasi absolut direktori proyek di VPS (contoh: `/home/prod/apps/tabunganku`) |
| `PRODUCTION_ENV` | Ya | Seluruh isi variabel environment produksi (di-paste langsung) |

Contoh isi secret `PRODUCTION_ENV`:
```env
APP_ENV=production
FLASK_DEBUG=false
PORT=5000
SECRET_KEY=ganti-dengan-secret-key-acak-minimal-32-karakter!!
GUNICORN_WORKERS=2
GUNICORN_THREADS=4

DB_HOST=mysql
DB_PORT=3306
DB_ROOT_PASSWORD=root_secure_password_123
DB_USER=tabungan_user
DB_PASSWORD=tabungan_secure_password_123
DB_NAME=db_tabungan
DB_SSL=false

JWT_SECRET_KEY=ganti-dengan-jwt-secret-acak-minimal-32-karakter!!
JWT_EXPIRY_HOURS=24
```

### 2. Manual Run via Docker Compose

```bash
# Build dan jalankan seluruh container
docker compose up -d --build

# Periksa status container
docker compose ps

# Matikan seluruh container
docker compose down
```
