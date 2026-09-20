#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "5.0.0"
EXPECTED_TOP_LEVEL = {"backend", "frontend", "core", "platforms", "assets", "artifacts", "tooling", "tests", "docs"}
FORBIDDEN_TOP_LEVEL = {"web", "shared", "scripts", "bussid", "ets2", "roblox", "download"}

def fail(message: str) -> None:
    raise SystemExit(f"REPOSITORY AUDIT FAILED: {message}")

def main() -> int:
    for folder in EXPECTED_TOP_LEVEL:
        if not (ROOT / folder).is_dir():
            fail(f"missing top-level folder: {folder}")
    for folder in FORBIDDEN_TOP_LEVEL:
        if (ROOT / folder).exists():
            fail(f"legacy top-level folder still exists: {folder}")

    required = [
        ROOT / "backend/app.py", ROOT / "backend/gateway_api.py",
        ROOT / "frontend/index.html", ROOT / "frontend/app.js", ROOT / "frontend/styles.css",
        ROOT / "frontend/sw.js", ROOT / "core/version.py", ROOT / "tooling/frontend-smoke.mjs",
        ROOT / "tooling/smoke.py",
    ]
    for path in required:
        if not path.is_file():
            fail(f"required file missing: {path.relative_to(ROOT)}")

    html = (ROOT / "frontend/index.html").read_text(encoding="utf-8")
    if re.search(r"onclick\s*=", html, re.I) or re.search(r"\sstyle\s*=", html, re.I):
        fail("inline handler or style attribute found")
    if re.search(r"<style\b", html, re.I) or re.search(r"<script\s*>", html, re.I):
        fail("inline style/script block found")
    if "PT. NARARYA JAYA UTAMA GROUB - All Right Reserved" not in html:
        fail("official footer is missing")

    app = (ROOT / "backend/app.py").read_text(encoding="utf-8")
    if app.count("app.mount(") != 1 or "StaticFiles(directory=FRONTEND" not in app:
        fail("frontend gateway configuration is invalid")

    code_roots = [ROOT / "backend", ROOT / "core", ROOT / "platforms", ROOT / "tooling", ROOT / "tests"]
    for code_root in code_roots:
        for path in code_root.rglob("*.py"):
            content = path.read_text(encoding="utf-8")
            if re.search(r"^\s*(?:from|import)\s+(?:shared|web)\.", content, re.M):
                fail(f"legacy import remains in {path.relative_to(ROOT)}")

    version = (ROOT / "core/version.py").read_text(encoding="utf-8")
    if VERSION not in version:
        fail("core version is not 5.0.0")

    package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
    lock = json.loads((ROOT / "package-lock.json").read_text(encoding="utf-8"))
    if package["version"] != VERSION or lock["version"] != VERSION or lock["packages"][""]["version"] != VERSION:
        fail("npm package versions are out of sync")
    if "frontend/app.js" not in package["scripts"]["syntax"] or "backend.app:app" not in package["scripts"]["start"]:
        fail("npm scripts are not wired to the v5 layout")

    if not (ROOT / "docs/FOLDER_DESCRIPTIONS.md").is_file():
        fail("folder description documentation is missing")
    print("REPOSITORY AUDIT PASSED")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
