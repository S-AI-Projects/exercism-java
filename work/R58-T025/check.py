#!/usr/bin/env python3
"""
Verification check and complexity study harness for Task R58-T025 (Forth).

Requirements:
1. Use Python subprocess and tempfile.
2. Read exercises/practice/forth/.meta/config.json.
3. Resolve solution, test and reference paths dynamically.
4. Copy the complete exercise, including hidden files and folders, into a temporary directory.
5. Substitute the maintained reference implementation into scratch src/main/java only.
6. Run ./gradlew test inside the temporary copy.
7. Check child process return code.
8. Parse test results and report executed, passed, skipped, and failed tests.
9. Fail if zero tests execute.
10. Fail if any test fails or Gradle exits unsuccessfully.
11. Verify that the original learner solution remains unchanged.
12. Do not rewrite the working repository during verification.
13. Execute benchmark runs across 3 valid input sizes (5 repetitions each), record median timings.
14. Save inputs, expected vs actual results, tool versions, test results, and benchmark data.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import tomllib
import xml.etree.ElementTree as ET

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
WORK_DIR = os.path.join(REPO_ROOT, "work", "R58-T025")
EXERCISE_DIR = os.path.join(REPO_ROOT, "exercises", "practice", "forth")

BENCHMARK_SIZES = [99, 999, 4999]
BENCHMARK_REPETITIONS = 5


def get_env():
    env = os.environ.copy()
    jdk = "/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home"
    if os.path.exists(jdk):
        env["JAVA_HOME"] = jdk
        env["PATH"] = f"/opt/homebrew/opt/openjdk@21/bin:{env.get('PATH', '')}"
    return env


def get_tool_versions(env):
    versions = {"python": sys.version.split()[0]}
    try:
        proc = subprocess.run(["java", "-version"], env=env, capture_output=True, text=True)
        versions["java"] = (proc.stderr or proc.stdout).splitlines()[0].strip()
    except Exception as e:
        versions["java"] = f"unknown: {e}"
    try:
        proc = subprocess.run(
            ["./gradlew", "--version"],
            cwd=EXERCISE_DIR,
            env=env,
            capture_output=True,
            text=True,
        )
        for line in proc.stdout.splitlines():
            if line.startswith("Gradle "):
                versions["gradle"] = line.strip()
                break
    except Exception as e:
        versions["gradle"] = f"unknown: {e}"
    return versions


def run_benchmark(scratch_dir, env):
    """Compiles and executes benchmark harness in scratch directory."""
    benchmark_source = """
import java.util.*;

public class ForthBenchmark {
    public static void main(String[] args) {
        int[] sizes = {99, 999, 4999};
        int runs = 5;

        // JVM Warm-up (200 iterations)
        for (int i = 0; i < 200; i++) {
            ForthEvaluator warmup = new ForthEvaluator();
            warmup.evaluateProgram(Collections.singletonList("1 1 + 1 + 1 +"));
        }

        System.out.println("JSON_START");
        System.out.print("[");
        boolean firstSize = true;

        for (int size : sizes) {
            StringBuilder sb = new StringBuilder("1");
            int pairs = (size - 1) / 2;
            int actualTokens = 1 + pairs * 2;
            for (int i = 0; i < pairs; i++) {
                sb.append(" 1 +");
            }
            List<String> program = Collections.singletonList(sb.toString());

            // Correctness assertion
            ForthEvaluator checker = new ForthEvaluator();
            List<Integer> expected = checker.evaluateProgram(program);
            int expectedValue = pairs + 1;
            if (expected.size() != 1 || expected.get(0) != expectedValue) {
                throw new AssertionError("Correctness check failed! Got: " + expected);
            }

            long[] times = new long[runs];
            for (int r = 0; r < runs; r++) {
                ForthEvaluator eval = new ForthEvaluator();
                long start = System.nanoTime();
                eval.evaluateProgram(program);
                long elapsed = System.nanoTime() - start;
                times[r] = elapsed;
            }

            Arrays.sort(times);
            long medianNs = times[runs / 2];
            double medianMs = medianNs / 1_000_000.0;

            if (!firstSize) System.out.print(",");
            firstSize = false;

            System.out.printf("{\\"size\\": %d, \\"median_ms\\": %.4f, \\"expected_value\\": %d, \\"times_ms\\": [",
                    actualTokens, medianMs, expectedValue);
            for (int r = 0; r < runs; r++) {
                if (r > 0) System.out.print(", ");
                System.out.printf("%.4f", times[r] / 1_000_000.0);
            }
            System.out.print("]}");
        }
        System.out.println("]");
        System.out.println("JSON_END");
    }
}
"""
    bench_file = os.path.join(scratch_dir, "src", "main", "java", "ForthBenchmark.java")
    with open(bench_file, "w") as f:
        f.write(benchmark_source)

    bin_dir = os.path.join(scratch_dir, "bench_bin")
    os.makedirs(bin_dir, exist_ok=True)

    compile_cmd = [
        "javac", "-d", bin_dir,
        os.path.join(scratch_dir, "src", "main", "java", "Token.java"),
        os.path.join(scratch_dir, "src", "main", "java", "ForthEvaluator.java"),
        bench_file,
    ]
    subprocess.run(compile_cmd, env=env, check=True, capture_output=True)

    run_proc = subprocess.run(
        ["java", "-cp", bin_dir, "ForthBenchmark"],
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )

    out = run_proc.stdout
    json_str = out[out.find("JSON_START") + len("JSON_START"):out.find("JSON_END")].strip()
    return json.loads(json_str)


def main():
    os.makedirs(WORK_DIR, exist_ok=True)
    env = get_env()
    tool_versions = get_tool_versions(env)

    print("=== Step 1: Resolving paths from config.json ===")
    config_file = os.path.join(EXERCISE_DIR, ".meta", "config.json")
    with open(config_file, "r") as f:
        config = json.load(f)

    solution_rel = config["files"]["solution"][0]
    test_rel = config["files"]["test"][0]
    example_rels = config["files"]["example"]

    print(f"  solution: {solution_rel}")
    print(f"  test:     {test_rel}")
    print(f"  examples: {example_rels}")

    print("\n=== Step 2: Validating tests.toml ===")
    tests_toml_file = os.path.join(EXERCISE_DIR, ".meta", "tests.toml")
    with open(tests_toml_file, "rb") as f:
        toml_data = tomllib.load(f)

    total_canonical = len(toml_data)
    included = sum(1 for v in toml_data.values() if v.get("include", True) is not False)
    excluded = total_canonical - included
    print(f"  Total canonical entries: {total_canonical}")
    print(f"  Included: {included}, Excluded: {excluded}")

    print("\n=== Step 3: Verifying learner stub remains unsolved ===")
    learner_stub_path = os.path.join(EXERCISE_DIR, solution_rel)
    with open(learner_stub_path, "r") as f:
        stub_content = f.read()
    assert "UnsupportedOperationException" in stub_content, "Learner stub must remain unsolved!"
    print("  Confirmed: learner stub throws UnsupportedOperationException.")

    print("\n=== Step 4: Verifying reference complexity and invariant comment ===")
    ref_evaluator_path = os.path.join(EXERCISE_DIR, ".meta", "src", "reference", "java", "ForthEvaluator.java")
    with open(ref_evaluator_path, "r") as f:
        ref_code = f.read()
    assert "Complexity and Invariant Analysis for ForthEvaluator" in ref_code, (
        "Reference implementation must contain complexity and invariant comment!"
    )
    assert "O(N^2)" in ref_code, "Reference comment must explain O(N^2) time complexity!"
    print("  Confirmed: reference implementation contains complexity & invariant comment.")

    results = {
        "status": "RUNNING",
        "tool_versions": tool_versions,
        "inputs": {
            "exercise": "exercises/practice/forth",
            "benchmark_sizes": BENCHMARK_SIZES,
            "benchmark_repetitions": BENCHMARK_REPETITIONS,
        },
        "checks": {},
    }

    print("\n=== Step 5: Testing reference in isolated temporary directory ===")
    with tempfile.TemporaryDirectory() as temp_dir:
        scratch_exercise = os.path.join(temp_dir, "forth")
        shutil.copytree(EXERCISE_DIR, scratch_exercise)

        # Substitute reference implementation files into src/main/java
        dest_dir = os.path.join(scratch_exercise, "src", "main", "java")
        for ref_rel in example_rels:
            src_file = os.path.join(scratch_exercise, ref_rel)
            shutil.copy2(src_file, os.path.join(dest_dir, os.path.basename(ref_rel)))

        # Enable all disabled tests in scratch copy only
        scratch_test = os.path.join(scratch_exercise, test_rel)
        with open(scratch_test, "r") as f:
            test_content = f.read()
        import re
        test_content_enabled = re.sub(r"@Disabled(\([^)]*\))?", "", test_content)
        with open(scratch_test, "w") as f:
            f.write(test_content_enabled)

        # Run gradlew test
        proc = subprocess.run(
            ["./gradlew", "test"],
            cwd=scratch_exercise,
            env=env,
            capture_output=True,
            text=True,
        )

        print(f"  Gradle exit code: {proc.returncode}")
        if proc.returncode != 0:
            print("STDERR:\n", proc.stderr)
            print("STDOUT:\n", proc.stdout)
            sys.exit(proc.returncode)

        # Parse test results from XML
        xml_file = os.path.join(
            scratch_exercise, "build", "test-results", "test", "TEST-ForthEvaluatorTest.xml"
        )
        assert os.path.isfile(xml_file), f"Test XML report not found at {xml_file}"

        tree = ET.parse(xml_file)
        root = tree.getroot()

        tests_total = int(root.attrib.get("tests", 0))
        tests_skipped = int(root.attrib.get("skipped", 0))
        tests_failures = int(root.attrib.get("failures", 0))
        tests_errors = int(root.attrib.get("errors", 0))
        tests_passed = tests_total - tests_skipped - tests_failures - tests_errors

        print(f"  Executed Tests: {tests_total}")
        print(f"  Passed:   {tests_passed}")
        print(f"  Skipped:  {tests_skipped}")
        print(f"  Failures: {tests_failures}")
        print(f"  Errors:   {tests_errors}")

        assert tests_total > 0, "Test count must be greater than zero!"
        assert tests_failures == 0, f"Found {tests_failures} test failures!"
        assert tests_errors == 0, f"Found {tests_errors} test errors!"

        results["checks"]["test_execution"] = {
            "exit_code": proc.returncode,
            "tests_total": tests_total,
            "tests_passed": tests_passed,
            "tests_skipped": tests_skipped,
            "tests_failures": tests_failures,
            "tests_errors": tests_errors,
        }

        print("\n=== Step 6: Running empirical benchmark on variable-size inputs ===")
        benchmark_results = run_benchmark(scratch_exercise, env)
        print("  Benchmark measurements:")
        for entry in benchmark_results:
            print(f"    Size: {entry['size']:4d} tokens | Median: {entry['median_ms']:.4f} ms | Repetitions: {entry['times_ms']}")

        results["checks"]["benchmarks"] = benchmark_results

    # Verify working tree was not rewritten
    with open(learner_stub_path, "r") as f:
        after_stub = f.read()
    assert after_stub == stub_content, "Working tree starter file was modified!"
    print("\n  Working tree integrity verified: untouched.")

    results["status"] = "PASSED"
    results_file = os.path.join(WORK_DIR, "results.json")
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nAll assertions passed! Saved evidence to {results_file}")
    sys.exit(0)


if __name__ == "__main__":
    main()
