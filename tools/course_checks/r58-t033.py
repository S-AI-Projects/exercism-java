#!/usr/bin/env python3
"""Check that gigasecond's existing test rejects an off-by-one duration mutant."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from common import record_versions, run_reference_tests  # noqa: E402

TASK = "R58-T033"
EVIDENCE = ROOT / "work" / TASK
MUTANT_TEST = "modernTime"


def shorten_duration(source: Path) -> None:
    if source.name != "Gigasecond.java":
        return
    text = source.read_text(encoding="utf-8")
    original = "plusSeconds(1000000000)"
    if text.count(original) != 1:
        raise RuntimeError("Expected exactly one gigasecond duration expression in the scratch reference")
    source.write_text(text.replace(original, "plusSeconds(999999999)"), encoding="utf-8")


def main() -> int:
    record_versions(EVIDENCE)
    original = run_reference_tests("gigasecond", EVIDENCE / "original")
    mutant = run_reference_tests(
        "gigasecond", EVIDENCE / "mutant", mutation=shorten_duration, expected_failure=MUTANT_TEST
    )
    summary = (
        f"Original: {original['tests']} tests, {original['failures']} failures (pass).\n"
        f"Mutant: {mutant['tests']} tests, {mutant['failures']} failures; rejected by {MUTANT_TEST}.\n"
        "Mutation: plusSeconds(1000000000) -> plusSeconds(999999999).\n"
        "Diagnostic input/output: 2011-04-25 -> 2043-01-01T01:46:40; mutant -> 2043-01-01T01:46:39.\n"
    )
    (EVIDENCE / "mutation-summary.txt").write_text(summary, encoding="utf-8")
    print(f"{TASK}: original reference passes; off-by-one mutant rejected by {MUTANT_TEST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
