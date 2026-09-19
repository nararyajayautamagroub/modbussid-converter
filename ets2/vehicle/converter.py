from pathlib import Path
from shared.asset_inspector import report
from shared.asset_export import export_found_asset
def inspect(path:Path): return report(path)
def export(path:Path,destination:Path): return export_found_asset(path,destination)
