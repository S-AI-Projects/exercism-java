#!/usr/bin/env python3
"""Run intergalactic-transmission tests against an isolated reference copy."""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXERCISE = ROOT / "exercises/practice/intergalactic-transmission"
VARIANTS = ("reference", "failing", "empty", "interrupt")
FAILING_REFERENCE = '''import java.util.List;

public class IntergalacticTransmission {
    public static List<Integer> getTransmitSequence(List<Integer> message) {
        return List.of(1); // Deliberately wrong: even an empty message yields data.
    }

    public static List<Integer> decodeSequence(List<Integer> receivedSequence) {
        return List.of(1);
    }
}
'''
EMPTY_TEST_SOURCE = '''public class IntergalacticTransmissionTest {
    // Deliberately no @Test methods: this verifies zero-test detection.
}
'''


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def is_within(path, root):
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def invoke(command, cwd, timeout=300, env=None):
    try:
        completed = subprocess.run(command, cwd=cwd, text=True, capture_output=True,
                                   timeout=timeout, env=env)
        return {"command": command, "returncode": completed.returncode,
                "stdout": completed.stdout, "stderr": completed.stderr,
                "timed_out": False}
    except subprocess.TimeoutExpired as error:
        return {"command": command, "returncode": 124,
                "stdout": error.stdout or "", "stderr": error.stderr or "",
                "timed_out": True}


def read_test_counts(test_results_dir):
    totals = {"tests": 0, "failures": 0, "errors": 0, "skipped": 0}
    report_paths = sorted(test_results_dir.glob("TEST-*.xml"))
    for report_path in report_paths:
        suite = ET.parse(report_path).getroot()
        for key in totals:
            totals[key] += int(suite.attrib.get(key, 0))
    totals["executed"] = totals["tests"] - totals["skipped"]
    return totals, len(report_paths)


def run_variant(variant):
    config_path = EXERCISE / ".meta/config.json"
    config = json.loads(config_path.read_text())
    role_paths = config["files"]
    solution_paths = [EXERCISE / value for value in role_paths["solution"]]
    test_paths = [EXERCISE / value for value in role_paths["test"]]
    example_paths = [EXERCISE / value for value in role_paths["example"]]
    if not solution_paths or not test_paths or not example_paths:
        raise ValueError("config.json must declare solution, test, and example paths")
    if len(solution_paths) != len(example_paths):
        raise ValueError("solution and example path lists must have the same length")
    for declared_path in solution_paths + test_paths + example_paths:
        if not declared_path.is_file() or not is_within(declared_path, EXERCISE):
            raise ValueError(f"invalid or missing configured exercise path: {declared_path}")

    hashes_before = {str(path.relative_to(ROOT)): digest(path) for path in solution_paths}
    expectations = {
        "reference": {"runner_returncode": 0, "minimum_executed": 1},
        "failing": {"runner_returncode": "nonzero", "gradle_returncode": "nonzero",
                    "minimum_failures": 1},
        "empty": {"runner_returncode": "nonzero", "gradle_returncode": 0,
                  "executed": 0},
        "interrupt": {"runner_returncode": 130, "scratch_cleaned": True},
    }
    report = {"variant": variant, "config": role_paths, "expected": expectations[variant],
              "learner_hashes_before": hashes_before, "test_counts": None,
              "gradle": None, "runner_error": None, "interrupted": False,
              "scratch_cleaned": False}
    scratch_path = None
    try:
        with tempfile.TemporaryDirectory(prefix=f"r58-t029-{variant}-") as temporary:
            scratch = Path(temporary) / "intergalactic-transmission"
            scratch_path = scratch
            shutil.copytree(EXERCISE, scratch, ignore=shutil.ignore_patterns("build", ".gradle"))

            for example, solution in zip(example_paths, solution_paths):
                destination = scratch / solution.relative_to(EXERCISE)
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(example, destination)

            if variant == "failing":
                (scratch / solution_paths[0].relative_to(EXERCISE)).write_text(FAILING_REFERENCE)
            elif variant == "empty":
                (scratch / test_paths[0].relative_to(EXERCISE)).write_text(EMPTY_TEST_SOURCE)
            elif variant == "interrupt":
                # Exercise cleanup and hash verification when a run is interrupted.
                raise KeyboardInterrupt

            wrapper = scratch / "gradlew"
            if not wrapper.is_file():
                raise FileNotFoundError("configured exercise copy has no gradlew")
            wrapper.chmod(wrapper.stat().st_mode | 0o111)
            gradle_env = os.environ.copy()
            # Use Gradle's normal user cache so its distribution and dependency
            # caches can be reused across the four scenarios.
            report["gradle"] = invoke(["./gradlew", "test"], scratch, env=gradle_env)
            report["test_counts"], report["test_report_files"] = read_test_counts(
                scratch / "build/test-results/test")
    except KeyboardInterrupt:
        report["interrupted"] = True
        report["runner_error"] = "simulated KeyboardInterrupt after scratch copy"
    except Exception as error:
        report["runner_error"] = f"{type(error).__name__}: {error}"
    finally:
        report["learner_hashes_after"] = {
            str(path.relative_to(ROOT)): digest(path) for path in solution_paths
        }
        report["learner_hashes_match"] = report["learner_hashes_before"] == report["learner_hashes_after"]
        report["scratch_cleaned"] = scratch_path is not None and not scratch_path.exists()

    if not report["learner_hashes_match"]:
        report["runner_error"] = "learner solution hash changed"
        runner_exit = 1
    elif report["runner_error"] and not report["interrupted"]:
        runner_exit = 1
    elif report["interrupted"]:
        runner_exit = 130
    else:
        gradle_rc = report["gradle"]["returncode"]
        counts = report["test_counts"]
        if variant == "empty" and counts["executed"] == 0:
            report["runner_error"] = "zero tests executed"
            runner_exit = 1
        elif counts["executed"] == 0:
            report["runner_error"] = "zero tests executed"
            runner_exit = 1
        elif gradle_rc != 0:
            # Propagate the child status to the caller.
            runner_exit = gradle_rc if gradle_rc > 0 else 1
        elif counts["failures"] or counts["errors"]:
            runner_exit = 1
        else:
            runner_exit = 0
    report["runner_returncode"] = runner_exit
    report["actual"] = {"runner_returncode": runner_exit,
                        "gradle_returncode": report["gradle"]["returncode"] if report["gradle"] else None,
                        "test_counts": report["test_counts"],
                        "learner_hashes_match": report["learner_hashes_match"],
                        "scratch_cleaned": report["scratch_cleaned"]}
    return report, runner_exit


def main():
    homebrew_jdk = Path("/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home")
    if homebrew_jdk.is_dir():
        os.environ["JAVA_HOME"] = str(homebrew_jdk)
        os.environ["PATH"] = str(homebrew_jdk / "bin") + os.pathsep + os.environ.get("PATH", "")

    parser = argparse.ArgumentParser()
    parser.add_argument("--variant", choices=VARIANTS, default="reference")
    args = parser.parse_args()
    report, exit_code = run_variant(args.variant)
    print(json.dumps(report, indent=2))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
