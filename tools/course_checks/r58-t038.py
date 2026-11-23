#!/usr/bin/env python3
"""Validate Sum of Multiples config paths and run the reference-backed tests."""

from __future__ import annotations

import copy
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from common import record_versions, run_reference_tests, validate_files_config  # noqa: E402

TASK = "R58-T038"
SLUG = "sum-of-multiples"
EVIDENCE = ROOT / "work" / TASK


def expect_rejected(exercise: Path, config: dict, expected_message: str) -> None:
    try:
        validate_files_config(exercise, config)
    except RuntimeError as error:
        if expected_message not in str(error):
            raise RuntimeError(f"Expected {expected_message!r}, got {error!r}") from error
        return
    raise RuntimeError(f"Invalid fixture was accepted: expected {expected_message}")


def main() -> int:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    record_versions(EVIDENCE)
    exercise = ROOT / "exercises/practice/sum-of-multiples"
    config_path = exercise / ".meta/config.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    resolved = validate_files_config(exercise, config)
    expected_roles = {"solution", "test", "example", "invalidator"}
    if not expected_roles.issubset(resolved):
        raise RuntimeError(f"Missing config roles: {expected_roles - set(resolved)}")
    fixtures = []
    missing_reference = copy.deepcopy(config)
    missing_reference["files"]["example"] = [".meta/src/reference/java/Missing.java"]
    expect_rejected(exercise, missing_reference, "is missing")
    fixtures.append("missing example/reference path: rejected")
    missing_test = copy.deepcopy(config)
    missing_test["files"]["test"] = ["src/test/java/MissingTest.java"]
    expect_rejected(exercise, missing_test, "is missing")
    fixtures.append("missing test path: rejected")
    outside = copy.deepcopy(config)
    outside["files"]["example"] = ["../../README.md"]
    expect_rejected(exercise, outside, "escapes the exercise")
    fixtures.append("outside-exercise path: rejected")
    report = ["Config path roles:"]
    report.extend(f"- {role}: {', '.join(str(path.relative_to(ROOT)) for path in paths)}" for role, paths in resolved.items())
    report.extend(["Invalid fixtures:", *[f"- {item}" for item in fixtures]])
    (EVIDENCE / "path-check-results.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    test_result = run_reference_tests(SLUG, EVIDENCE)
    print(
        f"{TASK}: all declared paths valid; 3 invalid fixtures rejected; reference suite: "
        f"{test_result['tests']} cases discovered, {test_result['failures']} failures, "
        f"{test_result['skipped']} skipped"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
