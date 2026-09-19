# BUSSID Vehicle

Adapter untuk mod kendaraan BUSSID.

## Alur
Input -> inspect container -> daftar asset -> pilih -> export ZIP -> download.

## Yang dikenali
Ekstensi BUSSID, gambar, model umum, serta archive ZIP/TAR dapat diklasifikasikan. Struktur internal yang proprietary tidak dianggap sudah ter-parse penuh tanpa spesifikasi.

## Modul
- `converter.py`: facade inspect/export.
- `shared.asset_inspector`: pemeriksaan file.
- `shared.asset_export`: packaging hasil.

## Catatan
File terenkripsi/password/DRM tidak dibongkar paksa.
