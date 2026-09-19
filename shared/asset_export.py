from __future__ import annotations

import json
import tarfile
import zipfile
from pathlib import Path

from .asset_inspector import report


def _selected_names(selected: list[str] | None) -> set[str] | None:
    if selected is None:
        return None
    cleaned = {item.strip() for item in selected if item and item.strip()}
    if not cleaned:
        raise ValueError("Daftar asset yang dipilih kosong.")
    return cleaned


def export_found_asset(
    source: Path,
    destination: Path,
    selected: list[str] | None = None,
) -> Path:
    source = source.resolve()
    destination = destination.resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    if source == destination:
        raise ValueError("File sumber dan tujuan tidak boleh sama.")

    names = _selected_names(selected)
    destination.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(
        destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as out:
        if names is None:
            out.write(source, source.name)
        elif source.suffix.lower() == ".zip":
            with zipfile.ZipFile(source) as archive:
                available = {info.filename for info in archive.infolist()}
                missing = names - available
                if missing:
                    raise ValueError(
                        "Entry ZIP tidak ditemukan: " + ", ".join(sorted(missing))
                    )
                for info in archive.infolist():
                    if info.filename in names and not info.is_dir():
                        out.writestr(info, archive.read(info.filename))
        elif source.suffix.lower() in {".tar", ".gz", ".tgz", ".bz2", ".xz"}:
            with tarfile.open(source) as archive:
                members = {member.name: member for member in archive.getmembers()}
                missing = names - set(members)
                if missing:
                    raise ValueError(
                        "Entry TAR tidak ditemukan: " + ", ".join(sorted(missing))
                    )
                for name in sorted(names):
                    member = members[name]
                    if not member.isfile():
                        continue
                    extracted = archive.extractfile(member)
                    if extracted is None:
                        raise ValueError(f"Entry TAR tidak dapat dibaca: {name}")
                    out.writestr(name, extracted.read())
        else:
            raise ValueError("Pemilihan entry hanya didukung untuk ZIP/TAR.")

        manifest = {
            "format": "game-mod-export-v2",
            "source": source.name,
            "report": report(source),
            "selected": sorted(names) if names is not None else None,
        }
        out.writestr(
            "manifest.json",
            json.dumps(manifest, indent=2, ensure_ascii=False).encode("utf-8"),
        )

    return destination
