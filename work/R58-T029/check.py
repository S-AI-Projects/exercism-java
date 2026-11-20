#!/usr/bin/env python3
"""Exercise the focused runner and retain expected/actual evidence."""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = Path(__file__).resolve().parent
RUNNER = ROOT / "tools/course_checks/r58-t029.py"
VARIANTS = ("reference", "failing", "empty", "interrupt")


def capture(command, cwd, timeout=420):
    try:
        completed = subprocess.run(command, cwd=cwd, text=True, capture_output=True,
                                   timeout=timeout)
        return {"command": command, "returncode": completed.returncode,
                "stdout": completed.stdout, "stderr": completed.stderr,
                "timed_out": False}
    except subprocess.TimeoutExpired as error:
        return {"command": command, "returncode": 124,
                "stdout": error.stdout or "", "stderr": error.stderr or "",
                "timed_out": True}


def save(results):
    (EVIDENCE / "results.json").write_text(json.dumps(results, indent=2) + "\n")


def check_run(variant, process, report):
    actual = report["actual"]
    if actual["learner_hashes_match"] is not True:
        raise AssertionError(f"{variant}: learner solution hashes changed")
    if actual["scratch_cleaned"] is not True:
        raise AssertionError(f"{variant}: temporary copy was not cleaned")
    if variant == "reference":
        counts = actual["test_counts"]
        if process["returncode"] != 0 or actual["gradle_returncode"] != 0:
            raise AssertionError("reference run did not pass")
        if not counts or counts["executed"] <= 0 or counts["failures"] or counts["errors"]:
            raise AssertionError("reference run had zero executed cases or failures")
    elif variant == "failing":
        counts = actual["test_counts"]
        if process["returncode"] == 0 or actual["gradle_returncode"] == 0:
            raise AssertionError("failing reference did not propagate a non-zero child status")
        if process["returncode"] != actual["gradle_returncode"]:
            raise AssertionError("runner did not propagate the Gradle child status unchanged")
        if not counts or counts["executed"] <= 0 or counts["failures"] + counts["errors"] == 0:
            raise AssertionError("failing reference did not produce a test assertion failure")
    elif variant == "empty":
        if process["returncode"] == 0:
            raise AssertionError("zero-test run did not fail at the runner level")
        if not actual["test_counts"] or actual["test_counts"]["executed"] != 0:
            raise AssertionError("empty test selection was not detected as zero tests")
        if report["runner_error"] != "zero tests executed":
            raise AssertionError("runner did not identify the zero-test condition")
    elif variant == "interrupt":
        if process["returncode"] != 130 or report["interrupted"] is not True:
            raise AssertionError("interruption did not return status 130")


def main():
    homebrew_jdk = Path("/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home")
    if homebrew_jdk.is_dir():
        os.environ["JAVA_HOME"] = str(homebrew_jdk)
        os.environ["PATH"] = str(homebrew_jdk / "bin") + os.pathsep + os.environ.get("PATH", "")
    results = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "inputs": {"runner": str(RUNNER.relative_to(ROOT)), "variants": list(VARIANTS)},
        "expected": {
            "reference": "runner exits 0; tests execute and pass",
            "failing": "runner propagates non-zero Gradle status and assertion failure",
            "empty": "runner exits non-zero when zero tests execute",
            "interrupt": "runner exits 130 and cleans temporary copy",
            "all_variants": "learner hashes match before/after every run",
        },
        "tool_versions": {
            "python": capture(["python3", "--version"], ROOT),
            "java": capture(["java", "-version"], ROOT),
            "javac": capture(["javac", "-version"], ROOT),
        },
        "runs": {},
    }
    save(results)
    if any(value["returncode"] != 0 for value in results["tool_versions"].values()):
        raise AssertionError("Could not record all required tool versions")
    for variant in VARIANTS:
        process = capture([sys.executable, str(RUNNER), "--variant", variant], ROOT, timeout=420)
        entry = {"expected": results["expected"][variant], "process": process, "report": None,
                 "passed": False}
        results["runs"][variant] = entry
        try:
            report = json.loads(process["stdout"])
            entry["report"] = report
            check_run(variant, process, report)
            entry["passed"] = True
        except (json.JSONDecodeError, AssertionError, KeyError, TypeError) as error:
            entry["assertion_error"] = str(error)
            save(results)
            raise AssertionError(f"{variant} runner check failed: {error}") from error
        finally:
            save(results)

    real_counts = results["runs"]["reference"]["report"]["actual"]["test_counts"]
    print("Reference cases: {tests} reported, {executed} executed, {skipped} skipped, {failures} failed".format(**real_counts))
    print("Failing reference, zero-test, and interruption exit statuses: verified")
    print("Learner solution hashes match after all four runs; temporary copies cleaned")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"R58-T029 check failed: {error}", file=sys.stderr)
        sys.exit(1)
