# Game Mod Asset Lab v4.2.0

Web-based inspector, classifier, exporter, scraper, account system, dan download utility untuk **file/mod yang memang Anda miliki atau berwenang memprosesnya**.

## Alur utama

**Upload / pilih asset → Inspect → temukan entry → klasifikasi template → Export → Download**

## Platform dan kategori

- BUSSID: Vehicle, Map, Kodename, Sprite Sheet, Lights
- ETS2/ATS: Vehicle, Map
- Roblox: Vehicle, Lights, Export

## Template

- **AO**: Ambient Occlusion
- **Texture**: texture umum
- **Kaca/XOR**: template kaca / glass

Classifier memakai nama file berbasis token agar radio.png tidak salah dibaca sebagai AO hanya karena mengandung huruf ao.

## Fitur yang sudah aktif

- Deteksi file dan SHA-256
- Deteksi container ZIP/TAR
- Daftar isi archive
- Export seluruh file atau entry terpilih ke ZIP
- Manifest JSON pada hasil export
- Upload file ke workspace repository dengan batas 100 MB
- Inspeksi hanya pada path yang berada di dalam repository
- Repository catalog lokal
- Sinkronisasi catalog ke GitHub repository publik secara berkala
- Endpoint health dan capabilities
- Animasi data untuk Strobo, Rotator, LED Bar
- Paket Roblox lampu berisi JSON + script Lua untuk Roblox Studio
- Inspect ukuran/format image dan ekstraksi Sprite Sheet menjadi frame ZIP
- Near-real-time repository tree dengan default branch, commit SHA, tanggal commit, dan filter prefix
- Download asset Roblox publik melalui endpoint resmi Asset Delivery
- Validasi URL Roblox sebelum download
- Web scraper publik dengan parser HTML, metadata Open Graph, JSON-LD, heading, link, image, robots.txt, batas ukuran, timeout, anti-SSRF, dan same-host crawl
- GitHub Actions untuk dependency check, static check, compile, unit test, runtime smoke test, dan Python 3.10-3.14

## Endpoint utama

- GET /api/health
- GET /api/auth/status
- GET /api/auth/me
- POST /api/auth/register
- POST /api/auth/login
- POST /api/auth/logout
- POST /api/auth/logout-all
- PUT /api/auth/settings
- PUT /api/auth/profile
- PUT /api/auth/password
- GET /api/auth/google/start
- GET /api/auth/google/callback
- GET /api/i18n
- GET /api/i18n/{language}
- GET /manifest.webmanifest
- GET /sw.js
- GET /icon.svg
- GET /api/capabilities
- GET /api/categories
- GET /api/repository
- POST /api/assets/upload
- GET /api/assets/inspect?path=...
- GET /api/assets/export?path=...
- GET /api/templates/types
- GET /api/templates/classify?path=...
- GET /api/assets/roblox/validate?url=...
- GET /api/assets/roblox/url?url=...
- GET /api/sprite-sheet/inspect?path=...
- GET /api/sprite-sheet/extract?path=...&columns=4&rows=4
- GET /api/repository/tree?prefix=...
- GET /api/scraper/fetch?url=...
- GET /api/scraper/crawl?url=...&max_pages=...
- GET /api/lights/{strobo|rotator|ledbar}
- GET /api/lights/{strobo|rotator|ledbar}/download?platform=...

## Akurasi data repository

Website membaca struktur repository lokal saat runtime. Endpoint /api/repository juga mencoba membaca tree branch main dari GitHub dan mengembalikan commit SHA, jumlah file, daftar path, serta status sinkronisasi.

Jika GitHub tidak bisa diakses, data lokal tetap dipakai sehingga website tidak mati hanya karena internet sedang bermain petak umpet.

## Batas penting

Project ini **tidak** membypass password, enkripsi, DRM, signature, private asset, atau access control.

Untuk format game proprietary seperti beberapa format internal ETS2/BUSSID/Roblox, project hanya melaporkan metadata, mendeteksi container yang dikenali, atau memproses format yang didukung. Parser native penuh harus ditambahkan berdasarkan format, dokumentasi, atau sample yang sah.

Exporter Roblox lampu menghasilkan **JSON + script Lua Roblox Studio**. Output tersebut bukan file native .rbxm/.rbxmx.

## Jalankan

    python -m pip install -r requirements.txt
    uvicorn web.app:app --reload

Buka http://127.0.0.1:8000.

## Validasi

    python -m compileall -q bussid ets2 roblox shared web tests
    python -m pytest -q -W error

## Scraper

Scraper berjalan pada host publik HTTP/HTTPS, memvalidasi DNS/IP publik, memeriksa robots.txt bila tersedia, membatasi response sampai 20 MB per request, timeout 60 detik maksimum, dan crawl hanya pada host yang sama. Ini ditujukan untuk data publik, bukan untuk melewati login, paywall, private resource, atau access control.

### Contoh

    /api/scraper/fetch?url=https%3A%2F%2Fexample.com
    /api/scraper/crawl?url=https%3A%2F%2Fexample.com&max_pages=5&max_bytes=5242880


## CLI scraper v4.2

    python scripts/scraper.py https://example.com
    python scripts/scraper.py https://example.com --crawl --max-pages 5
    python scripts/scraper.py https://example.com --output reports/example.json

## Validasi lokal v4.2

    python scripts/check.py
    python scripts/smoke.py

Perintah check menjalankan pip check, compileall, Ruff (E9/F), dan pytest dengan warning diperlakukan sebagai error. smoke.py menjalankan endpoint FastAPI utama secara in-process.

## Authentication & Account

Fitur v4.2:
- Register dengan email/password dan migrasi SQLite otomatis untuk schema lama
- Login/logout dengan rate limit percobaan password
- Logout semua session
- Ganti password
- Session database SQLite
- Google Login via OpenID Connect
- Pengaturan profil, bahasa, tema, dan notifikasi
- 10 bahasa: Indonesia, English, Melayu, Arabic, Japanese, Korean, Chinese, Spanish, Portuguese, French

Google Login tidak mengaktifkan credential secara otomatis. Simpan credential di environment, jangan di source code:

    GOOGLE_CLIENT_ID=...
    GOOGLE_CLIENT_SECRET=...
    GOOGLE_REDIRECT_URI=https://domain-anda.example/api/auth/google/callback

Di Google Cloud Console, gunakan OAuth Client tipe **Web application** dan daftarkan redirect URI yang sama persis dengan `GOOGLE_REDIRECT_URI`.

Untuk deployment HTTPS:

    COOKIE_SECURE=1
    SESSION_SECRET=<random-secret-panjang>

Tanpa Google credential, tombol Google Login tampil tetapi disabled. Register/login lokal tetap bekerja.

## Branding & Footer

Website menggunakan footer resmi:

`PT. NARARYA JAYA UTAMA GROUB - All Right Reserved`

Repository ini saat ini berisi aplikasi web Game Mod Asset Lab dan tooling scraper; tidak ada source bot Discord/Telegram pada repo ini, jadi tidak saya pura-purakan ada. 

## Frontend, npm & Gateway

Frontend sekarang dipisah menjadi `web/index.html`, `web/styles.css`, dan `web/app.js`. Tidak ada inline CSS/JavaScript pada halaman utama. `package.json` tidak memakai dependency frontend berat agar `npm install` / `npm ci` tetap sederhana.

    npm install
    npm run check
    npm start

Gateway FastAPI tersedia di:

    /api/gateway/health
    /api/gateway/routes

CI menjalankan `npm ci` + `npm run check` dan kemudian test Python.

## PWA & All Device Support

Website menggunakan layout responsive untuk mobile, tablet, desktop, viewport safe-area, hamburger menu, dan installable PWA. Service worker tidak menyimpan response `/api/*` agar data akun, scraper, dan asset tidak masuk cache publik.
