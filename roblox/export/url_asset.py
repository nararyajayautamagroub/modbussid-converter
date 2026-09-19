from pathlib import Path
from shared.roblox_url import download_asset
from shared.asset_inspector import inspect_file
def fetch(url:str,destination:Path):
 result=download_asset(url,destination); result["inspection"]=inspect_file(destination); return result
