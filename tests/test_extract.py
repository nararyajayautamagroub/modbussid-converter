import zipfile
from pathlib import Path
from modbussid.extractor import extract

def test_zip_extract(tmp_path: Path):
    src=tmp_path/"test.bussidmod"
    with zipfile.ZipFile(src,"w") as z:
        z.writestr("vehicle/model.obj","o bus\nv 0 0 0\nv 1 0 0\nv 0 1 0\nf 1 2 3\n")
        z.writestr("vehicle/body.png",b"PNG")
    out=tmp_path/"out"; result=extract(src,out)
    assert (out/"vehicle/model.obj").exists()
    assert any(a.kind=="texture" for a in result.assets)
