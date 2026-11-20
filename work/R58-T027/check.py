#!/usr/bin/env python3
"""Run the reference exercise tests and the documented Java micro-example."""

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXERCISE = ROOT / "exercises/practice/all-your-base"
EVIDENCE = Path(__file__).resolve().parent
EXPECTED_MICRO_OUTPUT = "0\nno digits to check"


def run(command, cwd, timeout=300, env=None):
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True, timeout=timeout, env=env)
    return {
        "command": command,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    # Homebrew's JDK is installed but may not be on a GUI-launched app's PATH.
    homebrew_jdk = Path("/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home")
    if homebrew_jdk.is_dir():
        os.environ["JAVA_HOME"] = str(homebrew_jdk)
        os.environ["PATH"] = str(homebrew_jdk / "bin") + os.pathsep + os.environ.get("PATH", "")
    config = json.loads((EXERCISE / ".meta/config.json").read_text())
    solution_paths = [EXERCISE / item for item in config["files"]["solution"]]
    example_paths = [EXERCISE / item for item in config["files"]["example"]]
    source_hashes = {str(path.relative_to(ROOT)): sha256(path) for path in solution_paths}

    results = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "java_version": run(["java", "-version"], ROOT),
        "javac_version": run(["javac", "-version"], ROOT),
        "python_version": run(["python3", "--version"], ROOT),
        "micro_example_expected": EXPECTED_MICRO_OUTPUT,
        "micro_example_inputs": {"digits": [1, 0, 1], "empty_digits": []},
    }
    if any(result["returncode"] != 0 for key, result in results.items() if key.endswith("version")):
        raise AssertionError("Could not read required tool versions")

    # Compile and run the documented snippet before the Gradle test attempt so
    # its evidence is retained even if the wrapper cannot fetch Gradle.
    with tempfile.TemporaryDirectory(prefix="r58-t027-micro-") as micro_temp:
        micro_dir = Path(micro_temp)
        micro_source = EVIDENCE / "micro_example/DigitMinimumExample.java"
        shutil.copy2(micro_source, micro_dir / micro_source.name)
        compiled = run(["javac", micro_source.name], micro_dir)
        results["micro_example_compile"] = compiled
        if compiled["returncode"] != 0:
            (EVIDENCE / "results.json").write_text(json.dumps(results, indent=2) + "\n")
            raise AssertionError("Micro-example did not compile")
        execution = run(["java", "DigitMinimumExample"], micro_dir)
        actual_output = execution["stdout"].strip()
        results["micro_example_run"] = execution
        results["micro_example_actual"] = actual_output
        if execution["returncode"] != 0 or actual_output != EXPECTED_MICRO_OUTPUT:
            (EVIDENCE / "results.json").write_text(json.dumps(results, indent=2) + "\n")
            raise AssertionError("Micro-example output did not match the hint")

    with tempfile.TemporaryDirectory(prefix="r58-t027-") as temporary:
        scratch = Path(temporary) / "all-your-base"
        shutil.copytree(EXERCISE, scratch, ignore=shutil.ignore_patterns("build", ".gradle"))
        for source, destination in zip(example_paths, solution_paths):
            target = scratch / destination.relative_to(EXERCISE)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)

        gradle = scratch / "gradlew"
        if not gradle.exists():
            raise AssertionError("Exercise Gradle wrapper is missing")
        gradle.chmod(gradle.stat().st_mode | 0o111)
        # Keep the wrapper's cache in the disposable scratch area. This avoids
        # writing to or relying on a user-level Gradle cache.
        gradle_home = scratch / ".gradle-user-home"
        gradle_env = os.environ.copy()
        gradle_env["GRADLE_USER_HOME"] = str(gradle_home)
        results["reference_tests"] = run(["./gradlew", "test", "--no-daemon"], scratch, env=gradle_env)
        xml_files = list((scratch / "build/test-results/test").glob("TEST-*.xml"))
        counts = {"tests": 0, "failures": 0, "errors": 0, "skipped": 0}
        for xml_file in xml_files:
            root = ET.parse(xml_file).getroot()
            for key in counts:
                counts[key] += int(root.attrib.get(key, 0))
        results["test_counts"] = counts
        if results["reference_tests"]["returncode"] != 0:
            (EVIDENCE / "results.json").write_text(json.dumps(results, indent=2) + "\n")
            raise AssertionError("Reference Gradle test run failed; see results.json")
        if not xml_files or counts["tests"] <= 0:
            raise AssertionError("Gradle run executed zero tests")
        if counts["failures"] or counts["errors"]:
            raise AssertionError("One or more reference tests failed")

    # Prove the task ran against a scratch copy and left the learner file intact.
    results["learner_source_hashes_before"] = source_hashes
    results["learner_source_hashes_after"] = {
        str(path.relative_to(ROOT)): sha256(path) for path in solution_paths
    }
    if results["learner_source_hashes_before"] != results["learner_source_hashes_after"]:
        raise AssertionError("Learner starter source changed during the check")

    (EVIDENCE / "results.json").write_text(json.dumps(results, indent=2) + "\n")
    print("Reference exercise tests: {tests} total, {failures} failed, {errors} errors, {skipped} skipped".format(**counts))
    print("Micro-example output asserted:")
    print(actual_output)
    print("Learner source unchanged: yes")


if __name__ == "__main__":
    main()
