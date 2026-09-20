# Game Mod Asset Lab v3.0.0

Web-based inspector, classifier, exporter, and download utility untuk **file/mod yang memang Anda miliki atau berwenang memprosesnya**.

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
- GitHub Actions untuk dependency check, static check, compile, dan test Python 3.10-3.13

## Endpoint utama

- GET /api/health
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
    /api/scraper/crawl?url=https%3A%2F%2Fexample.com&max_pages=5

