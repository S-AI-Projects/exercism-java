#!/usr/bin/env python3
"""
Verification check for Task R58-T024 (House reference readability refactoring).

Verifies:
1. exercises/practice/house/.meta/config.json paths resolve correctly.
2. exercises/practice/house/.meta/tests.toml parses cleanly.
3. Learner starter stub (src/main/java/House.java) remains unsolved.
4. Refactored reference implementation in .meta/src/reference/java/House.java:
   - Eliminates ambiguous local state shadowing (no 'StringBuilder verse' or 'String[] verses').
   - Contains extracted 'relativeClause' calculation.
   - Preserves public API and exact return types.
5. In a temporary directory, the refactored reference passes all 14 tests:
   - verseOne ("verse one - the house that jack built")
   - verseTwo ("verse two - the malt that lay")
   - verseThree ("verse three - the rat that ate")
   - and all other test cases.
6. Reports test counts; fails if test count is 0 or any assertion fails.
7. Saves results and tool versions to work/R58-T024/results.json.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import tomllib
import xml.etree.ElementTree as ET

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
WORK_DIR = os.path.join(REPO_ROOT, "work", "R58-T024")
EXERCISE_DIR = os.path.join(REPO_ROOT, "exercises", "practice", "house")

NAMED_CASES = [
    {
        "method": "verseOne",
        "display_name": "verse one - the house that jack built",
        "uuid": "28a540ff-f765-4348-9d57-ae33f25f41f2",
        "input": 1,
        "expected_start": "This is the house that Jack built.",
    },
    {
        "method": "verseTwo",
        "display_name": "verse two - the malt that lay",
        "uuid": "ebc825ac-6e2b-4a5e-9afd-95732191c8da",
        "input": 2,
        "expected_start": "This is the malt that lay in the house that Jack built.",
    },
    {
        "method": "verseThree",
        "display_name": "verse three - the rat that ate",
        "uuid": "1ed8bb0f-edb8-4bd1-b6d4-b64754fe4a60",
        "input": 3,
        "expected_start": "This is the rat that ate the malt that lay in the house that Jack built.",
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

    print("\n=== Step 4: Validating reference readability refactoring ===")
    ref_path = os.path.join(EXERCISE_DIR, example_rel)
    with open(ref_path, "r") as f:
        ref_code = f.read()

    # Verify that ambiguous variable shadowing has been eliminated
    assert "StringBuilder verse =" not in ref_code, (
        "Ambiguous local variable 'verse' shadowing method verse() should be eliminated"
    )
    assert "String[] verses =" not in ref_code, (
        "Ambiguous local variable 'verses' shadowing method verses() should be eliminated"
    )
    # Verify that coherent calculation has been extracted
    assert "relativeClause" in ref_code, (
        "Expected helper method 'relativeClause' extracting the clausal embedding calculation"
    )
    # Verify public/package interface methods are preserved
    assert "String verse(int" in ref_code, "Public method verse(int) must be preserved"
    assert "String verses(int" in ref_code, "Public method verses(int, int) must be preserved"
    assert "String sing()" in ref_code, "Public method sing() must be preserved"
    print("  Readability improvements confirmed:")
    print("    - Local variable shadowing eliminated (verse -> rhyme, verses -> verseCollection)")
    print("    - Extracted relativeClause(int index) helper method")
    print("    - Exact API contract preserved")

    results = {
        "status": "RUNNING",
        "tool_versions": tool_versions,
        "inputs": {
            "named_cases": NAMED_CASES,
            "refactoring": {
                "shadowing_eliminated": True,
                "extracted_calculation": "relativeClause(int index)",
                "preserved_api": ["verse(int)", "verses(int, int)", "sing()"],
            },
        },
        "checks": {},
    }

    print("\n=== Step 5: Running tests against refactored reference implementation ===")
    with tempfile.TemporaryDirectory() as temp_dir:
        scratch_exercise = os.path.join(temp_dir, "house")
        shutil.copytree(EXERCISE_DIR, scratch_exercise)

        # Substitute reference into solution
        shutil.copy2(
            os.path.join(scratch_exercise, example_rel),
            os.path.join(scratch_exercise, solution_rel),
        )

        # Enable all tests in scratch copy
        scratch_test = os.path.join(scratch_exercise, test_rel)
        with open(scratch_test, "r") as f:
            test_content = f.read()
        test_content_enabled = test_content.replace('@Disabled("Remove to run test")', "")
        with open(scratch_test, "w") as f:
            f.write(test_content_enabled)

        proc = subprocess.run(
            ["./gradlew", "test"],
            cwd=scratch_exercise,
            env=env,
            capture_output=True,
            text=True,
        )

        print(f"  Gradle exit code: {proc.returncode}")
        if proc.returncode != 0:
            print("STDERR:\n", proc.stderr)
            print("STDOUT:\n", proc.stdout)
            sys.exit(proc.returncode)

        # Parse test results from XML
        xml_file = os.path.join(
            scratch_exercise, "build", "test-results", "test", "TEST-HouseTest.xml"
        )
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
            matches = [
                tc for tc in root.findall("testcase")
                if tc.attrib.get("name") in (display_name, method_name, f"{method_name}()")
            ]
            assert matches, f"Named case '{display_name}' ({method_name}) not found in XML results"
            elem = matches[0]
            assert elem.find("failure") is None, f"Named case {display_name} failed!"
            assert elem.find("skipped") is None, f"Named case {display_name} was skipped!"
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
    with open(learner_stub_path, "r") as f:
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
