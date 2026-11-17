#!/usr/bin/env python3
"""Entry point for the focused run-length-encoding runner verification."""
import subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[2]
result=subprocess.run([sys.executable,"tools/course_checks/r58-t019.py"],cwd=root)
raise SystemExit(result.returncode)
