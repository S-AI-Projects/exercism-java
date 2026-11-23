#!/usr/bin/env python3
"""Run the maintained crypto-square comparison checker from the repository root."""

from pathlib import Path
import runpy

root = Path(__file__).resolve().parents[2]
runpy.run_path(str(root / "tools/course_checks/r58-t036.py"), run_name="__main__")
