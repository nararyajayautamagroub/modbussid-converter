# modbussid-converter

Toolkit web untuk inspeksi/extract dan konversi asset mod BUSSID yang dapat diproses oleh pipeline ini.

> Gunakan hanya file dan asset yang kamu berhak inspeksi. Project ini tidak membypass encryption, DRM, signature, atau access control.

## Web interface

Jalankan lokal:

```powershell
python -m pip install -e .
.\\run_web.ps1
```

Buka `http://127.0.0.1:8000`.

Website menyediakan upload file, pilihan format, proses server-side, dan ZIP hasil.

### Deployment

Backend memakai FastAPI, jadi bisa dideploy ke server/container Python yang mendukung ASGI. Untuk FBX/DAE/BLEND, server harus memiliki Blender terpasang dan tersedia di PATH. Jangan mengunggah file berhak cipta atau data pribadi tanpa izin.

## CLI

```bash
python -m modbussid inspect input.bussidmod
python -m modbussid extract input.bussidmod -o output
python -m modbussid export input.bussidmod --format all -o exports
```

## Status

Extraction saat ini bersifat format-agnostic. Jika file menggunakan mesh/container internal BUSSID yang belum dikenali, aplikasi melaporkan bahwa decoder khusus diperlukan daripada mengarang hasil 3D.
