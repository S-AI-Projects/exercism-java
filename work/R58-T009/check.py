#!/usr/bin/env python3
"""
Verification check for Task R58-T009 (parallel-letter-frequency isolated reference runner).

Verifies:
1. Dynamically resolves solution, test, and example paths from
   exercises/practice/parallel-letter-frequency/.meta/config.json.
2. Ensures all declared paths are relative, do not escape the exercise root, and exist.
3. Tests deliberate negative metadata fixtures:
   - missing-reference
   - missing-test
   - outside-exercise traversal
   Asserting each is rejected for the intended reason.
4. Confirms working-tree learner starter stub remains unsolved (UnsupportedOperationException)
   and ensures the working tree is never modified (SHA-256 integrity verification before/after every run).
5. Cross-checks tests.toml canonical metadata against src/test/java/ParallelLetterFrequencyTest.java
   (all 13 canonical cases and @DisplayName annotations).
6. Tests the isolated runner under three distinct scenarios:
   - Scenario A: Maintained reference in temporary copy with all tests enabled -> passes all 13 tests.
     Anchor case 'large texts' (containing "it's the result of forty years underground! Allow me to indulge my fancy.")
     and all 13 @DisplayName cases pass with 0 failures, 0 errors, 0 skipped.
   - Scenario B: Deliberately failing reference mutant -> produces assertion failures (failures > 0)
     and non-zero child exit; runner rejects it.
   - Scenario C: Empty test selection (--tests NoSuchParallelLetterFrequencyTestClass) -> executes 0 tests
     and non-zero child exit; runner rejects it.
7. Asserts temporary directories are cleanly removed after each execution.
8. Verifies learner files before/after every run and in a finally block to ensure zero modification.
9. Saves inputs, expected vs actual outputs, tool versions, and check evidence to
   work/R58-T009/results.json and work/R58-T009/latest-result.json.
"""

from __future__ import annotations

import copy
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
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    tomllib = None

REPO_ROOT = Path(__file__).resolve().parents[2]
EXERCISE_DIR = REPO_ROOT / "exercises" / "practice" / "parallel-letter-frequency"
WORK_DIR = REPO_ROOT / "work" / "R58-T009"
CONFIG_FILE = EXERCISE_DIR / ".meta" / "config.json"
TESTS_TOML_FILE = EXERCISE_DIR / ".meta" / "tests.toml"
MAINTENANCE_DOC = REPO_ROOT / "docs" / "maintenance" / "parallel-letter-frequency.md"

# Canonical test cases from tests.toml and ParallelLetterFrequencyTest.java
CANONICAL_CASES = [
    {"method": "testNoTexts", "display_name": "no texts", "uuid": "c054d642-c1fa-4234-8007-9339f2337886"},
    {"method": "testOneTextWithOneLetter", "display_name": "one text with one letter", "uuid": "818031be-49dc-4675-b2f9-c4047f638a2a"},
    {"method": "testOneTextWithMultipleLetters", "display_name": "one text with multiple letters", "uuid": "c0b81d1b-940d-4cea-9f49-8445c69c17ae"},
    {"method": "testTwoTextsWithOneLetter", "display_name": "two texts with one letter", "uuid": "708ff1e0-f14a-43fd-adb5-e76750dcf108"},
    {"method": "testTwoTextsWithMultipleLetters", "display_name": "two texts with multiple letters", "uuid": "1b5c28bb-4619-4c9d-8db9-a4bb9c3bdca0"},
    {"method": "testIgnoreLetterCasing", "display_name": "ignore letter casing", "uuid": "6366e2b8-b84c-4334-a047-03a00a656d63"},
    {"method": "testIgnoreWhitespace", "display_name": "ignore whitespace", "uuid": "92ebcbb0-9181-4421-a784-f6f5aa79f75b"},
    {"method": "testIgnorePunctuation", "display_name": "ignore punctuation", "uuid": "bc5f4203-00ce-4acc-a5fa-f7b865376fd9"},
    {"method": "testIgnoreNumbers", "display_name": "ignore numbers", "uuid": "68032b8b-346b-4389-a380-e397618f6831"},
    {"method": "testUnicodeLetters", "display_name": "Unicode letters", "uuid": "aa9f97ac-3961-4af1-88e7-6efed1bfddfd"},
    {"method": "testCombinationOfLowerAndUppercaseLettersPunctuationAndWhiteSpace", "display_name": "combination of lower- and uppercase letters, punctuation and white space", "uuid": "7b1da046-701b-41fc-813e-dcfb5ee51813"},
    {"method": "testLargeTexts", "display_name": "large texts", "uuid": "4727f020-df62-4dcf-99b2-a6e58319cb4f"},
    {"method": "testManySmallTexts", "display_name": "many small texts", "uuid": "adf8e57b-8e54-4483-b6b8-8b32c115884c"},
]

ANCHOR_TEXT_SUBSTRING = "s the result of forty years underground! Allow me to indulge my fancy."


def get_env() -> dict[str, str]:
    env = os.environ.copy()
    candidate_jdks = [
        "/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home",
        "/opt/homebrew/Cellar/openjdk@21/21.0.13.0.3/libexec/openjdk.jdk/Contents/Home",
        "/Library/Java/JavaVirtualMachines/openjdk-21.jdk/Contents/Home",
    ]
    for jdk in candidate_jdks:
        if os.path.isdir(jdk):
            env["JAVA_HOME"] = jdk
            env["PATH"] = f"{jdk}/bin:{env.get('PATH', '')}"
            break
    return env


def get_tool_versions(env: dict[str, str]) -> dict[str, str]:
    versions = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
    }
    try:
        proc = subprocess.run(
            ["java", "-version"],
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        output = proc.stderr or proc.stdout
        versions["java"] = output.splitlines()[0].strip() if output else "unknown"
    except Exception as e:
        versions["java"] = f"error: {e}"

    try:
        proc = subprocess.run(
            ["./gradlew", "--version"],
            cwd=str(EXERCISE_DIR),
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        for line in proc.stdout.splitlines():
            if line.startswith("Gradle "):
                versions["gradle"] = line.strip()
                break
        else:
            versions["gradle"] = "Gradle unknown"
    except Exception as e:
        versions["gradle"] = f"error: {e}"

    return versions


def validate_files(config: dict, exercise_root: Path) -> list[str]:
    root = Path(exercise_root).resolve()
    errors = []
    files = config.get("files")
    if not isinstance(files, dict):
        return ["files must be an object"]
    for role, entries in files.items():
        if not isinstance(entries, list):
            errors.append(f"{role}: expected a list")
            continue
        for entry in entries:
            if not isinstance(entry, str) or not entry:
                errors.append(f"{role}: path must be a non-empty string")
                continue
            relative = Path(entry)
            if relative.is_absolute() or ".." in relative.parts:
                errors.append(f"{role}: path escapes exercise: {entry}")
                continue
            candidate = (root / relative).resolve()
            try:
                candidate.relative_to(root)
            except ValueError:
                errors.append(f"{role}: path escapes exercise: {entry}")
                continue
            if not candidate.is_file():
                errors.append(f"{role}: missing file: {entry}")
    return errors


def expect_rejected(label: str, fixture: dict, root: Path, expected_fragment: str) -> str:
    errors = validate_files(fixture, root)
    if not any(expected_fragment in error for error in errors):
        raise AssertionError(f"{label} fixture was not rejected for {expected_fragment!r}: {errors}")
    msg = errors[0]
    print(f"  ✓ [FIXTURE] {label} rejected as expected: {msg}")
    return msg


def parse_tests_toml(toml_path: Path) -> dict[str, dict[str, str]]:
    if tomllib is not None:
        with open(toml_path, "rb") as f:
            return tomllib.load(f)
    content = toml_path.read_text(encoding="utf-8")
    entries: dict[str, dict[str, str]] = {}
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
            key, val = line.split("=", 1)
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            entries[current_uuid][key] = val
    return entries


def hash_files(paths: list[Path]) -> dict[str, str]:
    hashes = {}
    for path in paths:
        if path.is_file():
            hashes[str(path.relative_to(REPO_ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def assert_learner_unchanged(target_files: list[Path], initial_hashes: dict[str, str], stage: str) -> None:
    current_hashes = hash_files(target_files)
    if current_hashes != initial_hashes:
        raise AssertionError(f"Learner starter files were modified during stage: {stage}!\n"
                             f"Initial: {initial_hashes}\nCurrent: {current_hashes}")


def copy_exercise_with_reference(base_dir: Path, config: dict, mutant_patch: str | None = None) -> Path:
    scratch = base_dir / "parallel-letter-frequency"
    shutil.copytree(EXERCISE_DIR, scratch, ignore=shutil.ignore_patterns(".gradle", "build"))

    solution_rel = config["files"]["solution"][0]
    test_rel = config["files"]["test"][0]
    example_rels = config["files"]["example"]

    dest_solution = scratch / solution_rel
    dest_dir = dest_solution.parent
    dest_dir.mkdir(parents=True, exist_ok=True)

    for ref_rel in example_rels:
        ref_file = scratch / ref_rel
        assert ref_file.is_file(), f"Reference file {ref_rel} missing from scratch copy"
        shutil.copy2(ref_file, dest_dir / ref_file.name)

    # If mutant patch specified, apply it to the scratch solution
    if mutant_patch is not None:
        sol_file = scratch / solution_rel
        content = sol_file.read_text(encoding="utf-8")
        if mutant_patch == "empty_map":
            # Mutate countLetters() to return empty map
            target = "return this.letters"
            replacement = "return java.util.Collections.emptyMap(); // mutant\n        /*"
            end_target = ".buildMap();"
            end_replacement = ".buildMap(); */"
            assert target in content and end_target in content, "Failed to apply empty_map mutant patch"
            content = content.replace(target, replacement).replace(end_target, end_replacement)
            sol_file.write_text(content, encoding="utf-8")
        else:
            raise ValueError(f"Unknown mutant patch: {mutant_patch}")

    # Enable all tests by stripping @Disabled in scratch copy
    scratch_test = scratch / test_rel
    tc = scratch_test.read_text(encoding="utf-8")
    tc = re.sub(r'^\s*@Disabled\("Remove to run test"\)\s*\n', "", tc, flags=re.MULTILINE)
    scratch_test.write_text(tc, encoding="utf-8")

    return scratch


def run_gradle_test(scratch: Path, env: dict[str, str], extra_args: list[str] | None = None) -> subprocess.CompletedProcess:
    cmd = ["./gradlew", "test", "--no-daemon"]
    if extra_args:
        cmd.extend(extra_args)
    return subprocess.run(
        cmd,
        cwd=str(scratch),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def parse_xml_results(scratch: Path) -> dict:
    report_dir = scratch / "build" / "test-results" / "test"
    xml_files = list(report_dir.glob("TEST-*.xml"))
    summary = {
        "total": 0,
        "passed": 0,
        "failures": 0,
        "errors": 0,
        "skipped": 0,
        "executed": 0,
        "case_results": {},
        "failed_case_details": {},
    }

    for xml_path in xml_files:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        tests = int(root.attrib.get("tests", 0))
        failures = int(root.attrib.get("failures", 0))
        errors = int(root.attrib.get("errors", 0))
        skipped = int(root.attrib.get("skipped", 0))

        summary["total"] += tests
        summary["failures"] += failures
        summary["errors"] += errors
        summary["skipped"] += skipped

        for case in root.findall("testcase"):
            name = case.attrib.get("name", "")
            fail_elem = case.find("failure")
            err_elem = case.find("error")
            skip_elem = case.find("skipped")

            if fail_elem is not None:
                summary["case_results"][name] = "FAILED"
                summary["failed_case_details"][name] = fail_elem.attrib.get("message", "").strip()
            elif err_elem is not None:
                summary["case_results"][name] = "ERROR"
                summary["failed_case_details"][name] = err_elem.attrib.get("message", "").strip()
            elif skip_elem is not None:
                summary["case_results"][name] = "SKIPPED"
            else:
                summary["case_results"][name] = "PASSED"

    summary["executed"] = summary["total"] - summary["skipped"]
    summary["passed"] = summary["executed"] - summary["failures"] - summary["errors"]
    return summary


def verify_maintenance_doc() -> None:
    assert MAINTENANCE_DOC.is_file(), f"Maintenance document missing at {MAINTENANCE_DOC}"
    doc_text = MAINTENANCE_DOC.read_text(encoding="utf-8")
    assert "src/main/java/ParallelLetterFrequency.java" in doc_text, "doc must mention real starter stub path"
    assert "src/test/java/ParallelLetterFrequencyTest.java" in doc_text, "doc must mention real test suite path"
    assert ".meta/src/reference/java/ParallelLetterFrequency.java" in doc_text, "doc must mention real reference path"
    assert "build/" in doc_text, "doc must distinguish build/ generated artifacts"
    assert ".meta/tests.toml" in doc_text, "doc must discuss tests.toml canonical metadata"


def main() -> int:
    print("==================================================")
    print("Task R58-T009 Verification Check: parallel-letter-frequency")
    print("==================================================")

    # 1. Metadata and config check
    assert CONFIG_FILE.is_file(), f"Missing config.json at {CONFIG_FILE}"
    assert TESTS_TOML_FILE.is_file(), f"Missing tests.toml at {TESTS_TOML_FILE}"

    with open(CONFIG_FILE, encoding="utf-8") as f:
        config = json.load(f)

    # Validate real configuration
    print("\n[Step 1] Validating real config.json file mappings...")
    real_errors = validate_files(config, EXERCISE_DIR)
    assert not real_errors, f"Real metadata failed validation: {real_errors}"
    print("  ✓ Real config.json passes: all files resolve cleanly inside exercise.")

    # Validate negative fixtures
    print("\n[Step 2] Testing deliberate negative metadata fixtures...")
    fixtures_results = {}

    missing_reference = copy.deepcopy(config)
    missing_reference["files"]["example"] = [".meta/src/reference/java/MissingReference.java"]
    ref_err = expect_rejected("missing reference", missing_reference, EXERCISE_DIR, "missing file")
    fixtures_results["missing_reference"] = ref_err

    missing_test = copy.deepcopy(config)
    missing_test["files"]["test"] = ["src/test/java/MissingTest.java"]
    test_err = expect_rejected("missing test", missing_test, EXERCISE_DIR, "missing file")
    fixtures_results["missing_test"] = test_err

    outside = copy.deepcopy(config)
    outside["files"]["solution"] = ["../../README.md"]
    outside_err = expect_rejected("outside-exercise traversal", outside, EXERCISE_DIR, "escapes exercise")
    fixtures_results["outside_exercise"] = outside_err

    # Validate canonical cases in tests.toml and ParallelLetterFrequencyTest.java
    print("\n[Step 3] Validating canonical cases against tests.toml and test suite...")
    tests_toml = parse_tests_toml(TESTS_TOML_FILE)
    test_suite_text = (EXERCISE_DIR / config["files"]["test"][0]).read_text(encoding="utf-8")

    assert ANCHOR_TEXT_SUBSTRING in test_suite_text, (
        f"Anchor text substring {ANCHOR_TEXT_SUBSTRING!r} not found in test suite!"
    )
    print(f"  ✓ Anchor case text verified: '{ANCHOR_TEXT_SUBSTRING}' is present in testLargeTexts (largeTexts4).")

    for case in CANONICAL_CASES:
        uuid = case["uuid"]
        assert uuid in tests_toml, f"UUID {uuid} not found in tests.toml"
        expected_desc = tests_toml[uuid]["description"]
        assert expected_desc.lower() == case["display_name"].lower(), (
            f"Description mismatch for UUID {uuid}: expected '{expected_desc}', got '{case['display_name']}'"
        )
        display_annotation = f'@DisplayName("{case["display_name"]}")'
        assert display_annotation in test_suite_text, (
            f"Annotation {display_annotation} missing in ParallelLetterFrequencyTest.java!"
        )
        print(f"  ✓ UUID {uuid} -> '{case['display_name']}' [method: {case['method']}]")

    solution_rel = config["files"]["solution"][0]
    learner_stub_path = EXERCISE_DIR / solution_rel

    # Record working tree file hashes
    solution_files = [EXERCISE_DIR / p for p in config["files"]["solution"]]
    test_files = [EXERCISE_DIR / p for p in config["files"]["test"]]
    target_files = solution_files + test_files
    initial_hashes = hash_files(target_files)

    # 4. Check learner starter stub is unsolved
    print("\n[Step 4] Checking learner starter stub...")
    stub_content = learner_stub_path.read_text(encoding="utf-8")
    assert "UnsupportedOperationException" in stub_content, "Learner stub must remain unsolved!"
    print("  ✓ Learner stub confirmed unsolved (throws UnsupportedOperationException).")

    env = get_env()
    tool_versions = get_tool_versions(env)
    print(f"  Tool versions: Python {tool_versions['python']}, {tool_versions['java']}, {tool_versions['gradle']}")

    results = {
        "task": "R58-T009",
        "exercise": "parallel-letter-frequency",
        "timestamp_unix": int(time.time()),
        "status": "RUNNING",
        "tool_versions": tool_versions,
        "metadata_validation": {
            "real_config": "PASSED: all real config.json file roles resolve inside the exercise.",
            "fixtures": {
                "missing_reference": {"status": "REJECTED_AS_EXPECTED", "error": fixtures_results["missing_reference"]},
                "missing_test": {"status": "REJECTED_AS_EXPECTED", "error": fixtures_results["missing_test"]},
                "outside_exercise": {"status": "REJECTED_AS_EXPECTED", "error": fixtures_results["outside_exercise"]},
            },
        },
        "file_map": {role: entries for role, entries in config["files"].items()},
        "tests": {},
        "canonical_cases": {},
        "anchor_case": {
            "method": "testLargeTexts",
            "display_name": "large texts",
            "text_substring": ANCHOR_TEXT_SUBSTRING,
            "status": "PENDING",
        },
        "runs": {},
        "checks": {},
    }

    try:
        # Scenario A: Reference solution execution in isolated scratch copy
        print("\n[Step 5.A] Running test suite against maintained reference in isolated scratch directory...")
        temp_a_path = None
        with tempfile.TemporaryDirectory(prefix="r58-t009-ref-") as tmp_dir:
            temp_a_path = Path(tmp_dir)
            scratch = copy_exercise_with_reference(temp_a_path, config)
            proc = run_gradle_test(scratch, env)
            print(f"  Gradle exit code: {proc.returncode}")
            assert proc.returncode == 0, f"Reference test execution failed with exit code {proc.returncode}!\nSTDERR: {proc.stderr[-1000:]}"

            ref_summary = parse_xml_results(scratch)
            print(f"  Total tests: {ref_summary['total']}, Executed: {ref_summary['executed']}, Passed: {ref_summary['passed']}, "
                  f"Failures: {ref_summary['failures']}, Errors: {ref_summary['errors']}")

            assert ref_summary["executed"] == len(CANONICAL_CASES), (
                f"Expected {len(CANONICAL_CASES)} executed tests, got {ref_summary['executed']}"
            )
            assert ref_summary["failures"] == 0, f"Expected 0 failures, got {ref_summary['failures']}"
            assert ref_summary["errors"] == 0, f"Expected 0 errors, got {ref_summary['errors']}"
            assert ref_summary["skipped"] == 0, f"Expected 0 skipped, got {ref_summary['skipped']}"

            for case in CANONICAL_CASES:
                c_name = case["display_name"]
                status = ref_summary["case_results"].get(c_name, "NOT_FOUND")
                assert status == "PASSED", f"Canonical case '{c_name}' did not pass! Status: {status}"
                results["canonical_cases"][case["method"]] = {
                    "display_name": case["display_name"],
                    "uuid": case["uuid"],
                    "status": "PASSED",
                }

            # Anchor case verification
            assert results["canonical_cases"]["testLargeTexts"]["status"] == "PASSED"
            results["anchor_case"]["status"] = "PASSED"
            print(f"  ✓ Anchor case 'large texts' successfully passed against reference.")

            results["tests"] = {
                "total": ref_summary["total"],
                "executed": ref_summary["executed"],
                "passed": ref_summary["passed"],
                "failures": ref_summary["failures"],
                "errors": ref_summary["errors"],
                "skipped": ref_summary["skipped"],
            }
            results["runs"]["maintained_reference"] = {
                "return_code": proc.returncode,
                "executed": ref_summary["executed"],
                "passed": ref_summary["passed"],
                "failures": ref_summary["failures"],
                "errors": ref_summary["errors"],
                "status": "PASSED",
            }
            results["checks"]["reference_tests_passed"] = True

        assert temp_a_path is not None and not temp_a_path.exists(), "Temporary directory for Scenario A was not cleaned up!"
        assert_learner_unchanged(target_files, initial_hashes, "after Scenario A (reference run)")
        print("  ✓ Temporary directory cleaned up; working tree hashes identical.")

        # Scenario B: Deliberately failing reference mutant
        print("\n[Step 5.B] Testing runner rejection of deliberately failing mutant reference...")
        temp_b_path = None
        with tempfile.TemporaryDirectory(prefix="r58-t009-fail-") as tmp_dir:
            temp_b_path = Path(tmp_dir)
            scratch_fail = copy_exercise_with_reference(temp_b_path, config, mutant_patch="empty_map")
            proc_fail = run_gradle_test(scratch_fail, env)
            print(f"  Mutant Gradle exit code: {proc_fail.returncode}")
            assert proc_fail.returncode != 0, "Mutant reference run should have exited non-zero!"

            fail_summary = parse_xml_results(scratch_fail)
            print(f"  Mutant executed: {fail_summary['executed']}, Failures: {fail_summary['failures']}, Errors: {fail_summary['errors']}")
            assert fail_summary["failures"] > 0, "Mutant reference run should have produced assertion failures!"
            assert fail_summary["case_results"].get("large texts") == "FAILED", (
                "Anchor case 'large texts' should have failed for empty_map mutant!"
            )
            print("  ✓ Deliberately failing mutant was correctly rejected by runner.")

            results["runs"]["deliberately_failing_mutant"] = {
                "return_code": proc_fail.returncode,
                "executed": fail_summary["executed"],
                "passed": fail_summary["passed"],
                "failures": fail_summary["failures"],
                "errors": fail_summary["errors"],
                "status": "REJECTED_AS_EXPECTED",
            }
            results["checks"]["mutant_rejected"] = True

        assert temp_b_path is not None and not temp_b_path.exists(), "Temporary directory for Scenario B was not cleaned up!"
        assert_learner_unchanged(target_files, initial_hashes, "after Scenario B (mutant run)")
        print("  ✓ Temporary directory cleaned up; working tree hashes identical.")

        # Scenario C: Empty test selection
        print("\n[Step 5.C] Testing runner rejection of empty test selection...")
        temp_c_path = None
        with tempfile.TemporaryDirectory(prefix="r58-t009-zero-") as tmp_dir:
            temp_c_path = Path(tmp_dir)
            scratch_zero = copy_exercise_with_reference(temp_c_path, config)
            proc_zero = run_gradle_test(scratch_zero, env, extra_args=["--tests", "NoSuchParallelLetterFrequencyTestClass"])
            print(f"  Empty selection Gradle exit code: {proc_zero.returncode}")
            assert proc_zero.returncode != 0, "Empty test selection should exit non-zero!"

            zero_summary = parse_xml_results(scratch_zero)
            print(f"  Empty selection executed tests: {zero_summary['executed']}")
            assert zero_summary["executed"] == 0, f"Expected 0 executed tests, got {zero_summary['executed']}"
            print("  ✓ Empty test selection was correctly rejected by runner.")

            results["runs"]["empty_test_selection"] = {
                "return_code": proc_zero.returncode,
                "executed": zero_summary["executed"],
                "status": "REJECTED_AS_EXPECTED",
            }
            results["checks"]["empty_selection_rejected"] = True

        assert temp_c_path is not None and not temp_c_path.exists(), "Temporary directory for Scenario C was not cleaned up!"
        assert_learner_unchanged(target_files, initial_hashes, "after Scenario C (zero-test run)")
        print("  ✓ Temporary directory cleaned up; working tree hashes identical.")

    finally:
        assert_learner_unchanged(target_files, initial_hashes, "final cleanup assertion")

    # 6. Verify maintenance document
    print("\n[Step 6] Checking maintenance document docs/maintenance/parallel-letter-frequency.md...")
    verify_maintenance_doc()
    print("  ✓ Maintenance doc verified: names real paths and distinguishes generated artifacts.")
    results["checks"]["maintenance_doc_verified"] = True

    # 7. Final working tree integrity check
    print("\n[Step 7] Verifying working tree integrity...")
    post_hashes = hash_files(target_files)
    assert initial_hashes == post_hashes, "Working tree files were modified during check execution!"
    assert "UnsupportedOperationException" in learner_stub_path.read_text(encoding="utf-8")
    print("  ✓ Working tree integrity verified: completely untouched.")
    results["checks"]["working_tree_unchanged"] = True
    results["checks"]["real_config_passed"] = True
    results["checks"]["all_three_negative_fixtures_rejected"] = True

    # 8. Write results
    results["status"] = "PASSED"
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    results_file = WORK_DIR / "results.json"
    latest_file = WORK_DIR / "latest-result.json"

    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    with open(latest_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"\n[Summary] All checks PASSED successfully.")
    print(f"Evidence saved to {results_file} and {latest_file}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except AssertionError as e:
        print(f"\n[FAILURE] Assertion failed: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}", file=sys.stderr)
        sys.exit(2)
