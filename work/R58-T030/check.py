#!/usr/bin/env python3
"""Run selected grep contract tests against the reference in a scratch copy."""

import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXERCISE = ROOT / "exercises/practice/grep"
EVIDENCE = Path(__file__).resolve().parent
CASES = [
    {
        "method": "multipleFilesOneMatchMultipleFlags",
        "display_name": "Multiple files, one match, multiple flags",
        "pattern": "WITH LOSS OF EDEN, TILL ONE GREATER MAN",
        "flags": ["-n", "-i", "-x"],
        "files": ["iliad.txt", "midsummer-night.txt", "paradise-lost.txt"],
        "expected_output": "paradise-lost.txt:4:With loss of Eden, till one greater Man",
    },
    {
        "method": "multipleFilesSeveralMatchesFileFlagTakesPrecedenceOverLineNumberFlag",
        "display_name": "Multiple files, several matches, file flag takes precedence over line number flag",
        "pattern": "who",
        "flags": ["-n", "-l"],
        "files": ["iliad.txt", "midsummer-night.txt", "paradise-lost.txt"],
        "expected_output": "iliad.txt\nparadise-lost.txt",
    },
]


def run(command, cwd, env, timeout=300):
    completed = subprocess.run(command, cwd=cwd, text=True, capture_output=True,
                               timeout=timeout, env=env)
    return {"command": command, "returncode": completed.returncode,
            "stdout": completed.stdout, "stderr": completed.stderr}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def is_within(path, root):
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def save(results):
    (EVIDENCE / "results.json").write_text(json.dumps(results, indent=2) + "\n")


def instrument_selected_test(test_source, case, index):
    display = re.escape(case["display_name"])
    disable_pattern = rf'@Disabled\("Remove to run test"\)\s*(?=@Test\s*@DisplayName\("{display}"\))'
    test_source, disabled_count = re.subn(disable_pattern, "", test_source)
    if disabled_count != 1:
        raise AssertionError(f"Could not enable exactly one selected test: {case['method']}")

    method_pattern = (rf'(?s)(public void {re.escape(case["method"])}\(\)\s*\{{'
                      rf'.*?String actual = grepTool\.grep\(.*?;\s*)assertThat\(actual\)')
    marker = f"R58T030_CASE{index}"
    def insert_marker(match):
        return (match.group(1) + f'        System.out.println("{marker}=" + '
                'actual.replace("\\n", "<NL>"));\n        assertThat(actual)')

    test_source, instrumented_count = re.subn(method_pattern, insert_marker, test_source, count=1)
    if instrumented_count != 1:
        raise AssertionError(f"Could not instrument output for {case['method']}")
    return test_source, marker


def main():
    jdk_home = Path("/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home")
    env = os.environ.copy()
    if jdk_home.is_dir():
        env["JAVA_HOME"] = str(jdk_home)
        env["PATH"] = str(jdk_home / "bin") + os.pathsep + env.get("PATH", "")

    config_path = EXERCISE / ".meta/config.json"
    config = json.loads(config_path.read_text())
    roles = config["files"]
    solution_paths = [EXERCISE / value for value in roles["solution"]]
    test_paths = [EXERCISE / value for value in roles["test"]]
    example_paths = [EXERCISE / value for value in roles["example"]]
    if not solution_paths or not test_paths or not example_paths:
        raise AssertionError("config.json must declare solution, test, and example paths")
    if len(solution_paths) != len(example_paths):
        raise AssertionError("solution and example path lists must have matching lengths")
    for path in solution_paths + test_paths + example_paths:
        if not path.is_file() or not is_within(path, EXERCISE):
            raise AssertionError(f"missing or out-of-exercise config path: {path}")

    before_hashes = {str(path.relative_to(ROOT)): sha256(path) for path in solution_paths}
    results = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "inputs": {"config_path": str(config_path.relative_to(ROOT)), "file_roles": roles,
                   "cases": CASES},
        "expected": {"gradle_returncode": 0, "minimum_executed_tests": 1,
                     "selected_case_outputs_equal_expected": True,
                     "learner_hashes_unchanged": True},
        "tool_versions": {
            "python": run(["python3", "--version"], ROOT, env),
            "java": run(["java", "-version"], ROOT, env),
            "javac": run(["javac", "-version"], ROOT, env),
        },
        "reference_run": None,
    }
    save(results)
    for name, version in results["tool_versions"].items():
        if version["returncode"] != 0:
            raise AssertionError(f"Unable to record {name} version")

    scratch_root = None
    try:
        with tempfile.TemporaryDirectory(prefix="r58-t030-grep-") as temporary:
            scratch_root = Path(temporary)
            scratch = scratch_root / "grep"
            shutil.copytree(EXERCISE, scratch, ignore=shutil.ignore_patterns("build", ".gradle"))
            for example, solution in zip(example_paths, solution_paths):
                target = scratch / solution.relative_to(EXERCISE)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(example, target)

            scratch_test = scratch / test_paths[0].relative_to(EXERCISE)
            source = scratch_test.read_text()
            markers = []
            for index, case in enumerate(CASES, start=1):
                source, marker = instrument_selected_test(source, case, index)
                markers.append(marker)
            scratch_test.write_text(source)

            wrapper = scratch / "gradlew"
            if not wrapper.is_file():
                raise AssertionError("Exercise Gradle wrapper is missing from scratch copy")
            wrapper.chmod(wrapper.stat().st_mode | 0o111)
            gradle = run(["./gradlew", "test"], scratch, env)
            report_files = sorted((scratch / "build/test-results/test").glob("TEST-*.xml"))
            counts = {"tests": 0, "failures": 0, "errors": 0, "skipped": 0}
            test_output = []
            for report in report_files:
                suite = ET.parse(report).getroot()
                for key in counts:
                    counts[key] += int(suite.attrib.get(key, 0))
                test_output.append(suite.findtext("system-out") or "")
            counts["executed"] = counts["tests"] - counts["skipped"]
            results["reference_run"] = {
                "gradle": gradle, "test_report_files": len(report_files), "test_counts": counts,
                "cases": CASES,
            }
            save(results)

            actual_outputs = {}
            captured_output = gradle["stdout"] + "\n" + gradle["stderr"] + "\n" + "\n".join(test_output)
            for marker in markers:
                matching_lines = [match.group(1) for line in captured_output.splitlines()
                                  if (match := re.match(rf"\s*{re.escape(marker)}=(.*)$", line))]
                if len(matching_lines) != 1:
                    raise AssertionError(f"Expected one captured result line for {marker}")
                actual_outputs[marker] = matching_lines[0].replace("<NL>", "\n")

            for index, (case, marker) in enumerate(zip(CASES, markers), start=1):
                case["actual_output"] = actual_outputs[marker]
                case["assertion_passed"] = case["actual_output"] == case["expected_output"]
                if not case["assertion_passed"]:
                    raise AssertionError(f"Reference output did not match case {index}")

            results["reference_run"]["cases"] = CASES
            save(results)
            if gradle["returncode"] != 0:
                raise AssertionError("Gradle reference test command returned non-zero")
            if counts["executed"] <= 0:
                raise AssertionError("Gradle reported zero executed tests")
            if counts["failures"] or counts["errors"]:
                raise AssertionError("Gradle test reports contain a failure")
    except Exception as error:
        results["assertion_error"] = str(error)
        raise
    finally:
        after_hashes = {str(path.relative_to(ROOT)): sha256(path) for path in solution_paths}
        results["learner_hashes_before"] = before_hashes
        results["learner_hashes_after"] = after_hashes
        results["learner_hashes_unchanged"] = before_hashes == after_hashes
        results["temporary_copy_cleaned"] = scratch_root is not None and not scratch_root.exists()
        save(results)

    if not results["learner_hashes_unchanged"]:
        raise AssertionError("Learner source changed during temporary reference run")
    if not results["temporary_copy_cleaned"]:
        raise AssertionError("Temporary exercise copy was not cleaned")

    counts = results["reference_run"]["test_counts"]
    print("Reference tests: {tests} reported, {executed} executed, {skipped} skipped, {failures} failed".format(**counts))
    for case in CASES:
        print(f"{case['method']}: output assertion passed")
    print("Learner solution unchanged; temporary copy cleaned")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"R58-T030 check failed: {error}")
        raise
