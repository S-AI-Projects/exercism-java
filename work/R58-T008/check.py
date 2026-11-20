#!/usr/bin/env python3
"""
Verification check for Task R58-T008 (bob metadata path validation and reference testing).

Verifies:
1. Dynamically resolves solution, test, example, and invalidator paths from
   exercises/practice/bob/.meta/config.json.
2. Ensures all declared paths are relative, do not escape the exercise root, and exist.
3. Tests three deliberately invalid metadata fixtures:
   - missing-reference
   - missing-test
   - outside-exercise traversal
   Asserting each fails for the intended reason.
4. Confirms working-tree learner starter stub remains unsolved (UnsupportedOperationException)
   and ensures the working tree is never modified (SHA-256 integrity verification).
5. Copies exercise with dotfiles to an isolated temporary directory, substitutes the maintained
   reference into scratch src/main/java, enables all tests, and executes `./gradlew test --no-daemon`.
   Asserts returncode == 0, executed tests > 0 (all 26 canonical tests), failures == 0, errors == 0.
6. Verifies docs/maintenance/bob.md names real stub, reference, and test paths, and distinguishes
   generated artifacts.
7. Records tool versions, inputs, expected vs actual outputs, and check results
   in work/R58-T008/results.json and work/R58-T008/latest-result.json.
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
EXERCISE_DIR = REPO_ROOT / "exercises" / "practice" / "bob"
WORK_DIR = REPO_ROOT / "work" / "R58-T008"
CONFIG_FILE = EXERCISE_DIR / ".meta" / "config.json"
TESTS_TOML_FILE = EXERCISE_DIR / ".meta" / "tests.toml"
MAINTENANCE_DOC = REPO_ROOT / "docs" / "maintenance" / "bob.md"

NAMED_CASES = [
    {"method": "saySomething", "display_name": "stating something", "uuid": "e162fead-606f-437a-a166-d051915cea8e"},
    {"method": "shouting", "display_name": "shouting", "uuid": "73a966dc-8017-47d6-bb32-cf07d1a5fcd9"},
    {"method": "shoutingGibberish", "display_name": "shouting gibberish", "uuid": "d6c98afd-df35-4806-b55e-2c457c3ab748"},
    {"method": "shoutingAStatementContainingQuestionMark", "display_name": "shouting a statement containing a question mark", "uuid": "3c954328-86fb-4c71-8961-e18d6a5e2517"},
    {"method": "askingAQuestion", "display_name": "asking a question", "uuid": "8a2e771d-d6f1-4e3f-b6c6-b41495556e37"},
    {"method": "askingANumericQuestion", "display_name": "asking a numeric question", "uuid": "81080c62-4e4d-4066-b30a-48d8d76920d9"},
    {"method": "askingGibberish", "display_name": "asking gibberish", "uuid": "2a02716d-685b-4e2e-a804-2adaf281c01e"},
    {"method": "talkingForcefully", "display_name": "talking forcefully", "uuid": "c02f9179-ab16-4aa7-a8dc-940145c385f7"},
    {"method": "usingAcronymsInRegularSpeech", "display_name": "using acronyms in regular speech", "uuid": "153c0e25-9bb5-4ec5-966e-598463658bcd"},
    {"method": "forcefulQuestions", "display_name": "forceful question", "uuid": "a5193c61-4a92-4f68-93e2-f554eb385ec6"},
    {"method": "shoutingNumbers", "display_name": "shouting numbers", "uuid": "a20e0c54-2224-4dde-8b10-bd2cdd4f61bc"},
    {"method": "onlyNumbers", "display_name": "no letters", "uuid": "f7bc4b92-bdff-421e-a238-ae97f230ccac"},
    {"method": "questionWithOnlyNumbers", "display_name": "question with no letters", "uuid": "bb0011c5-cd52-4a5b-8bfb-a87b6283b0e2"},
    {"method": "shoutingWithSpecialCharacters", "display_name": "shouting with special characters", "uuid": "496143c8-1c31-4c01-8a08-88427af85c66"},
    {"method": "shoutingWithNoExclamationMark", "display_name": "shouting with no exclamation mark", "uuid": "e6793c1c-43bd-4b8d-bc11-499aea73925f"},
    {"method": "statementContainingQuestionMark", "display_name": "statement containing question mark", "uuid": "aa8097cc-c548-4951-8856-14a404dd236a"},
    {"method": "nonLettersWithQuestion", "display_name": "non-letters with question", "uuid": "9bfc677d-ea3a-45f2-be44-35bc8fa3753e"},
    {"method": "prattlingOn", "display_name": "prattling on", "uuid": "8608c508-f7de-4b17-985b-811878b3cf45"},
    {"method": "silence", "display_name": "silence", "uuid": "bc39f7c6-f543-41be-9a43-fd1c2f753fc0"},
    {"method": "prolongedSilence", "display_name": "prolonged silence", "uuid": "d6c47565-372b-4b09-b1dd-c40552b8378b"},
    {"method": "alternateSilence", "display_name": "alternate silence", "uuid": "4428f28d-4100-4d85-a902-e5a78cb0ecd3"},
    {"method": "startingWithWhitespace", "display_name": "starting with whitespace", "uuid": "5371ef75-d9ea-4103-bcfa-2da973ddec1b"},
    {"method": "endingWithWhiteSpace", "display_name": "ending with whitespace", "uuid": "05b304d6-f83b-46e7-81e0-4cd3ca647900"},
    {"method": "otherWhiteSpace", "display_name": "other whitespace", "uuid": "72bd5ad3-9b2f-4931-a988-dce1f5771de2"},
    {"method": "nonQuestionEndingWithWhiteSpace", "display_name": "non-question ending with whitespace", "uuid": "12983553-8601-46a8-92fa-fcaa3bc4a2a0"},
    {"method": "multipleLineQuestion", "display_name": "multiple line question", "uuid": "2c7278ac-f955-4eb4-bf8f-e33eb4116a15"},
]


def get_env() -> dict[str, str]:
    env = os.environ.copy()
    candidate_jdks = [
        "/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home",
        "/opt/homebrew/Cellar/openjdk@21/21.0.13.0.3/libexec/openjdk.jdk/Contents/Home",
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


def copy_exercise_with_reference(base_dir: Path, config: dict) -> Path:
    scratch = base_dir / "bob"
    shutil.copytree(EXERCISE_DIR, scratch, ignore=shutil.ignore_patterns(".gradle", "build"))

    solution_rel = config["files"]["solution"][0]
    test_rel = config["files"]["test"][0]
    example_rels = config["files"]["example"]

    # Substitute reference into scratch src/main/java
    dest_solution = scratch / solution_rel
    dest_dir = dest_solution.parent
    dest_dir.mkdir(parents=True, exist_ok=True)

    for ref_rel in example_rels:
        ref_file = scratch / ref_rel
        assert ref_file.is_file(), f"Reference file {ref_rel} missing from scratch copy"
        shutil.copy2(ref_file, dest_dir / ref_file.name)

    # Enable all tests by stripping @Disabled in scratch copy
    scratch_test = scratch / test_rel
    tc = scratch_test.read_text(encoding="utf-8")
    tc = re.sub(r'^\s*@Disabled\("Remove to run test"\)\s*\n', "", tc, flags=re.MULTILINE)
    scratch_test.write_text(tc, encoding="utf-8")

    return scratch


def run_gradle_test(scratch: Path, env: dict[str, str]) -> subprocess.CompletedProcess:
    cmd = ["./gradlew", "test", "--no-daemon"]
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
    assert "src/main/java/Bob.java" in doc_text, "doc must mention real starter stub path"
    assert "src/test/java/BobTest.java" in doc_text, "doc must mention real test suite path"
    assert ".meta/src/reference/java/Bob.java" in doc_text, "doc must mention real reference path"
    assert "build/" in doc_text, "doc must distinguish build/ generated artifacts"
    assert ".meta/tests.toml" in doc_text, "doc must discuss tests.toml canonical metadata"


def main() -> int:
    print("==================================================")
    print("Task R58-T008 Verification Check: bob")
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

    # Validate named cases in tests.toml
    print("\n[Step 3] Validating named cases against tests.toml and BobTest.java...")
    tests_toml = parse_tests_toml(TESTS_TOML_FILE)
    for case in NAMED_CASES:
        uuid = case["uuid"]
        assert uuid in tests_toml, f"UUID {uuid} not found in tests.toml"
        expected_desc = tests_toml[uuid]["description"]
        assert expected_desc.lower() == case["display_name"].lower(), (
            f"Description mismatch for UUID {uuid}: expected '{expected_desc}', got '{case['display_name']}'"
        )
        print(f"  ✓ UUID {uuid} -> '{case['display_name']}'")

    solution_rel = config["files"]["solution"][0]
    test_rel = config["files"]["test"][0]
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
        "task": "R58-T008",
        "exercise": "bob",
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
        "named_cases": {},
        "checks": {},
    }

    # 5. Reference solution execution in isolated scratch copy
    print("\n[Step 5] Running test suite against maintained reference in isolated scratch directory...")
    with tempfile.TemporaryDirectory(prefix="r58-t008-ref-") as tmp_dir:
        tmp_path = Path(tmp_dir)
        scratch = copy_exercise_with_reference(tmp_path, config)
        proc = run_gradle_test(scratch, env)
        print(f"  Gradle exit code: {proc.returncode}")
        assert proc.returncode == 0, f"Reference test execution failed with exit code {proc.returncode}!\nSTDERR: {proc.stderr[-1000:]}"

        ref_summary = parse_xml_results(scratch)
        print(f"  Total tests: {ref_summary['total']}, Executed: {ref_summary['executed']}, Passed: {ref_summary['passed']}, "
              f"Failures: {ref_summary['failures']}, Errors: {ref_summary['errors']}")

        assert ref_summary["executed"] > 0, "Zero tests were executed!"
        assert ref_summary["failures"] == 0, f"Expected 0 failures, got {ref_summary['failures']}"
        assert ref_summary["errors"] == 0, f"Expected 0 errors, got {ref_summary['errors']}"
        assert ref_summary["skipped"] == 0, f"Expected 0 skipped, got {ref_summary['skipped']}"

        for case in NAMED_CASES:
            c_name = case["display_name"]
            status = ref_summary["case_results"].get(c_name, "NOT_FOUND")
            assert status == "PASSED", f"Named case '{c_name}' did not pass! Status: {status}"
            results["named_cases"][case["method"]] = {
                "display_name": case["display_name"],
                "uuid": case["uuid"],
                "status": "PASSED",
            }

        results["tests"] = {
            "total": ref_summary["total"],
            "executed": ref_summary["executed"],
            "passed": ref_summary["passed"],
            "failures": ref_summary["failures"],
            "errors": ref_summary["errors"],
            "skipped": ref_summary["skipped"],
        }
        results["checks"]["reference_tests_passed"] = True

    # 6. Verify maintenance document
    print("\n[Step 6] Checking maintenance document docs/maintenance/bob.md...")
    verify_maintenance_doc()
    print("  ✓ Maintenance doc verified: names real paths and distinguishes generated artifacts.")
    results["checks"]["maintenance_doc_verified"] = True

    # 7. Verify working tree integrity
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
