from pathlib import Path
from modbussid.format_detect import detect_magic

def test_unknown(tmp_path: Path):
    p=tmp_path/"x.modbussid"; p.write_bytes(b"BUSSID"+b"\\x00"*20)
    assert detect_magic(p)=="unknown"
