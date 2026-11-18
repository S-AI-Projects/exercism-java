#!/usr/bin/env python3
"""
Verification check for Task R58-T021 (Allergies canonical case rationale).
Verifies:
1. exercises/practice/allergies/.meta/tests.toml parses and has valid rationale comments for:
   - 17fc7296-2440-4ac4-ad7b-d07c321bc5a0
   - 07ced27b-1da5-4c2e-8ae2-cb2791437546
   - 5035b954-b6fa-4b9b-a487-dae69d8c5f96
2. Working tree learner stub src/main/java/Allergies.java remains unsolved.
3. In a temporary copy, reference solution replaces the stub and all named/enabled cases pass.
4. Records test counts, inputs, expected vs actual results, and tool versions in work/R58-T021/.
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
WORK_DIR = os.path.join(REPO_ROOT, "work", "R58-T021")
EXERCISE_DIR = os.path.join(REPO_ROOT, "exercises", "practice", "allergies")

TARGET_UUIDS = [
    "17fc7296-2440-4ac4-ad7b-d07c321bc5a0",
    "07ced27b-1da5-4c2e-8ae2-cb2791437546",
    "5035b954-b6fa-4b9b-a487-dae69d8c5f96",
]

NAMED_CASES = [
    {
        "uuid": "17fc7296-2440-4ac4-ad7b-d07c321bc5a0",
        "method": "eggsNotAllergicToAnything",
        "display_name": "not allergic to anything",
        "expected_result": "PASSED",
    },
    {
        "uuid": "07ced27b-1da5-4c2e-8ae2-cb2791437546",
        "method": "eggsAllergicOnlyToEggs",
        "display_name": "allergic only to eggs",
        "expected_result": "PASSED",
    },
    {
        "uuid": "5035b954-b6fa-4b9b-a487-dae69d8c5f96",
        "method": "eggsAllergicToEggsAndSomethingElse",
        "display_name": "allergic to eggs and something else",
        "expected_result": "PASSED",
    },
]


def get_tool_versions(env):
    """Collects versions of Python, Java, and Gradle."""
    versions = {}
    versions["python"] = sys.version.split()[0]

    # Java version
    try:
        proc = subprocess.run(["java", "-version"], env=env, capture_output=True, text=True, check=True)
        # java -version outputs to stderr
        first_line = (proc.stderr or proc.stdout).splitlines()[0]
        versions["java"] = first_line.strip()
    except Exception as e:
        versions["java"] = f"Unknown: {e}"

    # Gradle version
    try:
        proc = subprocess.run(
            ["./gradlew", "--version"],
            cwd=EXERCISE_DIR,
            env=env,
            capture_output=True,
            text=True,
            check=True,
        )
        for line in proc.stdout.splitlines():
            if line.startswith("Gradle "):
                versions["gradle"] = line.strip()
                break
    except Exception as e:
        versions["gradle"] = f"Unknown: {e}"

    return versions


def main():
    os.makedirs(WORK_DIR, exist_ok=True)
    results = {
        "status": "RUNNING",
        "checks": {},
        "tool_versions": {},
    }

    print("=== Step 1: Validating exercises/practice/allergies/.meta/config.json ===")
    config_file = os.path.join(EXERCISE_DIR, ".meta", "config.json")
    assert os.path.isfile(config_file), f"config.json not found: {config_file}"
    with open(config_file, "r") as f:
        config_data = json.load(f)

    solution_rel = config_data["files"]["solution"][0]
    test_rel = config_data["files"]["test"][0]
    example_rel = config_data["files"]["example"][0]
    print(f"  Resolved solution path: {solution_rel}")
    print(f"  Resolved test path:     {test_rel}")
    print(f"  Resolved example path:  {example_rel}")

    results["checks"]["config_json"] = {
        "solution": solution_rel,
        "test": test_rel,
        "example": example_rel,
    }

    print("\n=== Step 2: Validating exercises/practice/allergies/.meta/tests.toml ===")
    tests_toml_file = os.path.join(EXERCISE_DIR, ".meta", "tests.toml")
    assert os.path.isfile(tests_toml_file), f"tests.toml not found: {tests_toml_file}"
    with open(tests_toml_file, "rb") as f:
        toml_data = tomllib.load(f)

    total_canonical_cases = len(toml_data)
    included_count = sum(1 for v in toml_data.values() if v.get("include", True) is not False)
    excluded_count = total_canonical_cases - included_count

    print(f"  Total canonical entries: {total_canonical_cases}")
    print(f"  Included entries:       {included_count}")
    print(f"  Excluded entries:       {excluded_count}")

    uuid_rationales = {}
    for uuid in TARGET_UUIDS:
        assert uuid in toml_data, f"UUID {uuid} missing from tests.toml"
        entry = toml_data[uuid]
        comment = entry.get("comment", "")
        assert comment, f"UUID {uuid} missing comment/rationale in tests.toml"
        print(f"  [{uuid}] {entry.get('description')}")
        print(f"    Rationale: {comment}")
        uuid_rationales[uuid] = {
            "description": entry.get("description"),
            "comment": comment,
            "included": entry.get("include", True),
        }

    results["checks"]["tests_toml"] = {
        "total_cases": total_canonical_cases,
        "included_cases": included_count,
        "excluded_cases": excluded_count,
        "target_uuids": uuid_rationales,
    }

    print("\n=== Step 3: Checking learner stub remains unsolved ===")
    learner_solution = os.path.join(EXERCISE_DIR, solution_rel)
    with open(learner_solution, "r") as f:
        stub_content = f.read()
    assert "UnsupportedOperationException" in stub_content, "Learner stub must remain unsolved!"
    print("  Confirmed learner stub throws UnsupportedOperationException.")
    results["checks"]["learner_stub_unsolved"] = True

    print("\n=== Step 4: Running reference implementation in temporary directory ===")
    env = os.environ.copy()
    if os.path.exists("/opt/homebrew/opt/openjdk@21/bin"):
        env["JAVA_HOME"] = "/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home"
        env["PATH"] = f"/opt/homebrew/opt/openjdk@21/bin:{env.get('PATH', '')}"

    tool_versions = get_tool_versions(env)
    results["tool_versions"] = tool_versions
    print("  Tool versions:")
    for tool, ver in tool_versions.items():
        print(f"    {tool}: {ver}")

    with tempfile.TemporaryDirectory() as temp_dir:
        scratch_exercise = os.path.join(temp_dir, "allergies")
        shutil.copytree(EXERCISE_DIR, scratch_exercise)

        # Substitute reference into scratch solution
        scratch_ref = os.path.join(scratch_exercise, example_rel)
        scratch_sol = os.path.join(scratch_exercise, solution_rel)
        shutil.copy2(scratch_ref, scratch_sol)

        # In scratch copy only, enable disabled tests so the named cases execute
        scratch_test = os.path.join(scratch_exercise, test_rel)
        with open(scratch_test, "r") as f:
            test_content = f.read()
        test_content_enabled = test_content.replace('@Disabled("Remove to run test")', "")
        with open(scratch_test, "w") as f:
            f.write(test_content_enabled)

        # Run gradlew test
        proc = subprocess.run(
            ["./gradlew", "test"],
            cwd=scratch_exercise,
            env=env,
            capture_output=True,
            text=True,
        )

        print(f"  Gradle process exit code: {proc.returncode}")
        if proc.returncode != 0:
            print("STDERR:\n", proc.stderr)
            print("STDOUT:\n", proc.stdout)
            sys.exit(proc.returncode)

        # Parse test results from JUnit XML
        xml_report_dir = os.path.join(scratch_exercise, "build", "test-results", "test")
        xml_file = os.path.join(xml_report_dir, "TEST-AllergiesTest.xml")
        assert os.path.isfile(xml_file), f"Test XML report not found at {xml_file}"

        tree = ET.parse(xml_file)
        root = tree.getroot()

        tests_total = int(root.attrib.get("tests", 0))
        tests_skipped = int(root.attrib.get("skipped", 0))
        tests_failures = int(root.attrib.get("failures", 0))
        tests_errors = int(root.attrib.get("errors", 0))
        tests_passed = tests_total - tests_skipped - tests_failures - tests_errors

        print(f"  Executed Tests: {tests_total}")
        print(f"  Passed:   {tests_passed}")
        print(f"  Skipped:  {tests_skipped}")
        print(f"  Failures: {tests_failures}")
        print(f"  Errors:   {tests_errors}")

        assert tests_total > 0, "Test count must be greater than zero!"
        assert tests_failures == 0, f"Found {tests_failures} test failures!"
        assert tests_errors == 0, f"Found {tests_errors} test errors!"

        # Verify named cases
        named_results = {}
        for case in NAMED_CASES:
            method_name = case["method"]
            display_name = case["display_name"]
            # Look up testcase by display name or method name
            matching_elems = [
                tc for tc in root.findall("testcase")
                if tc.attrib.get("name") in (display_name, method_name, f"{method_name}()")
            ]
            assert matching_elems, f"Named case '{display_name}' ({method_name}) not found in XML results"
            elem = matching_elems[0]
            failure = elem.find("failure")
            skipped = elem.find("skipped")
            assert failure is None, f"Named case {display_name} ({method_name}()) failed!"
            assert skipped is None, f"Named case {display_name} ({method_name}()) was skipped!"
            print(f"  [NAMED CASE] '{display_name}' ({method_name}()) -> PASSED")
            named_results[method_name] = "PASSED"

        results["checks"]["test_execution"] = {
            "exit_code": proc.returncode,
            "tests_total": tests_total,
            "tests_passed": tests_passed,
            "tests_skipped": tests_skipped,
            "tests_failures": tests_failures,
            "tests_errors": tests_errors,
            "named_cases": named_results,
        }

    # Verify working tree was not rewritten
    with open(learner_solution, "r") as f:
        after_stub = f.read()
    assert after_stub == stub_content, "Working tree starter file was modified!"
    print("  Working tree integrity verified: untouched.")

    results["status"] = "PASSED"
    results_file = os.path.join(WORK_DIR, "results.json")
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nAll assertions passed! Saved evidence to {results_file}")
    sys.exit(0)


if __name__ == "__main__":
    main()
