#!/usr/bin/env python3
"""Compare the crypto-square reference and an independent direct-index approach."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from common import java_environment, record_versions, run_reference_tests  # noqa: E402

TASK = "R58-T036"
EVIDENCE = ROOT / "work" / TASK
HARNESS = r'''public class CryptoSquareComparison {
    private static void check(String input, String expected) {
        String reference = new CryptoSquare(input).getCiphertext();
        String alternative = AlternativeCryptoSquare.encode(input);
        if (!expected.equals(reference) || !expected.equals(alternative)) {
            throw new AssertionError("Input=" + input + "; expected=" + expected
                    + "; reference=" + reference + "; alternative=" + alternative);
        }
        System.out.println("PASS " + input.length() + " chars -> " + expected.length() + " chars");
    }

    public static void main(String[] args) {
        check("", "");
        check("... --- ...", "");
        check("A", "a");
        check(" b ", "b");
        check("@1,%!", "1");
        check("This is fun!", "tsf hiu isn");
        check("Chill out.", "clu hlt io ");
        check("If man was meant to stay on the ground, god would have given us roots.",
                "imtgdvs fearwer mayoogo anouuio ntnnlvt wttddes aohghn  sseoau ");
    }
}'''


def main() -> int:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    record_versions(EVIDENCE)
    test_result = run_reference_tests("crypto-square", EVIDENCE)
    reference = ROOT / "exercises/practice/crypto-square/.meta/src/reference/java/CryptoSquare.java"
    alternative = ROOT / "work/R58-T036/AlternativeCryptoSquare.java"
    with tempfile.TemporaryDirectory(prefix="crypto-square-compare-") as temporary:
        directory = Path(temporary)
        harness = directory / "CryptoSquareComparison.java"
        harness.write_text(HARNESS + "\n", encoding="utf-8")
        compiled = subprocess.run(
            ["javac", "-d", str(directory), str(reference), str(alternative), str(harness)],
            capture_output=True,
            text=True,
            timeout=60,
            env=java_environment(),
        )
        if compiled.returncode != 0:
            raise RuntimeError(f"Comparison harness did not compile: {compiled.stderr}")
        result = subprocess.run(
            ["java", "-cp", str(directory), "CryptoSquareComparison"],
            capture_output=True,
            text=True,
            timeout=30,
            env=java_environment(),
        )
        if result.returncode != 0:
            raise RuntimeError(f"Approach comparison failed: {result.stderr}")
    if result.stdout.count("PASS ") != 8:
        raise RuntimeError("Expected both approaches to pass all eight contract examples")
    (EVIDENCE / "comparison-results.txt").write_text(result.stdout, encoding="utf-8")
    print(
        f"{TASK}: both approaches passed 8 examples; reference suite: {test_result['tests']} cases "
        f"discovered, {test_result['failures']} failures, {test_result['skipped']} skipped"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
