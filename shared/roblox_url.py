from __future__ import annotations
from urllib.parse import urlparse,parse_qs
from urllib.request import Request,urlopen
import re
def asset_id_from_url(url:str)->int:
 p=urlparse(url)
 if p.scheme not in {"https","http"} or not p.hostname or not p.hostname.lower().endswith("roblox.com"): raise ValueError("Hanya URL resmi roblox.com yang diizinkan.")
 values=parse_qs(p.query).get("id",[]) or re.findall(r"/(?:library|catalog|asset)/([0-9]+)",p.path)
 if not values: raise ValueError("Asset ID Roblox tidak ditemukan.")
 return int(values[0])
def download_asset(url:str,target:Path):
 aid=asset_id_from_url(url); req=Request(f"https://assetdelivery.roblox.com/v1/asset/?id={aid}",headers={"User-Agent":"Game-Mod-Asset-Lab/1.0"})
 with urlopen(req,timeout=20) as r: data=r.read(50*1024*1024+1)
 if len(data)>50*1024*1024: raise ValueError("Asset melebihi batas 50 MB.")
 target.write_bytes(data); return {"asset_id":aid,"bytes":len(data)}
