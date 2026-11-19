#!/usr/bin/env python3
"""
Verification check for Task R58-T026 (Darts implementation approach comparison).

Requirements:
1. Use Python subprocess and tempfile.
2. Read exercises/practice/darts/.meta/config.json.
3. Resolve solution, test, and reference paths dynamically.
4. Copy the complete exercise, including dotfiles, into a temporary directory.
5. Substitute the maintained reference into scratch src/main/java and run ./gradlew test.
6. Verify reference passes all 13 tests (including named cases: missedTarget, onTheOuterCircle,
   onTheMiddleCircle, onTheInnerCircle).
7. Test the alternative implementation (squared radius approach) against the same test suite.
8. Verify both implementations agree on all test cases.
9. Verify original learner solution remains unsolved (throws UnsupportedOperationException).
10. Check child return codes and test counts; fail if zero tests or any failure.
11. Save inputs, expected vs actual results, and tool versions in work/R58-T026/results.json.
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
import xml.etree.ElementTree as ET

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
WORK_DIR = os.path.join(REPO_ROOT, "work", "R58-T026")
EXERCISE_DIR = os.path.join(REPO_ROOT, "exercises", "practice", "darts")
ALT_SOURCE = os.path.join(WORK_DIR, "AlternativeDarts.java")

NAMED_CASES = [
    {
        "method": "missedTarget",
        "display_name": "Missed target",
        "uuid": "9033f731-0a3a-4d9c-b1c0-34a1c8362afb",
        "input": {"x": -9.0, "y": 9.0},
        "expected": 0,
    },
    {
        "method": "onTheOuterCircle",
        "display_name": "On the outer circle",
        "uuid": "4c9f6ff4-c489-45fd-be8a-1fcb08b4d0ba",
        "input": {"x": 0.0, "y": 10.0},
        "expected": 1,
    },
    {
        "method": "onTheMiddleCircle",
        "display_name": "On the middle circle",
        "uuid": "14378687-ee58-4c9b-a323-b089d5274be8",
        "input": {"x": -5.0, "y": 0.0},
        "expected": 5,
    },
    {
        "method": "onTheInnerCircle",
        "display_name": "On the inner circle",
        "uuid": "849e2e63-85bd-4fed-bc3b-781ae962e2c9",
        "input": {"x": 0.0, "y": -1.0},
        "expected": 10,
    },
]


def get_env():
    env = os.environ.copy()
    jdk = "/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home"
    if os.path.exists(jdk):
        env["JAVA_HOME"] = jdk
        env["PATH"] = f"/opt/homebrew/opt/openjdk@21/bin:{env.get('PATH', '')}"
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


def run_gradle_tests(scratch_dir, env, test_rel):
    """Enables all tests in scratch copy and executes ./gradlew test."""
    scratch_test = os.path.join(scratch_dir, test_rel)
    with open(scratch_test, "r") as f:
        test_content = f.read()
    test_content_enabled = re.sub(r'@Disabled(\([^)]*\))?', "", test_content)
    with open(scratch_test, "w") as f:
        f.write(test_content_enabled)

    proc = subprocess.run(
        ["./gradlew", "test"],
        cwd=scratch_dir,
        env=env,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        print("STDERR:\n", proc.stderr)
        print("STDOUT:\n", proc.stdout)
        sys.exit(proc.returncode)

    xml_file = os.path.join(
        scratch_dir, "build", "test-results", "test", "TEST-DartsTest.xml"
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

    print("=== Step 1: Resolving paths from config.json ===")
    config_file = os.path.join(EXERCISE_DIR, ".meta", "config.json")
    with open(config_file, "r") as f:
        config = json.load(f)

    solution_rel = config["files"]["solution"][0]
    test_rel = config["files"]["test"][0]
    example_rel = config["files"]["example"][0]

    print(f"  solution: {solution_rel}")
    print(f"  test:     {test_rel}")
    print(f"  example:  {example_rel}")

    print("\n=== Step 2: Validating tests.toml ===")
    tests_toml_file = os.path.join(EXERCISE_DIR, ".meta", "tests.toml")
    with open(tests_toml_file, "rb") as f:
        toml_data = tomllib.load(f)

    total_canonical = len(toml_data)
    included = sum(1 for v in toml_data.values() if v.get("include", True) is not False)
    excluded = total_canonical - included
    print(f"  Total canonical entries: {total_canonical}")
    print(f"  Included: {included}, Excluded: {excluded}")

    for case in NAMED_CASES:
        uuid = case["uuid"]
        assert uuid in toml_data, f"Named case UUID {uuid} missing from tests.toml"
        print(f"  [{uuid}] '{toml_data[uuid]['description']}' OK")

    print("\n=== Step 3: Verifying learner stub remains unsolved ===")
    learner_stub_path = os.path.join(EXERCISE_DIR, solution_rel)
    with open(learner_stub_path, "r") as f:
        stub_content = f.read()
    assert "UnsupportedOperationException" in stub_content, "Learner stub must remain unsolved!"
    print("  Confirmed: learner stub throws UnsupportedOperationException.")

    results = {
        "status": "RUNNING",
        "tool_versions": tool_versions,
        "inputs": {
            "exercise": "exercises/practice/darts",
            "named_cases": NAMED_CASES,
            "approaches_compared": [
                {
                    "name": "Reference (Euclidean distance via Math.sqrt)",
                    "file": example_rel,
                },
                {
                    "name": "Alternative (Squared Euclidean distance)",
                    "file": "work/R58-T026/AlternativeDarts.java",
                },
            ],
        },
        "checks": {},
    }

    print("\n=== Step 4: Testing Approach 1 (Maintained Reference) ===")
    with tempfile.TemporaryDirectory() as temp_dir:
        scratch_ref = os.path.join(temp_dir, "darts_ref")
        shutil.copytree(EXERCISE_DIR, scratch_ref)

        # Substitute reference
        shutil.copy2(
            os.path.join(scratch_ref, example_rel),
            os.path.join(scratch_ref, solution_rel),
        )

        ref_results = run_gradle_tests(scratch_ref, env, test_rel)
        print(f"  Gradle exit code: {ref_results['exit_code']}")
        print(f"  Total: {ref_results['tests_total']}, Passed: {ref_results['tests_passed']}, "
              f"Failures: {ref_results['tests_failures']}, Skipped: {ref_results['tests_skipped']}")

        assert ref_results["tests_total"] > 0, "Zero tests executed!"
        assert ref_results["tests_failures"] == 0, f"Found {ref_results['tests_failures']} failures in reference!"
        assert ref_results["tests_errors"] == 0

        # Verify named cases
        for case in NAMED_CASES:
            status = ref_results["case_statuses"].get(case["display_name"])
            assert status == "PASSED", f"Named case '{case['display_name']}' failed in reference!"
            print(f"  [REFERENCE] '{case['display_name']}' -> PASSED")

        results["checks"]["reference"] = {
            "exit_code": ref_results["exit_code"],
            "tests_total": ref_results["tests_total"],
            "tests_passed": ref_results["tests_passed"],
            "tests_skipped": ref_results["tests_skipped"],
            "tests_failures": ref_results["tests_failures"],
            "tests_errors": ref_results["tests_errors"],
            "named_cases": {c["method"]: "PASSED" for c in NAMED_CASES},
        }

    print("\n=== Step 5: Testing Approach 2 (Alternative: Squared Distance) ===")
    assert os.path.isfile(ALT_SOURCE), f"Alternative source not found: {ALT_SOURCE}"
    with tempfile.TemporaryDirectory() as temp_dir:
        scratch_alt = os.path.join(temp_dir, "darts_alt")
        shutil.copytree(EXERCISE_DIR, scratch_alt)

        # Substitute alternative
        shutil.copy2(ALT_SOURCE, os.path.join(scratch_alt, solution_rel))

        alt_results = run_gradle_tests(scratch_alt, env, test_rel)
        print(f"  Gradle exit code: {alt_results['exit_code']}")
        print(f"  Total: {alt_results['tests_total']}, Passed: {alt_results['tests_passed']}, "
              f"Failures: {alt_results['tests_failures']}, Skipped: {alt_results['tests_skipped']}")

        assert alt_results["tests_total"] > 0, "Zero tests executed!"
        assert alt_results["tests_failures"] == 0, f"Found {alt_results['tests_failures']} failures in alternative!"
        assert alt_results["tests_errors"] == 0

        # Verify named cases
        for case in NAMED_CASES:
            status = alt_results["case_statuses"].get(case["display_name"])
            assert status == "PASSED", f"Named case '{case['display_name']}' failed in alternative!"
            print(f"  [ALTERNATIVE] '{case['display_name']}' -> PASSED")

        # Compare outputs of both approaches
        assert ref_results["case_statuses"] == alt_results["case_statuses"], (
            "Mismatch between reference and alternative test results!"
        )
        print("  Both approaches produced 100% identical test pass results.")

        results["checks"]["alternative"] = {
            "exit_code": alt_results["exit_code"],
            "tests_total": alt_results["tests_total"],
            "tests_passed": alt_results["tests_passed"],
            "tests_skipped": alt_results["tests_skipped"],
            "tests_failures": alt_results["tests_failures"],
            "tests_errors": alt_results["tests_errors"],
            "named_cases": {c["method"]: "PASSED" for c in NAMED_CASES},
            "agrees_with_reference": True,
        }

    # Verify working tree was not rewritten
    with open(learner_stub_path, "r") as f:
        after_stub = f.read()
    assert after_stub == stub_content, "Working tree starter file was modified!"
    print("\n  Working tree integrity verified: untouched.")

    results["status"] = "PASSED"
    results_file = os.path.join(WORK_DIR, "results.json")
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nAll assertions passed! Saved evidence to {results_file}")
    sys.exit(0)


if __name__ == "__main__":
    main()
