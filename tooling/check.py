#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys

COMMANDS = [
    [sys.executable, "-m", "pip", "check"],
    [sys.executable, "-m", "compileall", "-q", "platforms", "core", "backend", "tooling", "tests"],
    [sys.executable, "-m", "ruff", "check", ".", "--select", "E9,F"],
    [sys.executable, "-m", "pytest", "-q", "-W", "error"],
    [sys.executable, "tooling/smoke.py"],
]


def main() -> int:
    for command in COMMANDS:
        print("$", " ".join(command), flush=True)
        result = subprocess.run(command, check=False)
        if result.returncode:
            return result.returncode
    print("ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
