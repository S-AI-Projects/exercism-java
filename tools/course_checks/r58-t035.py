#!/usr/bin/env python3
"""Run strain reference tests and measure keep over three valid list sizes."""

from __future__ import annotations

import csv
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from common import java_environment, record_versions, run_reference_tests  # noqa: E402

TASK = "R58-T035"
EVIDENCE = ROOT / "work" / TASK
HARNESS = r'''import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class StrainScaling {
    public static void main(String[] args) {
        int[] sizes = {1000, 10000, 100000};
        for (int size : sizes) {
            List<Integer> input = new ArrayList<>(size);
            for (int i = 0; i < size; i++) input.add(i);
            int expectedKept = (size + 1) / 2;
            List<Integer> correctness = Strain.keep(input, value -> value % 2 == 0);
            if (correctness.size() != expectedKept || correctness.get(0) != 0
                    || correctness.get(correctness.size() - 1) != size - 1 - (size % 2 == 0 ? 1 : 0)) {
                throw new AssertionError("Incorrect keep output for size " + size);
            }
            long[] timings = new long[5];
            int predicateCalls = 0;
            for (int run = 0; run < timings.length; run++) {
                int[] calls = {0};
                long started = System.nanoTime();
                List<Integer> actual = Strain.keep(input, value -> {
                    calls[0]++;
                    return value % 2 == 0;
                });
                timings[run] = System.nanoTime() - started;
                if (actual.size() != expectedKept || actual.get(0) != 0
                        || actual.get(actual.size() - 1) != size - 1 - (size % 2 == 0 ? 1 : 0)) {
                    throw new AssertionError("Incorrect timed output for size " + size);
                }
                if (calls[0] != size) throw new AssertionError("Expected " + size + " predicate calls, got " + calls[0]);
                predicateCalls = calls[0];
            }
            java.util.Arrays.sort(timings);
            System.out.println(size + "," + predicateCalls + "," + expectedKept + "," + timings[2]);
        }
    }
}'''


def main() -> int:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    record_versions(EVIDENCE)
    test_result = run_reference_tests("strain", EVIDENCE)
    with tempfile.TemporaryDirectory(prefix="strain-scaling-") as temporary:
        directory = Path(temporary)
        reference = ROOT / "exercises/practice/strain/.meta/src/reference/java/Strain.java"
        harness = directory / "StrainScaling.java"
        harness.write_text(HARNESS + "\n", encoding="utf-8")
        compiled = subprocess.run(
            ["javac", "-d", str(directory), str(reference), str(harness)],
            capture_output=True,
            text=True,
            timeout=60,
            env=java_environment(),
        )
        if compiled.returncode != 0:
            raise RuntimeError(f"Could not compile scaling harness: {compiled.stderr}")
        measured = subprocess.run(
            ["java", "-cp", str(directory), "StrainScaling"],
            capture_output=True,
            text=True,
            timeout=60,
            env=java_environment(),
        )
        if measured.returncode != 0:
            raise RuntimeError(f"Scaling harness failed: {measured.stderr}")
    rows = list(csv.reader(measured.stdout.splitlines()))
    expected_sizes = (1000, 10000, 100000)
    if len(rows) != len(expected_sizes):
        raise RuntimeError(f"Expected {len(expected_sizes)} measurements, got {len(rows)}")
    for row, size in zip(rows, expected_sizes):
        if [int(row[0]), int(row[1]), int(row[2])] != [size, size, (size + 1) // 2] or int(row[3]) <= 0:
            raise RuntimeError(f"Unexpected measurement row: {row}")
    output = EVIDENCE / "benchmark.csv"
    with output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(("input_size", "predicate_calls", "kept_values", "median_nanoseconds"))
        writer.writerows(rows)
    print(
        f"{TASK}: {test_result['tests']} cases discovered, {test_result['failures']} failures, "
        f"{test_result['skipped']} skipped; measured {len(rows)} valid sizes"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
