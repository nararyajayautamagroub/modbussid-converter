# modbussid-converter

Toolkit for inspecting and extracting BUSSID mod containers and converting recovered 3D assets to OBJ, DAE, FBX and Blender (.blend), with texture collection.

> Use only with files and assets you are authorized to inspect. This project does not bypass encryption, DRM, signatures, or access controls.

## Status

The project starts with a format-agnostic extraction layer. BUSSID container formats can differ by version, so the parser keeps the raw container intact and detects common embedded assets instead of pretending every file is a ZIP.

## CLI

```bash
python -m modbussid inspect input.bussidmod
python -m modbussid extract input.bussidmod -o output
python -m modbussid export input.bussidmod --format all -o exports
```

Supported export targets:
- OBJ + MTL
- DAE
- FBX
- BLEND
- textures copied to an export texture directory

For FBX/DAE/BLEND, Blender is used as the conversion backend when installed.

## Development

Python 3.11+ is recommended.

```bash
pip install -e .
pytest
```
