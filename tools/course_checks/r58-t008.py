#!/usr/bin/env python3
"""Validate Bob exercise config.json files map and negative path fixtures for Task R58-T008."""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EXERCISE_DIR = REPO_ROOT / "exercises" / "practice" / "bob"


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
    print(f"PASS: {label} fixture rejected: {msg}")
    return msg


def run_metadata_checks() -> dict[str, str]:
    config_path = EXERCISE_DIR / ".meta" / "config.json"
    assert config_path.is_file(), f"Missing config.json at {config_path}"
    config = json.loads(config_path.read_text(encoding="utf-8"))

    # 1. Real metadata check
    errors = validate_files(config, EXERCISE_DIR)
    if errors:
        raise AssertionError("Real metadata invalid: " + "; ".join(errors))
    print("PASS: all real config.json file roles resolve inside the exercise.")

    fixture_results = {
        "real_metadata": "PASS: all real config.json file roles resolve inside the exercise."
    }

    # 2. Missing reference fixture
    missing_reference = copy.deepcopy(config)
    missing_reference["files"]["example"] = [".meta/src/reference/java/MissingReference.java"]
    msg_ref = expect_rejected("missing reference", missing_reference, EXERCISE_DIR, "missing file")
    fixture_results["missing_reference"] = f"REJECTED: {msg_ref}"

    # 3. Missing test fixture
    missing_test = copy.deepcopy(config)
    missing_test["files"]["test"] = ["src/test/java/MissingTest.java"]
    msg_test = expect_rejected("missing test", missing_test, EXERCISE_DIR, "missing file")
    fixture_results["missing_test"] = f"REJECTED: {msg_test}"

    # 4. Outside-exercise traversal fixture
    outside = copy.deepcopy(config)
    outside["files"]["solution"] = ["../../README.md"]
    msg_outside = expect_rejected("outside-exercise traversal", outside, EXERCISE_DIR, "escapes exercise")
    fixture_results["outside_exercise"] = f"REJECTED: {msg_outside}"

    return fixture_results


def main() -> int:
    try:
        run_metadata_checks()
        return 0
    except AssertionError as e:
        print(f"FAIL: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
