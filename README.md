# Game Mod Asset Lab

Web-based inspector and exporter untuk asset mod yang memang berhak Anda akses.

## Konsep utama
**Bongkar/inspect -> temukan asset -> pilih asset -> export -> download.**

Jadi ketika inspector menemukan file di dalam archive, file tersebut menjadi kandidat output export. Tidak ada langkah palsu berupa "export" yang cuma mengganti ekstensi.

## Kategori
BUSSID: vehicle, map, kodename, sprite-sheet, lights.
ETS2: vehicle, map.
Roblox: vehicle, lights, export.

## Fitur saat ini
- Deteksi ZIP/TAR.
- Metadata ukuran, ekstensi, tipe, SHA-256.
- Daftar entry archive yang dapat dibaca.
- Export file/entry ke ZIP.
- Manifest JSON pada setiap export.
- Animasi data strobo, rotator, LED bar.
- Download asset Roblox melalui URL resmi.
- Web API dan halaman web sederhana.

## Keamanan
Proteksi password, enkripsi, DRM, signature, dan access control tidak dibypass. Roblox URL dibatasi ke domain resmi Roblox dan download dibatasi 50 MB.

## Jalankan
```bash
pip install -r requirements.txt
uvicorn web.app:app --reload
```
Buka http://127.0.0.1:8000.

## Struktur
```
bussid/      # adapter BUSSID
ets2/        # adapter ETS2
roblox/      # adapter Roblox
shared/      # inspector, exporter, animation, URL
web/         # FastAPI + UI
download/    # dokumentasi output
tests/       # pengujian
```
