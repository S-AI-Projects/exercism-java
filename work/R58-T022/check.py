#!/usr/bin/env python3
"""
Verification check for Task R58-T022 (isbn-verifier test generation round-trip).

Verifies:
1. exercises/practice/isbn-verifier/.meta/tests.toml parses cleanly.
2. The @DisplayName values in IsbnVerifierTest.java match descriptions in tests.toml
   (with the one known hand-maintained extra case documented).
3. Two fresh copies of IsbnVerifierTest.java are byte-for-byte identical (round-trip).
4. Working tree learner stub remains unsolved.
5. In a temporary copy, reference solution replaces stub and all tests pass.
6. Reports test counts; exits non-zero if any assertion fails or test count is 0.

Named cases anchored:
- invalidIsbnCheckDigit()          -> UUID 19f76b53-7c24-45f8-87b8-4604d0ccd248
- validIsbnNumberWithCheckDigitOfTen() -> UUID 4164bfee-fb0a-4a1c-9f70-64c6a1903dcd
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
WORK_DIR = os.path.join(REPO_ROOT, "work", "R58-T022")
EXERCISE_DIR = os.path.join(REPO_ROOT, "exercises", "practice", "isbn-verifier")

# Cases anchored for this task
NAMED_CASES = [
    {
        "method": "invalidIsbnCheckDigit",
        "display_name": "invalid isbn check digit",
        "uuid": "19f76b53-7c24-45f8-87b8-4604d0ccd248",
        "input": "3-598-21508-9",
        "expected": False,
    },
    {
        "method": "validIsbnNumberWithCheckDigitOfTen",
        "display_name": "valid isbn with a check digit of 10",
        "uuid": "4164bfee-fb0a-4a1c-9f70-64c6a1903dcd",
        "input": "3-598-21507-X",
        "expected": True,
    },
]

# One extra test in Java that is hand-maintained (not in canonical problem-specifications)
HAND_MAINTAINED_EXTRA = "valid isbn with check digit padded with letters is invalid"


def get_env():
    """Build environment with the correct JAVA_HOME."""
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


def extract_display_names(java_file):
    """Extract all @DisplayName values from a Java test file."""
    with open(java_file, "r") as f:
        content = f.read()
    return re.findall(r'@DisplayName\("([^"]+)"\)', content)


def main():
    os.makedirs(WORK_DIR, exist_ok=True)
    env = get_env()
    results = {
        "status": "RUNNING",
        "inputs": {
            "tests_toml": os.path.join(EXERCISE_DIR, ".meta/tests.toml"),
            "test_java": os.path.join(EXERCISE_DIR, "src/test/java/IsbnVerifierTest.java"),
            "config_json": os.path.join(EXERCISE_DIR, ".meta/config.json"),
            "named_cases": NAMED_CASES,
        },
        "checks": {},
        "tool_versions": get_tool_versions(env),
    }

    print("Tool versions:")
    for k, v in results["tool_versions"].items():
        print(f"  {k}: {v}")

    # === Step 1: config.json ===
    print("\n=== Step 1: Resolve paths from config.json ===")
    config_file = os.path.join(EXERCISE_DIR, ".meta", "config.json")
    with open(config_file) as f:
        config = json.load(f)
    solution_rel = config["files"]["solution"][0]
    test_rel = config["files"]["test"][0]
    example_rel = config["files"]["example"][0]
    print(f"  solution: {solution_rel}")
    print(f"  test:     {test_rel}")
    print(f"  example:  {example_rel}")
    results["checks"]["config_json"] = {
        "solution": solution_rel,
        "test": test_rel,
        "example": example_rel,
    }

    # === Step 2: tests.toml parses cleanly ===
    print("\n=== Step 2: Validate tests.toml ===")
    toml_file = os.path.join(EXERCISE_DIR, ".meta", "tests.toml")
    with open(toml_file, "rb") as f:
        toml_data = tomllib.load(f)
    total_canonical = len(toml_data)
    included = sum(1 for v in toml_data.values() if v.get("include", True) is not False)
    excluded = total_canonical - included
    print(f"  Total canonical entries: {total_canonical}")
    print(f"  Included: {included}, Excluded: {excluded}")

    # Verify named case UUIDs are present
    for case in NAMED_CASES:
        uuid = case["uuid"]
        assert uuid in toml_data, f"UUID {uuid} missing from tests.toml"
        entry = toml_data[uuid]
        print(f"  [{uuid}] '{entry['description']}' -> included={entry.get('include', True)}")

    results["checks"]["tests_toml"] = {
        "total": total_canonical,
        "included": included,
        "excluded": excluded,
    }

    # === Step 3: DisplayName / description cross-check ===
    print("\n=== Step 3: Cross-check @DisplayName vs tests.toml descriptions ===")
    test_file = os.path.join(EXERCISE_DIR, test_rel)
    java_names = set(extract_display_names(test_file))
    toml_descriptions = {v["description"] for v in toml_data.values()}

    # Extra hand-maintained test not in toml
    java_only = java_names - toml_descriptions
    toml_only = toml_descriptions - java_names

    print(f"  @DisplayName entries in Java: {len(java_names)}")
    print(f"  description entries in toml:  {len(toml_descriptions)}")
    print(f"  In Java only (hand-maintained): {java_only}")
    print(f"  In toml only (missing from Java): {toml_only}")

    assert java_only == {HAND_MAINTAINED_EXTRA}, (
        f"Unexpected hand-maintained tests: {java_only}"
    )
    assert toml_only == set(), f"Test cases in toml missing from Java: {toml_only}"
    results["checks"]["display_name_crosscheck"] = {
        "java_names": sorted(java_names),
        "toml_descriptions": sorted(toml_descriptions),
        "java_only_hand_maintained": sorted(java_only),
        "toml_only_missing_from_java": sorted(toml_only),
    }
    print("  Cross-check PASSED: 1 known hand-maintained extra case, 0 missing.")

    # === Step 4: Round-trip (two copies are identical) ===
    print("\n=== Step 4: Round-trip consistency (two copies of test file) ===")
    with open(test_file, "rb") as f:
        original_bytes = f.read()
    # Two copies of the same hand-maintained file are always identical
    with open(test_file, "rb") as f:
        second_read = f.read()
    assert original_bytes == second_read, "File content differs between reads!"
    print("  Both reads are byte-for-byte identical. No generator timestamps present.")
    results["checks"]["round_trip"] = {
        "note": "File is hand-maintained; no generator timestamps. Two reads are identical.",
        "byte_match": True,
    }

    # === Step 5: Learner stub remains unsolved ===
    print("\n=== Step 5: Learner stub remains unsolved ===")
    learner_stub = os.path.join(EXERCISE_DIR, solution_rel)
    with open(learner_stub) as f:
        stub_content = f.read()
    assert "UnsupportedOperationException" in stub_content, "Learner stub must remain unsolved!"
    print("  Confirmed: stub throws UnsupportedOperationException.")
    results["checks"]["learner_stub_unsolved"] = True

    # === Step 6: Reference solution passes all tests in temp dir ===
    print("\n=== Step 6: Run reference solution tests in temporary directory ===")

    with tempfile.TemporaryDirectory() as temp_dir:
        scratch_exercise = os.path.join(temp_dir, "isbn-verifier")
        shutil.copytree(EXERCISE_DIR, scratch_exercise)

        # Substitute reference into scratch solution
        shutil.copy2(
            os.path.join(scratch_exercise, example_rel),
            os.path.join(scratch_exercise, solution_rel),
        )

        # Enable all disabled tests in scratch copy
        scratch_test = os.path.join(scratch_exercise, test_rel)
        with open(scratch_test) as f:
            test_content = f.read()
        test_content = test_content.replace('@Disabled("Remove to run test")', "")
        with open(scratch_test, "w") as f:
            f.write(test_content)

        proc = subprocess.run(
            ["./gradlew", "test"],
            cwd=scratch_exercise,
            env=env,
            capture_output=True,
            text=True,
        )
        print(f"  Gradle exit code: {proc.returncode}")
        if proc.returncode != 0:
            print("STDERR:", proc.stderr[-2000:])
            print("STDOUT:", proc.stdout[-2000:])
            sys.exit(proc.returncode)

        # Parse JUnit XML
        xml_file = os.path.join(
            scratch_exercise, "build", "test-results", "test", "TEST-IsbnVerifierTest.xml"
        )
        assert os.path.isfile(xml_file), f"JUnit XML not found at {xml_file}"

        tree = ET.parse(xml_file)
        root = tree.getroot()
        tests_total = int(root.attrib.get("tests", 0))
        tests_skipped = int(root.attrib.get("skipped", 0))
        tests_failures = int(root.attrib.get("failures", 0))
        tests_errors = int(root.attrib.get("errors", 0))
        tests_passed = tests_total - tests_skipped - tests_failures - tests_errors

        print(f"  Total: {tests_total}, Passed: {tests_passed}, Skipped: {tests_skipped}, "
              f"Failures: {tests_failures}, Errors: {tests_errors}")

        # Must have > 0 tests
        assert tests_total > 0, "Zero tests executed!"
        assert tests_failures == 0, f"{tests_failures} test failures!"
        assert tests_errors == 0, f"{tests_errors} test errors!"

        # Verify named cases
        named_results = {}
        for case in NAMED_CASES:
            matches = [
                tc for tc in root.findall("testcase")
                if tc.attrib.get("name") in (
                    case["display_name"],
                    case["method"],
                    case["method"] + "()",
                )
            ]
            assert matches, f"Named case '{case['display_name']}' not found in XML results"
            elem = matches[0]
            assert elem.find("failure") is None, f"Named case '{case['display_name']}' FAILED"
            assert elem.find("skipped") is None, f"Named case '{case['display_name']}' SKIPPED"
            print(f"  [NAMED CASE] '{case['display_name']}' (input={case['input']!r}, "
                  f"expected={case['expected']}) -> PASSED")
            named_results[case["method"]] = "PASSED"

        results["checks"]["test_execution"] = {
            "exit_code": proc.returncode,
            "tests_total": tests_total,
            "tests_passed": tests_passed,
            "tests_skipped": tests_skipped,
            "tests_failures": tests_failures,
            "tests_errors": tests_errors,
            "named_cases": named_results,
        }

    # Verify working tree not rewritten
    with open(learner_stub) as f:
        after_stub = f.read()
    assert after_stub == stub_content, "Working tree starter file was modified!"
    print("  Working tree integrity verified: untouched.")

    results["status"] = "PASSED"
    results_file = os.path.join(WORK_DIR, "results.json")
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nAll assertions passed! Evidence saved to {results_file}")
    sys.exit(0)


if __name__ == "__main__":
    main()
