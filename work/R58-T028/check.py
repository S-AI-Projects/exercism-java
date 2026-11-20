#!/usr/bin/env python3
"""Validate nucleotide-count metadata and test the maintained reference."""

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
EXERCISE = ROOT / "exercises/practice/nucleotide-count"
EVIDENCE = Path(__file__).resolve().parent
PATH_CHECK = ROOT / "tools/course_checks/r58-t028.py"


def run(command, cwd, timeout=300, env=None):
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True,
                            timeout=timeout, env=env)
    return {"command": command, "returncode": result.returncode,
            "stdout": result.stdout, "stderr": result.stderr}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(results):
    (EVIDENCE / "results.json").write_text(json.dumps(results, indent=2) + "\n")


def main():
    # Prefer the installed Homebrew JDK when the desktop app PATH omits it.
    homebrew_jdk = Path("/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home")
    if homebrew_jdk.is_dir():
        os.environ["JAVA_HOME"] = str(homebrew_jdk)
        os.environ["PATH"] = str(homebrew_jdk / "bin") + os.pathsep + os.environ.get("PATH", "")

    config_path = EXERCISE / ".meta/config.json"
    config = json.loads(config_path.read_text())
    roles = config["files"]
    solutions = [EXERCISE / path for path in roles["solution"]]
    tests = [EXERCISE / path for path in roles["test"]]
    examples = [EXERCISE / path for path in roles["example"]]
    if not solutions or not tests or not examples:
        raise AssertionError("solution, test, and example roles must each have a path")
    before_hashes = {str(path.relative_to(ROOT)): sha256(path) for path in solutions}

    results = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "inputs": {"config_path": str(config_path.relative_to(ROOT)),
                   "files": roles, "reference_paths": [str(path.relative_to(ROOT)) for path in examples]},
        "expected": {"real_config": "all declared role paths exist inside the exercise",
                     "fixtures": ["missing reference rejected", "missing test rejected",
                                  "outside-exercise traversal rejected"],
                     "gradle": "return code 0 and at least one test reported"},
        "java_version": run(["java", "-version"], ROOT),
        "javac_version": run(["javac", "-version"], ROOT),
        "python_version": run(["python3", "--version"], ROOT),
    }
    save(results)
    if any(value["returncode"] != 0 for key, value in results.items() if key.endswith("version")):
        raise AssertionError("Unable to read required tool versions")

    path_result = run(["python3", str(PATH_CHECK)], ROOT)
    results["path_checker"] = path_result
    if path_result["returncode"] != 0:
        save(results)
        raise AssertionError("Path/configuration checker failed")
    path_report = json.loads(path_result["stdout"])
    results["path_report"] = path_report
    if not path_report["real_config"]["passed"] or len(path_report["fixtures"]) != 3 or not all(
            fixture["passed"] for fixture in path_report["fixtures"]):
        save(results)
        raise AssertionError("Real config or one of the three negative fixtures did not pass")

    with tempfile.TemporaryDirectory(prefix="r58-t028-exercise-") as temporary:
        scratch = Path(temporary) / "nucleotide-count"
        shutil.copytree(EXERCISE, scratch, ignore=shutil.ignore_patterns("build", ".gradle"))
        for reference, solution in zip(examples, solutions):
            target = scratch / solution.relative_to(EXERCISE)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(reference, target)

        wrapper = scratch / "gradlew"
        if not wrapper.is_file():
            save(results)
            raise AssertionError("Exercise Gradle wrapper is missing")
        wrapper.chmod(wrapper.stat().st_mode | 0o111)
        gradle_env = os.environ.copy()
        gradle_env["GRADLE_USER_HOME"] = str(Path(tempfile.gettempdir()) / "r58-t028-gradle-cache")
        gradle = run(["./gradlew", "test", "--no-daemon"], scratch, env=gradle_env)
        results["reference_gradle"] = gradle
        report_files = list((scratch / "build/test-results/test").glob("TEST-*.xml"))
        counts = {"tests": 0, "failures": 0, "errors": 0, "skipped": 0}
        for report in report_files:
            suite = ET.parse(report).getroot()
            for key in counts:
                counts[key] += int(suite.attrib.get(key, 0))
        results["test_counts"] = counts
        save(results)
        if gradle["returncode"] != 0:
            raise AssertionError("Gradle test run exited non-zero")
        if not report_files or counts["tests"] == 0:
            raise AssertionError("Gradle test run reported zero tests")
        if counts["failures"] or counts["errors"]:
            raise AssertionError("Gradle test report contains failures or errors")

    results["learner_solution_hashes_before"] = before_hashes
    results["learner_solution_hashes_after"] = {
        str(path.relative_to(ROOT)): sha256(path) for path in solutions
    }
    if results["learner_solution_hashes_before"] != results["learner_solution_hashes_after"]:
        save(results)
        raise AssertionError("Learner solution changed during scratch verification")
    results["actual"] = {"learner_solution_unchanged": True,
                         "gradle_returncode": results["reference_gradle"]["returncode"],
                         "tests": counts}
    save(results)
    print("Path fixtures: real config passed; 3 invalid fixtures rejected as expected")
    print("Reference tests: {tests} reported, {failures} failed, {errors} errors, {skipped} skipped".format(**counts))
    print("Learner solution unchanged: yes")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"R58-T028 check failed: {error}")
        raise
