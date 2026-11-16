#!/usr/bin/env python3
"""Run the VLQ reference tests and prove a seven-to-six-bit mutation is rejected."""
from __future__ import annotations

import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXERCISE = ROOT / "exercises/practice/variable-length-quantity"
CONFIG = EXERCISE / ".meta/config.json"
REFERENCE = EXERCISE / ".meta/src/reference/java/VariableLengthQuantity.java"
TEST_CLASS = "VariableLengthQuantityTest"
TARGET_TEST = "testSmallestDoubleByte"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def copy_exercise(destination: Path) -> Path:
    target = destination / "exercise"
    shutil.copytree(EXERCISE, target, ignore=shutil.ignore_patterns("build", ".gradle"))
    config = json.loads((target / ".meta/config.json").read_text())
    example_files = config["files"]["example"]
    source_dir = target / "src/main/java"
    source_dir.mkdir(parents=True, exist_ok=True)
    for relative in example_files:
        source = target / relative
        require(source.is_file(), f"Missing configured reference source: {relative}")
        shutil.copy2(source, source_dir / source.name)
    for test_file in config["files"]["test"]:
        path = target / test_file
        require(path.is_file(), f"Missing configured test source: {test_file}")
        text = path.read_text()
        text = re.sub(r'^\s*@Disabled\("Remove to run test"\)\s*\n', "", text, flags=re.M)
        path.write_text(text)
    return target


def run_gradle(exercise: Path, *extra: str) -> tuple[int, dict]:
    command = ["./gradlew", "test", "--no-daemon", *extra]
    process = subprocess.run(command, cwd=exercise, text=True, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
    xml_files = list((exercise / "build/test-results/test").glob("TEST-*.xml"))
    totals = {"tests": 0, "failures": 0, "errors": 0, "skipped": 0, "executed": 0,
              "failed_test_names": [], "reports": [str(p.relative_to(exercise)) for p in xml_files]}
    for report in xml_files:
        root = ET.parse(report).getroot()
        for key in ("tests", "failures", "errors", "skipped"):
            totals[key] += int(root.attrib.get(key, 0))
        for case in root.iter("testcase"):
            if case.find("failure") is not None or case.find("error") is not None:
                totals["failed_test_names"].append(case.attrib.get("name", ""))
    totals["executed"] = totals["tests"] - totals["skipped"]
    return process.returncode, {**totals, "output_tail": process.stdout[-5000:]}


def main() -> int:
    require(CONFIG.is_file() and REFERENCE.is_file(), "Exercise metadata or reference is missing")
    before = hashlib_files([EXERCISE / p for p in json.loads(CONFIG.read_text())["files"]["solution"]])
    results = {"task": "R58-T013", "timestamp_unix": int(time.time()),
               "python": sys.version, "platform": platform.platform(),
               "java": command_version(["java", "-version"]),
               "gradle_command": "./gradlew test --no-daemon"}
    with tempfile.TemporaryDirectory(prefix="r58-t013-") as temporary:
        temp = Path(temporary)
        original = copy_exercise(temp / "original")
        original_code, original_stats = run_gradle(original)
        require(original_code == 0, "Unmodified reference test run failed")
        require(original_stats["executed"] > 0, "Unmodified reference executed zero tests")
        require(original_stats["failures"] == 0 and original_stats["errors"] == 0,
                "Unmodified reference has assertion failures or errors")
        require(original_stats["skipped"] == 0, "Unmodified reference unexpectedly skipped tests")

        mutant = copy_exercise(temp / "mutant")
        mutant_source = mutant / "src/main/java/VariableLengthQuantity.java"
        source_text = mutant_source.read_text()
        require(source_text.count("number >>= 7;") == 1,
                "Expected exactly one seven-bit shift in encodeSingleNumber")
        mutant_source.write_text(source_text.replace("number >>= 7;", "number >>= 6;", 1))
        mutant_code, mutant_stats = run_gradle(mutant, "--tests",
                                               f"{TEST_CLASS}.{TARGET_TEST}")
        require(mutant_code != 0, "The six-bit mutant unexpectedly passed the target test")
        require(TARGET_TEST in mutant_stats["failed_test_names"],
                f"The mutant failed, but not at {TARGET_TEST}: {mutant_stats['failed_test_names']}")
        results["original"] = {"return_code": original_code, **original_stats}
        results["mutant"] = {"return_code": mutant_code, **mutant_stats}

    after = hashlib_files([EXERCISE / p for p in json.loads(CONFIG.read_text())["files"]["solution"]])
    require(before == after, "Learner starter files changed during the check")
    results["learner_solution_hashes_unchanged"] = True
    output = ROOT / "work/R58-T013/latest-result.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps(results, indent=2))
    print("PASS: original reference passes; the six-bit mutant is rejected by testSmallestDoubleByte.")
    return 0


def hashlib_files(paths: list[Path]) -> dict[str, str]:
    import hashlib
    return {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in paths}


def command_version(command: list[str]) -> str:
    process = subprocess.run(command, text=True, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
    return process.stdout.strip().splitlines()[0] if process.stdout else f"exit {process.returncode}"


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"FAIL: {error}", file=sys.stderr)
        raise SystemExit(1)
