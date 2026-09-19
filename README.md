# modbussid-converter

Toolkit for inspecting and extracting BUSSID mod containers and converting recovered 3D assets to OBJ, DAE, FBX and Blender (.blend), with texture collection.

> Use only with files and assets you are authorized to inspect. This project does not bypass encryption, DRM, signatures, or access controls.

## Windows EXE

The project can be built as a standalone Windows executable:

```text
dist\\modbussid-converter.exe
```

No Python installation is required on the target Windows PC for the packaged CLI itself.

### Build locally

Install Python 3.11+, then run PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\\build_exe.ps1
```

The executable is created at `dist\\modbussid-converter.exe`.

### Build automatically with GitHub Actions

Open **Actions → Build Windows EXE → Run workflow**. For a tagged release such as `v0.2.0`, the workflow also runs automatically.

After the workflow finishes, download the `modbussid-converter-windows` artifact from the workflow run.

## CLI

```bash
python -m modbussid inspect input.bussidmod
python -m modbussid extract input.bussidmod -o output
python -m modbussid export input.bussidmod --format all -o exports
```

When using the packaged EXE, replace `python -m modbussid` with:

```text
modbussid-converter.exe inspect input.bussidmod
modbussid-converter.exe extract input.bussidmod -o output
modbussid-converter.exe export input.bussidmod --format all -o exports
```

Supported export targets:
- OBJ + MTL
- DAE
- FBX
- BLEND
- textures copied to an export texture directory

For FBX/DAE/BLEND, Blender is used as the conversion backend when installed.

## Status

The project starts with a format-agnostic extraction layer. BUSSID container formats can differ by version, so the parser keeps the raw container intact and detects common embedded assets instead of pretending every file is a ZIP.

The standalone EXE packages the Python application. **Blender is not bundled into the EXE**, because it is a separate conversion backend and would make the executable unnecessarily enormous. Install Blender separately and pass its executable path with `--blender` when needed.

## Development

Python 3.11+ is recommended.

```bash
pip install -e .
pytest
```
