#!/usr/bin/env python3
"""Assert the binary-search Java micro-example and run reference tests."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from common import java_environment, record_versions, run_reference_tests  # noqa: E402

TASK = "R58-T037"
EVIDENCE = ROOT / "work" / TASK
EXPECTED = "true\n10\n"


def main() -> int:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    record_versions(EVIDENCE)
    test_result = run_reference_tests("binary-search", EVIDENCE)
    source = ROOT / "work/R58-T037/BinarySearchBoxingDemo.java"
    with tempfile.TemporaryDirectory(prefix="binary-search-hint-") as temporary:
        directory = Path(temporary)
        compiled = subprocess.run(
            ["javac", "-d", str(directory), str(source)],
            capture_output=True,
            text=True,
            timeout=60,
            env=java_environment(),
        )
        if compiled.returncode != 0:
            raise RuntimeError(f"Micro-example did not compile: {compiled.stderr}")
        result = subprocess.run(
            ["java", "-cp", str(directory), "BinarySearchBoxingDemo"],
            capture_output=True,
            text=True,
            timeout=30,
            env=java_environment(),
        )
        if result.returncode != 0 or result.stdout != EXPECTED:
            raise RuntimeError(f"Unexpected micro-example output: {result.stdout!r}; {result.stderr}")
    (EVIDENCE / "micro-example-output.txt").write_text(result.stdout, encoding="utf-8")
    print(
        f"{TASK}: micro-example output matches; reference suite: {test_result['tests']} cases "
        f"discovered, {test_result['failures']} failures, {test_result['skipped']} skipped"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
