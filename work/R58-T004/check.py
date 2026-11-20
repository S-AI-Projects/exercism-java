#!/usr/bin/env python3
"""
Verification check for Task R58-T004 (Yacht reference readability refactoring).

Verifies:
1. exercises/practice/yacht/.meta/config.json paths resolve correctly.
2. exercises/practice/yacht/.meta/tests.toml parses cleanly and all 29 canonical cases are registered.
3. Learner starter stub (src/main/java/Yacht.java) remains unsolved and untouched.
4. Refactored reference implementation in .meta/src/reference/java/Yacht.java:
   - Eliminates ambiguous local state ('Collection<Long> occurrences' -> 'Collection<Long> dieFaceCounts').
   - Contains extracted 'dieFrequencies()' calculation.
   - Clarifies lambda parameter ('x' -> 'entry').
   - Includes exercise-specific invariant comments.
   - Preserves public API contract, constructor, and exact return types.
5. In isolated temporary directories, executes `./gradlew test` against:
   - Original snapshot (before)
   - Refactored reference (after)
   Ensuring all 29 tests pass with 0 failures, 0 errors, 0 skipped, and before/after agreement.
6. Reports test counts; fails if test count is 0, exit code is non-zero, or any assertion fails.
7. Verifies working tree integrity is preserved.
8. Saves results and tool versions to work/R58-T004/results.json and latest-result.json.
"""

import hashlib
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

try:
    import tomllib
except ModuleNotFoundError:
    tomllib = None

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
WORK_DIR = os.path.join(REPO_ROOT, "work", "R58-T004")
EXERCISE_DIR = os.path.join(REPO_ROOT, "exercises", "practice", "yacht")
ORIGINAL_REF = os.path.join(WORK_DIR, "original", "Yacht.java")

NAMED_CASES = [
    {
        "method": "yacht",
        "display_name": "Yacht",
        "uuid": "3060e4a5-4063-4deb-a380-a630b43a84b6",
        "category": "YACHT",
        "dice": [5, 5, 5, 5, 5],
        "expected_score": 50,
    },
    {
        "method": "notYacht",
        "display_name": "Not Yacht",
        "uuid": "15026df2-f567-482f-b4d5-5297d57769d9",
        "category": "YACHT",
        "dice": [1, 3, 3, 2, 5],
        "expected_score": 0,
    },
    {
        "method": "yachtCountedAsThrees",
        "display_name": "Yacht counted as threes",
        "uuid": "f6125417-5c8a-4bca-bc5b-b4b76d0d28c8",
        "category": "THREES",
        "dice": [3, 3, 3, 3, 3],
        "expected_score": 15,
    },
    {
        "method": "fullHouseTwoSmallThreeBig",
        "display_name": "Full house two small, three big",
        "uuid": "51cb26db-6b24-49af-a9ff-12f53b252eea",
        "category": "FULL_HOUSE",
        "dice": [2, 2, 4, 4, 4],
        "expected_score": 16,
    },
    {
        "method": "fourOfAKind",
        "display_name": "Four of a Kind",
        "uuid": "b286084d-0568-4460-844a-ba79d71d79c6",
        "category": "FOUR_OF_A_KIND",
        "dice": [6, 6, 4, 6, 6],
        "expected_score": 24,
    },
    {
        "method": "yachtIsNotAFullHouse",
        "display_name": "Yacht is not a full house",
        "uuid": "32a3f4ee-9142-4edf-ba70-6c0f96eb4b0c",
        "category": "FULL_HOUSE",
        "dice": [2, 2, 2, 2, 2],
        "expected_score": 0,
    },
    {
        "method": "yachtCanBeScoredAsFourOfAKind",
        "display_name": "Yacht can be scored as Four of a Kind",
        "uuid": "f25c0c90-5397-4732-9779-b1e9b5f612ca",
        "category": "FOUR_OF_A_KIND",
        "dice": [3, 3, 3, 3, 3],
        "expected_score": 12,
    },
    {
        "method": "yachtAsChoice",
        "display_name": "Yacht as choice",
        "uuid": "b524c0cf-32d2-4b40-8fb3-be3500f3f135",
        "category": "CHOICE",
        "dice": [2, 2, 2, 2, 2],
        "expected_score": 10,
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
    versions = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
    }
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


def run_gradle_test_in_temp(exercise_dir, ref_source_file, solution_rel, test_rel, env):
    with tempfile.TemporaryDirectory(prefix="r58-t004-") as temp_dir:
        scratch_exercise = os.path.join(temp_dir, "yacht")
        shutil.copytree(exercise_dir, scratch_exercise)

        # Substitute reference into solution path
        shutil.copy2(
            ref_source_file,
            os.path.join(scratch_exercise, solution_rel),
        )

        # Enable all tests in scratch copy
        scratch_test = os.path.join(scratch_exercise, test_rel)
        with open(scratch_test, "r") as f:
            test_content = f.read()
        test_content_enabled = re.sub(
            r'^\s*@Disabled\("Remove to run test"\)\s*\n', "", test_content, flags=re.MULTILINE
        )
        with open(scratch_test, "w") as f:
            f.write(test_content_enabled)

        proc = subprocess.run(
            ["./gradlew", "test", "--no-daemon"],
            cwd=scratch_exercise,
            env=env,
            capture_output=True,
            text=True,
        )

        xml_file = os.path.join(
            scratch_exercise, "build", "test-results", "test", "TEST-YachtTest.xml"
        )
        if not os.path.isfile(xml_file):
            print(f"ERROR: XML report not found at {xml_file}")
            print("STDOUT:\n", proc.stdout)
            print("STDERR:\n", proc.stderr)
            raise RuntimeError(f"Gradle execution failed with return code {proc.returncode}")

        tree = ET.parse(xml_file)
        root = tree.getroot()

        tests_total = int(root.attrib.get("tests", 0))
        tests_skipped = int(root.attrib.get("skipped", 0))
        tests_failures = int(root.attrib.get("failures", 0))
        tests_errors = int(root.attrib.get("errors", 0))
        tests_passed = tests_total - tests_skipped - tests_failures - tests_errors

        case_results = {}
        for tc in root.findall("testcase"):
            tc_name = tc.attrib.get("name")
            failure = tc.find("failure")
            skipped = tc.find("skipped")
            error = tc.find("error")
            status = "PASSED"
            if failure is not None:
                status = "FAILED"
            elif error is not None:
                status = "ERROR"
            elif skipped is not None:
                status = "SKIPPED"
            case_results[tc_name] = status

        return {
            "exit_code": proc.returncode,
            "tests_total": tests_total,
            "tests_passed": tests_passed,
            "tests_skipped": tests_skipped,
            "tests_failures": tests_failures,
            "tests_errors": tests_errors,
            "case_results": case_results,
            "root_elem": root,
        }


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
            entries[current_uuid][k] = v
    return entries


def main():
    os.makedirs(WORK_DIR, exist_ok=True)
    env = get_env()
    tool_versions = get_tool_versions(env)

    print("=== Step 1: Resolving paths from config.json ===")
    config_file = os.path.join(EXERCISE_DIR, ".meta", "config.json")
    assert os.path.isfile(config_file), f"config.json not found: {config_file}"
    with open(config_file, "r") as f:
        config = json.load(f)

    solution_rel = config["files"]["solution"][0]
    test_rel = config["files"]["test"][0]
    example_rel = config["files"]["example"][0]
    print(f"  solution: {solution_rel}")
    print(f"  test:     {test_rel}")
    print(f"  example:  {example_rel}")

    assert os.path.isfile(os.path.join(EXERCISE_DIR, solution_rel))
    assert os.path.isfile(os.path.join(EXERCISE_DIR, test_rel))
    assert os.path.isfile(os.path.join(EXERCISE_DIR, example_rel))
    assert os.path.isfile(ORIGINAL_REF), f"Original reference snapshot missing at {ORIGINAL_REF}"

    print("\n=== Step 2: Validating tests.toml ===")
    tests_toml_file = os.path.join(EXERCISE_DIR, ".meta", "tests.toml")
    toml_data = parse_tests_toml(tests_toml_file)

    total_canonical = len(toml_data)
    included = sum(1 for v in toml_data.values() if v.get("include", True) is not False)
    excluded = total_canonical - included
    print(f"  Total canonical entries: {total_canonical}")
    print(f"  Included: {included}, Excluded: {excluded}")
    assert total_canonical == 29, f"Expected 29 tests in tests.toml, found {total_canonical}"

    for case in NAMED_CASES:
        uuid = case["uuid"]
        assert uuid in toml_data, f"Named case UUID {uuid} missing from tests.toml"
        assert toml_data[uuid]["description"] == case["display_name"], (
            f"Description mismatch for {uuid}: {toml_data[uuid]['description']} != {case['display_name']}"
        )
        print(f"  [{uuid}] '{case['display_name']}' verified in tests.toml")

    print("\n=== Step 3: Verifying learner starter stub remains unsolved ===")
    learner_stub_path = os.path.join(EXERCISE_DIR, solution_rel)
    with open(learner_stub_path, "rb") as f:
        stub_bytes = f.read()
    stub_hash_before = hashlib.sha256(stub_bytes).hexdigest()
    stub_text = stub_bytes.decode()

    assert "UnsupportedOperationException" in stub_text, "Learner stub must throw UnsupportedOperationException"
    assert "Delete this statement and write your own implementation." in stub_text, (
        "Learner stub missing default placeholder message"
    )
    print("  Learner starter stub verified: clean, unsolved, intact.")

    print("\n=== Step 4: Validating refactored reference implementation ===")
    ref_path = os.path.join(EXERCISE_DIR, example_rel)
    with open(ref_path, "r") as f:
        ref_code = f.read()

    # Readability assertions
    assert "Collection<Long> occurrences" not in ref_code, (
        "Ambiguous identifier 'occurrences' must be refactored"
    )
    assert "Collection<Long> dieFaceCounts" in ref_code, (
        "Refactored reference must name local state 'dieFaceCounts'"
    )
    assert "dieFrequencies()" in ref_code, (
        "Refactored reference must extract coherent calculation 'dieFrequencies()'"
    )
    assert "filter(entry -> entry.getValue() >= 4)" in ref_code, (
        "Refactored FOUR_OF_A_KIND must use clear lambda variable 'entry'"
    )
    assert "Exercise invariant:" in ref_code, (
        "Exercise invariant comment must be present"
    )

    # API and contract assertions
    assert "Yacht(int[] dice, YachtCategory yachtCategory)" in ref_code, (
        "Public constructor signature must be preserved"
    )
    assert "int score()" in ref_code, (
        "Public method score() must be preserved"
    )
    assert "default: return 0;" in ref_code, (
        "Default switch fallback must be preserved"
    )
    print("  Reference implementation readability improvements confirmed:")
    print("    - Ambiguous local state 'occurrences' replaced by 'dieFaceCounts'")
    print("    - Coherent calculation 'dieFrequencies()' extracted")
    print("    - Lambda parameter 'x' clarified to 'entry'")
    print("    - Invariant comments documented")
    print("    - Public API and contract preserved")

    print("\n=== Step 5: Running tests against original snapshot (Before) ===")
    before_result = run_gradle_test_in_temp(
        EXERCISE_DIR, ORIGINAL_REF, solution_rel, test_rel, env
    )
    print(f"  Before exit code: {before_result['exit_code']}")
    print(f"  Before executed tests: {before_result['tests_total']}")
    print(f"  Before passed: {before_result['tests_passed']}")
    assert before_result["exit_code"] == 0, "Original snapshot must pass all tests"
    assert before_result["tests_total"] == 29, f"Expected 29 tests, got {before_result['tests_total']}"
    assert before_result["tests_failures"] == 0, f"Expected 0 failures, got {before_result['tests_failures']}"
    assert before_result["tests_errors"] == 0, f"Expected 0 errors, got {before_result['tests_errors']}"

    print("\n=== Step 6: Running tests against refactored reference (After) ===")
    after_result = run_gradle_test_in_temp(
        EXERCISE_DIR, ref_path, solution_rel, test_rel, env
    )
    print(f"  After exit code: {after_result['exit_code']}")
    print(f"  After executed tests: {after_result['tests_total']}")
    print(f"  After passed: {after_result['tests_passed']}")
    assert after_result["exit_code"] == 0, "Refactored reference must pass all tests"
    assert after_result["tests_total"] == 29, f"Expected 29 tests, got {after_result['tests_total']}"
    assert after_result["tests_failures"] == 0, f"Expected 0 failures, got {after_result['tests_failures']}"
    assert after_result["tests_errors"] == 0, f"Expected 0 errors, got {after_result['tests_errors']}"
    assert after_result["tests_skipped"] == 0, f"Expected 0 skipped, got {after_result['tests_skipped']}"

    print("\n=== Step 7: Verifying before/after parity across all 29 cases ===")
    assert before_result["tests_total"] == after_result["tests_total"], (
        f"Test count mismatch: before={before_result['tests_total']} != after={after_result['tests_total']}"
    )
    for name, status in after_result["case_results"].items():
        assert status == "PASSED", f"Test '{name}' did not pass in after run!"
        assert before_result["case_results"].get(name) == "PASSED", (
            f"Test '{name}' status differed between before and after runs"
        )
    print("  Before and after outputs agree on all 29 cases.")

    print("\n=== Step 8: Verifying named baseline cases in test execution ===")
    named_case_evidence = {}
    for case in NAMED_CASES:
        display_name = case["display_name"]
        method_name = case["method"]
        assert after_result["case_results"].get(display_name) == "PASSED", (
            f"Named case '{display_name}' was not executed or did not pass"
        )
        print(f"  [NAMED CASE] '{display_name}' ({method_name}()) -> PASSED (Expected: {case['expected_score']})")
        named_case_evidence[method_name] = {
            "display_name": display_name,
            "uuid": case["uuid"],
            "category": case["category"],
            "dice": case["dice"],
            "expected_score": case["expected_score"],
            "status": "PASSED",
        }

    print("\n=== Step 9: Verifying working tree integrity ===")
    with open(learner_stub_path, "rb") as f:
        stub_bytes_after = f.read()
    stub_hash_after = hashlib.sha256(stub_bytes_after).hexdigest()
    assert stub_hash_before == stub_hash_after, "Working tree learner stub was modified!"
    print("  Working tree integrity verified: unchanged.")

    results_data = {
        "task": "R58-T004",
        "exercise": "yacht",
        "timestamp_unix": int(time.time()),
        "status": "PASSED",
        "tool_versions": tool_versions,
        "readability_improvements": {
            "ambiguous_local_state_renamed": {
                "before": "Collection<Long> occurrences",
                "after": "Collection<Long> dieFaceCounts",
                "purpose": "Distinguishes frequency count values from observed face values",
            },
            "extracted_coherent_calculation": {
                "method": "private Map<Integer, Long> dieFrequencies()",
                "purpose": "Encapsulates duplicated stream frequency grouping used in FULL_HOUSE and FOUR_OF_A_KIND",
            },
            "lambda_variable_clarified": {
                "before": "x -> x.getValue() >= 4",
                "after": "entry -> entry.getValue() >= 4",
            },
            "invariants_documented": [
                "5 dice rolled with faces 1..6 inclusively",
                "Full House invariant: exactly 3 of one face and 2 of another face",
                "Four of a Kind invariant: at least 4 dice of same face, scoring 4 times that face",
            ],
            "api_preserved": [
                "Yacht(int[] dice, YachtCategory yachtCategory)",
                "int score()",
            ],
        },
        "tests": {
            "total_canonical": total_canonical,
            "executed": after_result["tests_total"],
            "passed": after_result["tests_passed"],
            "failures": after_result["tests_failures"],
            "errors": after_result["tests_errors"],
            "skipped": after_result["tests_skipped"],
            "before_after_agreement": True,
        },
        "named_cases": named_case_evidence,
        "working_tree_learner_stub_unmodified": True,
    }

    results_file = os.path.join(WORK_DIR, "results.json")
    latest_file = os.path.join(WORK_DIR, "latest-result.json")

    with open(results_file, "w") as f:
        json.dump(results_data, f, indent=2)
    with open(latest_file, "w") as f:
        json.dump(results_data, f, indent=2)

    print(f"\nAll checks passed successfully!")
    print(f"Results recorded in:\n  - {results_file}\n  - {latest_file}")
    sys.exit(0)


if __name__ == "__main__":
    main()
