import argparse
from pathlib import Path
from .extractor import extract, inspect, write_report
from .exporters import export_all

def main():
    p=argparse.ArgumentParser(prog="modbussid")
    sub=p.add_subparsers(dest="command", required=True)
    i=sub.add_parser("inspect"); i.add_argument("input", type=Path)
    x=sub.add_parser("extract"); x.add_argument("input", type=Path); x.add_argument("-o","--output",type=Path,default=Path("extracted"))
    e=sub.add_parser("export")
    e.add_argument("input",type=Path); e.add_argument("--format",choices=["all","obj","dae","fbx","blend"],default="all")
    e.add_argument("-o","--output",type=Path,default=Path("exports")); e.add_argument("--blender",default="blender")
    a=p.parse_args()
    if a.command=="inspect":
        r=inspect(a.input)
        print(f"file={r.source}\nsize={r.size}\nsha256={r.sha256}\nmagic={r.magic}")
    elif a.command=="extract":
        r=extract(a.input,a.output); write_report(r,a.output/"report.json"); print(f"Extracted to {a.output}")
    elif a.command=="export":
        work=a.output/".extracted"; r=extract(a.input,work); write_report(r,a.output/"report.json")
        export_all(work,a.output/("all" if a.format=="all" else a.format),a.blender)
        print(f"Exported to {a.output}")
