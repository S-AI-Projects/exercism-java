#!/usr/bin/env python3
"""
Verification check for Task R58-T007 (saddle-points language construct analysis & learner guidance).

Verifies:
1. Resolves paths dynamically from exercises/practice/saddle-points/.meta/config.json.
2. Cross-checks tests.toml UUIDs and DisplayNames for named cases.
3. Confirms working-tree learner starter stub remains unsolved (UnsupportedOperationException)
   and ensures the working tree is never modified (SHA-256 integrity verification).
4. Copies exercise with dotfiles to an isolated temporary directory, substitutes the maintained
   reference into scratch src/main/java, enables all tests, and executes `./gradlew test --no-daemon`.
   Asserts returncode == 0, executed tests > 0 (all 9 canonical tests), failures == 0, errors == 0.
5. Compiles and executes the standalone micro-example (SaddlePointsBoxedPrimitiveExample.java)
   demonstrating the construct used by getRowMax (primitive unboxing) and the contrasting pitfall
   (boxed Integer object comparison with == outside the [-128, 127] cache).
   Asserts output lines match ["true", "false"].
6. Verifies published hint in exercises/practice/saddle-points/.docs/hints.md agrees with
   the micro-example outputs and names the construct present in the reference.
7. Records tool versions, inputs, expected vs actual outputs, and check results
   in work/R58-T007/results.json and work/R58-T007/latest-result.json.
"""

from __future__ import annotations

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
EXERCISE_DIR = REPO_ROOT / "exercises" / "practice" / "saddle-points"
WORK_DIR = REPO_ROOT / "work" / "R58-T007"
CONFIG_FILE = EXERCISE_DIR / ".meta" / "config.json"
TESTS_TOML_FILE = EXERCISE_DIR / ".meta" / "tests.toml"
HINTS_FILE = EXERCISE_DIR / ".docs" / "hints.md"
MICRO_EXAMPLE_FILE = WORK_DIR / "SaddlePointsBoxedPrimitiveExample.java"

NAMED_CASES = [
    {
        "method": "testCanIdentifySingleSaddlePoint",
        "display_name": "Can identify single saddle point",
        "uuid": "3e374e63-a2e0-4530-a39a-d53c560382bd",
    },
    {
        "method": "testCanIdentifyThatEmptyMatrixHasNoSaddlePoints",
        "display_name": "Can identify that empty matrix has no saddle points",
        "uuid": "6b501e2b-6c1f-491f-b1bb-7f278f760534",
    },
    {
        "method": "testCanIdentifyLackOfSaddlePointsWhenThereAreNone",
        "display_name": "Can identify lack of saddle points when there are none",
        "uuid": "8c27cc64-e573-4fcb-a099-f0ae863fb02f",
    },
    {
        "method": "testCanIdentifyMultipleSaddlePointsInAColumn",
        "display_name": "Can identify multiple saddle points in a column",
        "uuid": "6d1399bd-e105-40fd-a2c9-c6609507d7a3",
    },
    {
        "method": "testCanIdentifyMultipleSaddlePointsInARow",
        "display_name": "Can identify multiple saddle points in a Row",
        "uuid": "3e81dce9-53b3-44e6-bf26-e328885fd5d1",
    },
    {
        "method": "testCanIdentifySaddlePointInBottomRightCorner",
        "display_name": "Can identify saddle point in bottom right corner",
        "uuid": "88868621-b6f4-4837-bb8b-3fad8b25d46b",
    },
    {
        "method": "testCanIdentifySaddlePointsInANonSquareMatrix",
        "display_name": "Can identify saddle points in a non square matrix",
        "uuid": "5b9499ca-fcea-4195-830a-9c4584a0ee79",
    },
    {
        "method": "testCanIdentifyThatSaddlePointsInASingleColumnMatrixAreThoseWithMinimumValue",
        "display_name": "Can identify that saddle points in a single column matrix are those with the minimum value",
        "uuid": "ee99ccd2-a1f1-4283-ad39-f8c70f0cf594",
    },
    {
        "method": "testCanIdentifyThatSaddlePointsInASingleRowMatrixAreThoseWithMaximumValue",
        "display_name": "Can identify that saddle points in a single row matrix are those with the maximum value",
        "uuid": "63abf709-a84b-407f-a1b3-456638689713",
    },
]

EXPECTED_MICRO_OUTPUT = ["true", "false"]


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
    scratch = base_dir / "saddle-points"
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


def verify_micro_example(env: dict[str, str]) -> list[str]:
    assert MICRO_EXAMPLE_FILE.is_file(), f"Micro-example file missing at {MICRO_EXAMPLE_FILE}"
    with tempfile.TemporaryDirectory(prefix="r58-t007-micro-") as tmp_dir:
        classes_dir = Path(tmp_dir) / "classes"
        classes_dir.mkdir(parents=True, exist_ok=True)

        compile_cmd = ["javac", "-d", str(classes_dir), str(MICRO_EXAMPLE_FILE)]
        comp = subprocess.run(compile_cmd, env=env, capture_output=True, text=True, check=False)
        assert comp.returncode == 0, f"Micro-example compilation failed:\n{comp.stderr}"

        run_cmd = ["java", "-cp", str(classes_dir), "SaddlePointsBoxedPrimitiveExample"]
        run_res = subprocess.run(run_cmd, env=env, capture_output=True, text=True, check=False)
        assert run_res.returncode == 0, f"Micro-example execution failed:\n{run_res.stderr}"

        lines = run_res.stdout.strip().splitlines()
        return lines


def verify_published_hint() -> None:
    assert HINTS_FILE.is_file(), f"hints.md not found at {HINTS_FILE}"
    hint_text = HINTS_FILE.read_text(encoding="utf-8")
    assert "getRowMax" in hint_text, "hints.md must discuss getRowMax"
    assert "Collections.max" in hint_text, "hints.md must mention Collections.max construct"
    assert "primitive" in hint_text.lower(), "hints.md must discuss primitive values"
    assert "boxed" in hint_text.lower(), "hints.md must discuss boxed values"
    assert "128" in hint_text, "hints.md must include contrasting pitfall with value 128"
    assert "true" in hint_text, "hints.md must include true output"
    assert "false" in hint_text, "hints.md must include false output"


def main() -> int:
    print("==================================================")
    print("Task R58-T007 Verification Check: saddle-points")
    print("==================================================")

    # 1. Metadata and config checks
    assert CONFIG_FILE.is_file(), f"Missing config.json at {CONFIG_FILE}"
    assert TESTS_TOML_FILE.is_file(), f"Missing tests.toml at {TESTS_TOML_FILE}"

    with open(CONFIG_FILE, encoding="utf-8") as f:
        config = json.load(f)

    tests_toml = parse_tests_toml(TESTS_TOML_FILE)

    solution_rel = config["files"]["solution"][0]
    test_rel = config["files"]["test"][0]
    learner_stub_path = EXERCISE_DIR / solution_rel

    print("\n[Step 1] Validating named cases against tests.toml and MatrixTest.java...")
    for case in NAMED_CASES:
        uuid = case["uuid"]
        assert uuid in tests_toml, f"UUID {uuid} not found in tests.toml"
        expected_desc = tests_toml[uuid]["description"]
        assert expected_desc.lower() == case["display_name"].lower(), (
            f"Description mismatch for UUID {uuid}: expected '{expected_desc}', got '{case['display_name']}'"
        )
        print(f"  ✓ UUID {uuid} -> '{case['display_name']}'")

    # Record working tree file hashes
    solution_files = [EXERCISE_DIR / p for p in config["files"]["solution"]]
    test_files = [EXERCISE_DIR / p for p in config["files"]["test"]]
    target_files = solution_files + test_files
    initial_hashes = hash_files(target_files)

    # 2. Check learner starter stub is unsolved
    print("\n[Step 2] Checking learner starter stub...")
    stub_content = learner_stub_path.read_text(encoding="utf-8")
    assert "UnsupportedOperationException" in stub_content, "Learner stub must remain unsolved!"
    print("  ✓ Learner stub confirmed unsolved (throws UnsupportedOperationException).")

    env = get_env()
    tool_versions = get_tool_versions(env)
    print(f"  Tool versions: Python {tool_versions['python']}, {tool_versions['java']}, {tool_versions['gradle']}")

    results = {
        "task": "R58-T007",
        "exercise": "saddle-points",
        "timestamp_unix": int(time.time()),
        "status": "RUNNING",
        "tool_versions": tool_versions,
        "language_construct_analysis": {
            "selected_construct": "primitive versus boxed values",
            "examined_constructs": {
                "collection_mutation": "Not used. Collections.max reads the row list without modifying its contents or size.",
                "exception_contracts": "Not used. getRowMax does not declare, catch, or customize an exception contract.",
                "primitive_versus_boxed_values": "Actually used. The matrix stores List<List<Integer>> (boxed Integer objects). Collections.max returns Integer, which is auto-unboxed to primitive int by getRowMax.",
            },
            "relevance_to_exercise": "Unboxing to primitive int ensures numeric equality comparison via ==. Boxed Integer comparison with == tests reference identity, failing for values outside the [-128, 127] cache.",
        },
        "micro_example": {
            "source_file": str(MICRO_EXAMPLE_FILE.relative_to(REPO_ROOT)),
            "expected_output": EXPECTED_MICRO_OUTPUT,
            "actual_output": None,
        },
        "tests": {},
        "named_cases": {},
        "checks": {},
    }

    # 3. Reference solution execution in isolated scratch copy
    print("\n[Step 3] Running test suite against maintained reference in isolated scratch directory...")
    with tempfile.TemporaryDirectory(prefix="r58-t007-ref-") as tmp_dir:
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
            print(f"  ✓ [NAMED CASE] '{c_name}' -> PASSED")
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

    # 4. Micro-example compilation and execution
    print("\n[Step 4] Compiling and executing standalone micro-example...")
    actual_micro_output = verify_micro_example(env)
    print(f"  Actual micro-example output: {actual_micro_output}")
    print(f"  Expected micro-example output: {EXPECTED_MICRO_OUTPUT}")
    assert actual_micro_output == EXPECTED_MICRO_OUTPUT, (
        f"Micro-example output mismatch: expected {EXPECTED_MICRO_OUTPUT}, got {actual_micro_output}"
    )
    print("  ✓ Micro-example output verified: primitive == yields true, boxed == yields false.")
    results["micro_example"]["actual_output"] = actual_micro_output
    results["checks"]["micro_example_asserted"] = True

    # 5. Published hint verification
    print("\n[Step 5] Checking published hint in exercises/practice/saddle-points/.docs/hints.md...")
    verify_published_hint()
    print("  ✓ Published hint verified: covers primitive vs boxed values, getRowMax, snippet, and pitfall.")
    results["checks"]["published_hint_agrees"] = True

    # 6. Verify working tree integrity
    print("\n[Step 6] Verifying working tree integrity...")
    post_hashes = hash_files(target_files)
    assert initial_hashes == post_hashes, "Working tree files were modified during check execution!"
    assert "UnsupportedOperationException" in learner_stub_path.read_text(encoding="utf-8")
    print("  ✓ Working tree integrity verified: completely untouched.")
    results["checks"]["working_tree_unchanged"] = True

    # 7. Write results
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
