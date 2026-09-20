#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys


COMMANDS = [
    [sys.executable, "-m", "pip", "check"],
    [sys.executable, "-m", "compileall", "-q", "bussid", "ets2", "roblox", "scripts", "shared", "web", "tests"],
    [sys.executable, "-m", "ruff", "check", ".", "--select", "E9,F"],
    [sys.executable, "-m", "pytest", "-q", "-W", "error"],
]


def main() -> int:
    for command in COMMANDS:
        print("$", " ".join(command), flush=True)
        result = subprocess.run(command, check=False)
        if result.returncode != 0:
            return result.returncode
    print("ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
