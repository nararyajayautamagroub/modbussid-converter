import json,zipfile
from pathlib import Path
from .light_animation import build_animation,to_dict
def export_light_package(light_type:str,target:Path,platform:str)->Path:
    target.parent.mkdir(parents=True,exist_ok=True); payload={'platform':platform,'asset_type':'light_animation','animation':to_dict(build_animation(light_type))}
    json_path=target.with_suffix('.json'); json_path.write_text(json.dumps(payload,indent=2),encoding='utf-8')
    zip_path=target.with_suffix('.zip')
    with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:z.write(json_path,json_path.name)
    return zip_path
