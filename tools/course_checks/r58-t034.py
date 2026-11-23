#!/usr/bin/env python3
"""Compare ListOps behavior before and after the scoped foldRight refactor."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from common import java_environment, record_versions, run_reference_tests  # noqa: E402

TASK = "R58-T034"
EVIDENCE = ROOT / "work" / TASK
SOURCE = "exercises/practice/list-ops/.meta/src/reference/java/ListOps.java"
HARNESS = r'''import java.util.List;
public class ListOpsParity {
    public static void main(String[] args) {
        System.out.println("append=" + ListOps.append(List.of(1, 2), List.of(3)));
        System.out.println("concat=" + ListOps.concat(List.of(List.of(1, 2), List.of(3))));
        System.out.println("filter=" + ListOps.filter(List.of(1, -2, 3), value -> value > 0));
        System.out.println("size=" + ListOps.size(List.of(1, 2, 3)));
        System.out.println("map=" + ListOps.map(List.of(1, 2), value -> value * 2));
        System.out.println("reverse=" + ListOps.reverse(List.of(1, 2, 3)));
        System.out.println("foldLeft=" + ListOps.foldLeft(List.of(1, 2, 3), 0, (a, b) -> a - b));
        System.out.println("foldRight=" + ListOps.foldRight(List.of(1, 2, 3), 0, (a, b) -> a - b));
    }
}'''


def run_harness(source_text: str, directory: Path) -> str:
    source = directory / "ListOps.java"
    harness = directory / "ListOpsParity.java"
    source.write_text(source_text, encoding="utf-8")
    harness.write_text(HARNESS + "\n", encoding="utf-8")
    environment = java_environment()
    compiled = subprocess.run(
        ["javac", str(source), str(harness)], cwd=directory, capture_output=True, text=True, env=environment, timeout=60
    )
    if compiled.returncode != 0:
        raise RuntimeError(f"javac failed: {compiled.stderr}")
    executed = subprocess.run(
        ["java", "-cp", str(directory), "ListOpsParity"],
        cwd=directory,
        capture_output=True,
        text=True,
        env=environment,
        timeout=30,
    )
    if executed.returncode != 0:
        raise RuntimeError(f"Parity harness failed: {executed.stderr}")
    return executed.stdout


def main() -> int:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    record_versions(EVIDENCE)
    baseline = subprocess.run(["git", "show", f"origin/main:{SOURCE}"], cwd=ROOT, capture_output=True, text=True)
    if baseline.returncode != 0:
        raise RuntimeError(f"Could not read the baseline reference: {baseline.stderr}")
    current = (ROOT / SOURCE).read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory(prefix="list-ops-parity-") as temporary:
        temp = Path(temporary)
        before_dir = temp / "before"
        before_dir.mkdir()
        before = run_harness(baseline.stdout, before_dir)
        after_dir = temp / "after"
        after_dir.mkdir()
        after = run_harness(current, after_dir)
    if before != after:
        raise RuntimeError("ListOps outputs differ from the baseline")
    (EVIDENCE / "parity-output.txt").write_text(before, encoding="utf-8")
    test_result = run_reference_tests("list-ops", EVIDENCE)
    print(
        f"{TASK}: baseline and refactored outputs match; {test_result['tests']} cases discovered, "
        f"{test_result['failures']} failures, {test_result['skipped']} skipped"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
