# Game Mod Asset Lab

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
- Download asset Roblox publik melalui endpoint resmi Asset Delivery
- Validasi URL Roblox sebelum download
- GitHub Actions untuk compile dan test Python 3.10-3.13

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
- GET /api/lights/{strobo|rotator|ledbar}
- GET /api/lights/{strobo|rotator|ledbar}/download?platform=...

## Akurasi data repository

Website membaca struktur repository lokal saat runtime. Endpoint /api/repository juga mencoba membaca tree branch main dari GitHub dan mengembalikan commit SHA, jumlah file, daftar path, serta status sinkronisasi.

Jika GitHub tidak bisa diakses, data lokal tetap dipakai sehingga website tidak mati hanya karena internet sedang bermain petak umpet.

## Batas penting

Project ini **tidak** membypass password, enkripsi, DRM, signature, private asset, atau access control.

Untuk format game proprietary seperti beberapa format internal ETS2/BUSSID/Roblox, project hanya melaporkan metadata, mendeteksi container yang dikenali, atau memproses format yang didukung. Parser native penuh harus ditambahkan berdasarkan format, dokumentasi, atau sample yang sah.

Exporter Roblox lampu saat ini menghasilkan **paket data animasi JSON**, bukan file native .rbxm/.rbxmx.

## Jalankan

    python -m pip install -r requirements.txt
    uvicorn web.app:app --reload

Buka http://127.0.0.1:8000.

## Validasi

    python -m compileall -q bussid ets2 roblox shared web tests
    python -m pytest -q -W error
