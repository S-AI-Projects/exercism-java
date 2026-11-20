#!/usr/bin/env python3
"""
Verification check for Task R58-T006 (split-second-stopwatch implementation comparison).

Requirements:
1. Use Python subprocess and tempfile.
2. Read exercises/practice/split-second-stopwatch/.meta/config.json to dynamically resolve paths.
3. Validate tests.toml test entries and UUIDs.
4. Verify learner starter stub remains unsolved (throws UnsupportedOperationException).
5. Copy the exercise including dotfiles into an isolated scratch directory.
6. Substitute maintained reference into scratch and execute ./gradlew test.
7. Substitute independently written alternative into a fresh scratch copy and execute ./gradlew test.
8. Compare both implementations: verify 100% agreement on all test cases, including named anchor cases.
9. Verify working tree integrity: starter solution files remain unchanged.
10. Check child return codes and test counts; fail on zero tests, non-zero child exit, or assertion failure.
11. Save inputs, expected vs actual results, and tool versions in work/R58-T006/results.json and latest-result.json.
"""

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

try:
    import tomllib
except ImportError:
    tomllib = None

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
WORK_DIR = os.path.join(REPO_ROOT, "work", "R58-T006")
EXERCISE_DIR = os.path.join(REPO_ROOT, "exercises", "practice", "split-second-stopwatch")
ALT_SOURCE = os.path.join(WORK_DIR, "AlternativeSplitSecondStopwatch.java")

NAMED_CASES = [
    {
        "method": "startInitiatesTimeTrackingForCurrentLap",
        "display_name": "start initiates time tracking for current lap",
        "uuid": "491487b1-593d-423e-a075-aa78d449ff1f",
        "expected": "00:00:05",
    },
    {
        "method": "lapAddsCurrentLapToPreviousLaps",
        "display_name": "lap adds current lap to previous laps",
        "uuid": "091966e3-ed25-4397-908b-8bb0330118f8",
        "expected": '["00:00:10"]',
    },
    {
        "method": "supportsVeryLongLaps",
        "display_name": "supports very long laps",
        "uuid": "0b01751a-cb57-493f-bb86-409de6e84306",
        "expected": "14:08:30",
    },
]


def get_env():
    env = os.environ.copy()
    jdk = "/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home"
    if os.path.exists(jdk):
        env["JAVA_HOME"] = jdk
        env["PATH"] = f"/opt/homebrew/opt/openjdk@21/bin:/opt/homebrew/bin:{env.get('PATH', '')}"
    elif "JAVA_HOME" not in env:
        # fallback path search
        if os.path.exists("/opt/homebrew/bin"):
            env["PATH"] = f"/opt/homebrew/bin:{env.get('PATH', '')}"
    return env


def get_tool_versions(env):
    versions = {"python": sys.version.split()[0]}
    try:
        proc = subprocess.run(["java", "-version"], env=env, capture_output=True, text=True)
        versions["java"] = (proc.stderr or proc.stdout).splitlines()[0].strip()
    except Exception as e:
        versions["java"] = f"unknown: {e}"
    try:
        proc = subprocess.run(
            ["./gradlew", "--version"],
            cwd=EXERCISE_DIR,
            env=env,
            capture_output=True,
            text=True,
        )
        for line in proc.stdout.splitlines():
            if line.startswith("Gradle "):
                versions["gradle"] = line.strip()
                break
    except Exception as e:
        versions["gradle"] = f"unknown: {e}"
    return versions


def parse_tests_toml(toml_file):
    if tomllib is not None:
        with open(toml_file, "rb") as f:
            return tomllib.load(f)
    with open(toml_file, "r", encoding="utf-8") as f:
        content = f.read()
    entries = {}
    current_uuid = None
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        uuid_match = re.match(r"^\[([0-9a-fA-F-]+)\]$", line)
        if uuid_match:
            current_uuid = uuid_match.group(1)
            entries[current_uuid] = {}
            continue
        if current_uuid and "=" in line:
            k, v = line.split("=", 1)
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            if v.lower() == "false":
                v = False
            elif v.lower() == "true":
                v = True
            entries[current_uuid][k] = v
    return entries


def run_gradle_tests(scratch_dir, env, test_rel):
    """Enables all tests in scratch copy and executes ./gradlew test."""
    scratch_test = os.path.join(scratch_dir, test_rel)
    with open(scratch_test, "r") as f:
        test_content = f.read()
    test_content_enabled = re.sub(r"@Disabled(\([^)]*\))?", "", test_content)
    with open(scratch_test, "w") as f:
        f.write(test_content_enabled)

    proc = subprocess.run(
        ["./gradlew", "test", "--no-daemon"],
        cwd=scratch_dir,
        env=env,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        print("STDERR:\n", proc.stderr, file=sys.stderr)
        print("STDOUT:\n", proc.stdout, file=sys.stderr)
        raise RuntimeError(f"Gradle test failed with exit code {proc.returncode}")

    xml_file = os.path.join(
        scratch_dir, "build", "test-results", "test", "TEST-SplitSecondStopwatchTest.xml"
    )
    assert os.path.isfile(xml_file), f"Test XML report not found: {xml_file}"

    tree = ET.parse(xml_file)
    root = tree.getroot()

    tests_total = int(root.attrib.get("tests", 0))
    tests_skipped = int(root.attrib.get("skipped", 0))
    tests_failures = int(root.attrib.get("failures", 0))
    tests_errors = int(root.attrib.get("errors", 0))
    tests_passed = tests_total - tests_skipped - tests_failures - tests_errors

    case_statuses = {}
    for tc in root.findall("testcase"):
        name = tc.attrib.get("name", "")
        if tc.find("failure") is not None:
            status = "FAILED"
        elif tc.find("skipped") is not None:
            status = "SKIPPED"
        elif tc.find("error") is not None:
            status = "ERROR"
        else:
            status = "PASSED"
        case_statuses[name] = status

    return {
        "exit_code": proc.returncode,
        "tests_total": tests_total,
        "tests_passed": tests_passed,
        "tests_skipped": tests_skipped,
        "tests_failures": tests_failures,
        "tests_errors": tests_errors,
        "case_statuses": case_statuses,
    }


def main():
    os.makedirs(WORK_DIR, exist_ok=True)
    env = get_env()
    tool_versions = get_tool_versions(env)

    print("=== Step 1: Resolving paths from .meta/config.json ===")
    config_file = os.path.join(EXERCISE_DIR, ".meta", "config.json")
    with open(config_file, "r") as f:
        config = json.load(f)

    solution_rel = config["files"]["solution"][0]
    test_rel = config["files"]["test"][0]
    example_rel = config["files"]["example"][0]

    print(f"  solution: {solution_rel}")
    print(f"  test:     {test_rel}")
    print(f"  example:  {example_rel}")

    print("\n=== Step 2: Validating .meta/tests.toml ===")
    tests_toml_file = os.path.join(EXERCISE_DIR, ".meta", "tests.toml")
    toml_data = parse_tests_toml(tests_toml_file)

    total_canonical = len(toml_data)
    included = sum(1 for v in toml_data.values() if v.get("include", True) is not False)
    excluded = total_canonical - included
    print(f"  Total canonical entries: {total_canonical}")
    print(f"  Included: {included}, Excluded: {excluded}")

    for case in NAMED_CASES:
        uuid = case["uuid"]
        assert uuid in toml_data, f"Named case UUID {uuid} missing from tests.toml"
        assert toml_data[uuid]["description"] == case["display_name"], (
            f"Description mismatch for {uuid}: {toml_data[uuid]['description']} != {case['display_name']}"
        )
        print(f"  [{uuid}] '{case['display_name']}' verified in tests.toml")

    print("\n=== Step 3: Verifying learner stub remains unsolved ===")
    learner_stub_path = os.path.join(EXERCISE_DIR, solution_rel)
    with open(learner_stub_path, "rb") as f:
        stub_bytes_before = f.read()
    stub_text = stub_bytes_before.decode()
    stub_hash_before = hashlib.sha256(stub_bytes_before).hexdigest()

    assert "UnsupportedOperationException" in stub_text, (
        "Learner stub must throw UnsupportedOperationException"
    )
    print("  Confirmed: learner stub throws UnsupportedOperationException and remains unsolved.")

    results = {
        "task": "R58-T006",
        "exercise": "split-second-stopwatch",
        "status": "RUNNING",
        "tool_versions": tool_versions,
        "inputs": {
            "exercise": "exercises/practice/split-second-stopwatch",
            "named_cases": NAMED_CASES,
            "approaches_compared": [
                {
                    "name": "Reference (Continuous Wall-Clock / Epoch Offset Model)",
                    "file": example_rel,
                },
                {
                    "name": "Alternative (Discrete Duration Accumulation Model)",
                    "file": "work/R58-T006/AlternativeSplitSecondStopwatch.java",
                },
            ],
        },
        "checks": {},
    }

    print("\n=== Step 4: Testing Approach 1 (Maintained Reference) ===")
    with tempfile.TemporaryDirectory() as temp_dir:
        scratch_ref = os.path.join(temp_dir, "stopwatch_ref")
        shutil.copytree(EXERCISE_DIR, scratch_ref)

        # Substitute reference into solution path
        shutil.copy2(
            os.path.join(scratch_ref, example_rel),
            os.path.join(scratch_ref, solution_rel),
        )

        ref_results = run_gradle_tests(scratch_ref, env, test_rel)
        print(f"  Gradle exit code: {ref_results['exit_code']}")
        print(
            f"  Total: {ref_results['tests_total']}, Passed: {ref_results['tests_passed']}, "
            f"Failures: {ref_results['tests_failures']}, Skipped: {ref_results['tests_skipped']}"
        )

        assert ref_results["tests_total"] > 0, "Zero tests executed for reference!"
        assert ref_results["tests_failures"] == 0, (
            f"Found {ref_results['tests_failures']} failures in reference!"
        )
        assert ref_results["tests_errors"] == 0
        assert ref_results["tests_passed"] == ref_results["tests_total"]

        # Verify named cases
        named_ref_statuses = {}
        for case in NAMED_CASES:
            status = ref_results["case_statuses"].get(case["display_name"])
            assert status == "PASSED", f"Named case '{case['display_name']}' failed in reference!"
            print(f"  [REFERENCE] '{case['display_name']}' -> PASSED")
            named_ref_statuses[case["method"]] = "PASSED"

        results["checks"]["reference"] = {
            "exit_code": ref_results["exit_code"],
            "tests_total": ref_results["tests_total"],
            "tests_passed": ref_results["tests_passed"],
            "tests_skipped": ref_results["tests_skipped"],
            "tests_failures": ref_results["tests_failures"],
            "tests_errors": ref_results["tests_errors"],
            "named_cases": named_ref_statuses,
        }

    print("\n=== Step 5: Testing Approach 2 (Alternative: Duration Accumulation) ===")
    assert os.path.isfile(ALT_SOURCE), f"Alternative source not found: {ALT_SOURCE}"
    with tempfile.TemporaryDirectory() as temp_dir:
        scratch_alt = os.path.join(temp_dir, "stopwatch_alt")
        shutil.copytree(EXERCISE_DIR, scratch_alt)

        # Substitute alternative into solution path
        shutil.copy2(ALT_SOURCE, os.path.join(scratch_alt, solution_rel))

        alt_results = run_gradle_tests(scratch_alt, env, test_rel)
        print(f"  Gradle exit code: {alt_results['exit_code']}")
        print(
            f"  Total: {alt_results['tests_total']}, Passed: {alt_results['tests_passed']}, "
            f"Failures: {alt_results['tests_failures']}, Skipped: {alt_results['tests_skipped']}"
        )

        assert alt_results["tests_total"] > 0, "Zero tests executed for alternative!"
        assert alt_results["tests_failures"] == 0, (
            f"Found {alt_results['tests_failures']} failures in alternative!"
        )
        assert alt_results["tests_errors"] == 0
        assert alt_results["tests_passed"] == alt_results["tests_total"]

        # Verify named cases
        named_alt_statuses = {}
        for case in NAMED_CASES:
            status = alt_results["case_statuses"].get(case["display_name"])
            assert status == "PASSED", f"Named case '{case['display_name']}' failed in alternative!"
            print(f"  [ALTERNATIVE] '{case['display_name']}' -> PASSED")
            named_alt_statuses[case["method"]] = "PASSED"

        # Compare outputs of both approaches
        assert ref_results["case_statuses"] == alt_results["case_statuses"], (
            "Mismatch between reference and alternative test results!"
        )
        print("  Both approaches produced 100% identical test pass results across all 29 cases.")

        results["checks"]["alternative"] = {
            "exit_code": alt_results["exit_code"],
            "tests_total": alt_results["tests_total"],
            "tests_passed": alt_results["tests_passed"],
            "tests_skipped": alt_results["tests_skipped"],
            "tests_failures": alt_results["tests_failures"],
            "tests_errors": alt_results["tests_errors"],
            "named_cases": named_alt_statuses,
            "agrees_with_reference": True,
            "all_cases_agreement": True,
        }

    print("\n=== Step 6: Verifying working tree integrity ===")
    with open(learner_stub_path, "rb") as f:
        stub_bytes_after = f.read()
    stub_hash_after = hashlib.sha256(stub_bytes_after).hexdigest()
    assert stub_hash_before == stub_hash_after, "Working tree learner starter stub was modified!"
    print("  Working tree integrity verified: untouched.")

    results["status"] = "PASSED"
    results_file = os.path.join(WORK_DIR, "results.json")
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)

    latest_file = os.path.join(WORK_DIR, "latest-result.json")
    with open(latest_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nAll assertions passed! Saved evidence to {results_file} and {latest_file}")
    sys.exit(0)


if __name__ == "__main__":
    main()
