#!/usr/bin/env python3
"""Run the maintained D&D Character reference against all exercise tests in isolation."""

from __future__ import annotations

import json
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
from pathlib import Path


SCRIPT = Path(__file__).resolve()
REPO_ROOT = SCRIPT.parents[2]
EXERCISE_REL = Path("exercises/practice/dnd-character")
EXERCISE = REPO_ROOT / EXERCISE_REL
CONFIG_PATH = EXERCISE / ".meta" / "config.json"
REFERENCE = EXERCISE / ".meta" / "src" / "reference" / "java" / "DnDCharacter.java"
LEARNER_DISABLED = re.compile(
    r'(?m)^[ \t]*@Disabled\("Remove to run test"\)[ \t]*\r?\n'
)


def run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    print("+", " ".join(command), f"(cwd={cwd})")
    return subprocess.run(
        command,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def main() -> int:
    if not CONFIG_PATH.is_file() or not REFERENCE.is_file():
        print(f"Required exercise metadata/reference not found under {REPO_ROOT}", file=sys.stderr)
        return 2

    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    solution_paths = config["files"]["solution"]
    test_paths = config["files"]["test"]
    if not solution_paths or not test_paths:
        print("config.json must define at least one solution and test path", file=sys.stderr)
        return 2

    wrapper = REPO_ROOT / "gradlew"
    if not wrapper.is_file():
        wrapper = EXERCISE / "gradlew"
    if not wrapper.is_file():
        print("Gradle wrapper not found at repository root or exercise root; cannot run ./gradlew test.", file=sys.stderr)
        return 2

    with tempfile.TemporaryDirectory(prefix="r58-t011-") as temp_name:
        scratch = Path(temp_name) / "dnd-character"
        shutil.copytree(EXERCISE, scratch, ignore=shutil.ignore_patterns("build", ".gradle"))
        scratch_wrapper = scratch / "gradlew"
        shutil.copy2(wrapper, scratch_wrapper)
        wrapper_dir = wrapper.parent / "gradle" / "wrapper"
        if wrapper_dir.is_dir():
            shutil.copytree(wrapper_dir, scratch / "gradle" / "wrapper", dirs_exist_ok=True)
        scratch_wrapper.chmod(scratch_wrapper.stat().st_mode | 0o111)

        for relative_solution in solution_paths:
            destination = scratch / relative_solution
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(REFERENCE, destination)

        # Exercism starter tests are intentionally @Disabled for learners.
        # Enable only that standard marker in the temporary copy so the
        # maintained reference is exercised against the complete test suite.
        enabled_from_scratch = 0
        for relative_test in test_paths:
            test_file = scratch / relative_test
            original = test_file.read_text(encoding="utf-8")
            updated, count = LEARNER_DISABLED.subn("", original)
            enabled_from_scratch += count
            if count:
                test_file.write_text(updated, encoding="utf-8")
        print(f"Enabled {enabled_from_scratch} learner-disabled tests in the temporary copy only.")

        result = run(["./gradlew", "test", "--no-daemon"], scratch)
        print(result.stdout)

        report_files = sorted((scratch / "build" / "test-results" / "test").glob("TEST-*.xml"))
        totals = {"tests": 0, "failures": 0, "errors": 0, "skipped": 0}
        for report in report_files:
            root = ET.parse(report).getroot()
            for key in totals:
                totals[key] += int(root.attrib.get(key, "0"))
        executed = totals["tests"] - totals["skipped"]

        evidence = {
            "task": "R58-T011",
            "timestamp_unix": int(time.time()),
            "python": sys.version,
            "platform": platform.platform(),
            "command": "./gradlew test --no-daemon",
            "return_code": result.returncode,
            "learner_disabled_tests_enabled_in_temporary_copy": enabled_from_scratch,
            "test_reports": [str(path.relative_to(scratch)) for path in report_files],
            **totals,
            "executed": executed,
        }
        evidence_path = REPO_ROOT / "work" / "R58-T011" / "latest-result.json"
        evidence_path.parent.mkdir(parents=True, exist_ok=True)
        evidence_path.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(evidence, indent=2))

        if result.returncode != 0:
            print("FAIL: Gradle returned a non-zero exit code.", file=sys.stderr)
            return result.returncode or 1
        if executed == 0:
            print("FAIL: Gradle reported zero non-skipped tests.", file=sys.stderr)
            return 1
        if totals["failures"] or totals["errors"]:
            print("FAIL: one or more tests failed.", file=sys.stderr)
            return 1
        if totals["skipped"]:
            print("FAIL: one or more tests were unexpectedly skipped.", file=sys.stderr)
            return 1
        print(f"PASS: {executed} tests executed; no skips, failures, or errors.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
