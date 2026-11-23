#!/usr/bin/env python3
"""Validate alphametics case rationales and the reference test suite."""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from common import record_versions, run_reference_tests  # noqa: E402


SLUG = "alphametics"
TASK = "R58-T031"
EVIDENCE = ROOT / "work" / TASK
EXPECTED = {
    "e0c08b07-9028-4d5f-91e1-d178fead8e1a": ("testThreeLetters", "1 + 99 = 100"),
    "a504ee41-cb92-4ec2-9f11-c37e95ab3f25": ("testUniqueValue", "distinct letters"),
    "4e3b81d2-be7b-4c5c-9a80-cd72bc6d465a": ("testLeadingZero", "forces A to zero"),
}


def main() -> int:
    record_versions(EVIDENCE)
    metadata_path = ROOT / "exercises/practice/alphametics/.meta/tests.toml"
    metadata = tomllib.loads(metadata_path.read_text(encoding="utf-8"))
    entries = {key: value for key, value in metadata.items() if isinstance(value, dict)}
    if len(entries) != 10:
        raise RuntimeError(f"Expected 10 canonical cases; found {len(entries)}")
    included = sum(entry.get("include", True) for entry in entries.values())
    excluded = len(entries) - included
    if (included, excluded) != (10, 0):
        raise RuntimeError(f"Unexpected metadata counts: {included} included, {excluded} excluded")
    source = (ROOT / "exercises/practice/alphametics/src/test/java/AlphameticsTest.java").read_text()
    for uuid, (test_name, rationale) in EXPECTED.items():
        entry = entries.get(uuid)
        if entry is None or not entry.get("comment"):
            raise RuntimeError(f"Missing comment for {uuid}")
        if test_name not in source or rationale not in entry["comment"]:
            raise RuntimeError(f"Rationale/test mapping mismatch for {uuid}")
    (EVIDENCE / "case-counts.txt").write_text(
        f"Canonical cases: {len(entries)}\nIncluded: {included}\nExcluded: {excluded}\n",
        encoding="utf-8",
    )
    test_result = run_reference_tests(SLUG, EVIDENCE)
    print(
        f"{TASK}: metadata valid; {test_result['tests']} cases discovered, "
        f"{test_result['failures']} failures, {test_result['skipped']} skipped; "
        "10 included, 0 excluded"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
