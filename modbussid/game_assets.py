from pathlib import Path

ETS2_EXTENSIONS = {
    ".scs": "scs_archive",
    ".sii": "unit_definition",
    ".sui": "unit_include",
    ".mat": "material",
    ".pmd": "model_descriptor",
    ".pmg": "model_geometry",
    ".pma": "model_animation",
    ".pmc": "collision_model",
    ".ppd": "prefab",
    ".pim": "model_source",
    ".pip": "model_locator",
    ".dds": "texture",
}

BUSSID_EXTENSIONS = {
    ".bussidmod": "bussid_vehicle_or_mod",
    ".bussidvehicle": "bussid_vehicle",
    ".png": "texture",
    ".jpg": "texture",
    ".jpeg": "texture",
    ".webp": "texture",
    ".json": "metadata",
    ".xml": "metadata",
}

VEHICLE_HINTS = ("truck", "vehicle", "bus", "trailer", "chassis", "cabin", "engine", "wheel", "tire", "interior")
MAP_HINTS = ("map", "sector", "prefab", "road", "city", "terrain", "model", "world", "navigation")

def identify_asset(path: Path, game: str = "auto") -> dict:
    name = path.name.lower()
    ext = path.suffix.lower()
    if game == "auto":
        if ext in ETS2_EXTENSIONS or ext == ".scs":
            game = "ets2"
        elif ext in BUSSID_EXTENSIONS:
            game = "bussid"
        else:
            game = "unknown"

    catalog = ETS2_EXTENSIONS if game == "ets2" else BUSSID_EXTENSIONS
    kind = catalog.get(ext, "unknown")
    joined = str(path).lower()
    category = "map" if any(x in joined for x in MAP_HINTS) else "vehicle" if any(x in joined for x in VEHICLE_HINTS) else "other"

    return {
        "game": game,
        "kind": kind,
        "category": category,
        "extension": ext,
        "path": str(path),
        "recognized": kind != "unknown",
    }
