#!/usr/bin/env python3
"""Verify Pangram contract examples and the isolated reference test suite."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from common import java_environment, record_versions, run_reference_tests  # noqa: E402

TASK = "R58-T040"
EVIDENCE = ROOT / "work" / TASK
CASES = (
    ("the_quick_brown_fox_jumps_over_the_lazy_dog", True),
    ("the 1 quick brown fox jumps over the 2 lazy dogs", True),
    ("7h3 qu1ck brown fox jumps ov3r 7h3 lazy dog", False),
)
HARNESS = r'''public class PangramContractCheck {
    public static void main(String[] args) {
        PangramChecker checker = new PangramChecker();
        check(checker, "the_quick_brown_fox_jumps_over_the_lazy_dog", true);
        check(checker, "the 1 quick brown fox jumps over the 2 lazy dogs", true);
        check(checker, "7h3 qu1ck brown fox jumps ov3r 7h3 lazy dog", false);
    }

    private static void check(PangramChecker checker, String input, boolean expected) {
        boolean actual = checker.isPangram(input);
        if (actual != expected) throw new AssertionError(input + ": expected " + expected + ", got " + actual);
        System.out.println(actual);
    }
}'''


def main() -> int:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    record_versions(EVIDENCE)
    test_result = run_reference_tests("pangram", EVIDENCE)
    hint = (ROOT / "exercises/practice/pangram/.docs/hints.md").read_text(encoding="utf-8")
    for input_text, expected in CASES:
        if f"`{input_text}`" not in hint or f"`{str(expected).lower()}`" not in hint:
            raise RuntimeError(f"Decision table does not document {input_text!r} -> {expected}")
    missing = set("abcdefghijklmnopqrstuvwxyz") - set(CASES[2][0].lower())
    if missing != set("eit") or "`e`, `i`, and `t`" not in hint:
        raise RuntimeError(f"Incorrect missing-letter rationale: {sorted(missing)}")
    reference = ROOT / "exercises/practice/pangram/.meta/src/reference/java/PangramChecker.java"
    with tempfile.TemporaryDirectory(prefix="pangram-contract-") as temporary:
        directory = Path(temporary)
        harness = directory / "PangramContractCheck.java"
        harness.write_text(HARNESS + "\n", encoding="utf-8")
        compiled = subprocess.run(
            ["javac", "-d", str(directory), str(reference), str(harness)],
            capture_output=True,
            text=True,
            timeout=60,
            env=java_environment(),
        )
        if compiled.returncode != 0:
            raise RuntimeError(f"Contract harness did not compile: {compiled.stderr}")
        result = subprocess.run(
            ["java", "-cp", str(directory), "PangramContractCheck"],
            capture_output=True,
            text=True,
            timeout=30,
            env=java_environment(),
        )
        if result.returncode != 0 or result.stdout != "true\ntrue\nfalse\n":
            raise RuntimeError(f"Contract cases failed: {result.stdout!r}; {result.stderr}")
    (EVIDENCE / "decision-table-results.txt").write_text(result.stdout, encoding="utf-8")
    print(
        f"{TASK}: 3 decision-table cases match; reference suite: {test_result['tests']} cases "
        f"discovered, {test_result['failures']} failures, {test_result['skipped']} skipped"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
