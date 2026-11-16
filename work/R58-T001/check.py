
import json
import shutil
import subprocess
import sys
import tempfile
import tomllib
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXERCISE = ROOT / "exercises/practice/simple-cipher"
CONFIG = EXERCISE / ".meta/config.json"
TESTS_TOML = EXERCISE / ".meta/tests.toml"
EVIDENCE = ROOT / "work/R58-T001"


def run_command(command, cwd):
    return subprocess.run(
        command,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )


def count_cases(data):
    entries = [
        value for value in data.values()
        if isinstance(value, dict) and "description" in value
    ]
    excluded = sum(
        1 for entry in entries if entry.get("include", True) is False
    )
    return {
        "total": len(entries),
        "included": len(entries) - excluded,
        "excluded": excluded
    }


def main():
    EVIDENCE.mkdir(parents=True, exist_ok=True)

    with CONFIG.open("r", encoding="utf-8") as file:
        config = json.load(file)

    solutions = config["files"]["solution"]
    tests = config["files"]["test"]
    examples = config["files"]["example"]

    if len(solutions) != len(examples):
        raise ValueError("Solution and example paths do not match.")

    # Read current canonical-case counts.
    with TESTS_TOML.open("rb") as file:
        current_data = tomllib.load(file)

    current_counts = count_cases(current_data)

    # Read the original counts from the current Git commit.
    original = run_command(
        ["git", "show", "HEAD:exercises/practice/simple-cipher/.meta/tests.toml"],
        ROOT
    )

    if original.returncode != 0:
        raise RuntimeError("Could not read the original tests.toml from Git.")

    before_counts = count_cases(tomllib.loads(original.stdout))

    # Record tool versions.
    python_version = sys.version
    java_version = run_command(["java", "-version"], ROOT)
    gradle_version = run_command(["./gradlew", "--version"], EXERCISE)

    versions = (
        f"Python:\n{python_version}\n"
        f"Java:\n{java_version.stdout}\n"
        f"Gradle:\n{gradle_version.stdout}\n"
    )
    (EVIDENCE / "tool-versions.txt").write_text(
        versions, encoding="utf-8"
    )

    # Copy the complete exercise, including hidden files, to a temporary folder.
    with tempfile.TemporaryDirectory(prefix="simple-cipher-check-") as temp:
        scratch = Path(temp) / "simple-cipher"
        shutil.copytree(EXERCISE, scratch)

        # Replace learner solution only in the temporary copy.
        for solution, example in zip(solutions, examples):
            source = scratch / example
            destination = scratch / solution
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)

        # Confirm configured test files exist in the temporary copy.
        for test_file in tests:
            if not (scratch / test_file).is_file():
                raise FileNotFoundError(f"Missing test file: {test_file}")

        result = run_command(["./gradlew", "test"], scratch)

        (EVIDENCE / "gradle-test-output.txt").write_text(
            result.stdout, encoding="utf-8"
        )

        # Read JUnit XML reports to count tests.
        report_files = list(
            (scratch / "build/test-results/test").glob("TEST-*.xml")
        )

        total = skipped = failures = errors = 0

        for report in report_files:
            root = ET.parse(report).getroot()
            for suite in root.iter("testsuite"):
                total += int(suite.attrib.get("tests", 0))
                skipped += int(suite.attrib.get("skipped", 0))
                failures += int(suite.attrib.get("failures", 0))
                errors += int(suite.attrib.get("errors", 0))

        executed = total - skipped

        checks = {
            "gradle_exit_code_is_zero": result.returncode == 0,
            "at_least_one_test_executed": executed > 0,
            "no_test_failures": failures == 0 and errors == 0,
            "test_reports_found": len(report_files) > 0
        }

        report = {
            "exercise": "simple-cipher",
            "configured_paths": config["files"],
            "canonical_cases_before": before_counts,
            "canonical_cases_after": current_counts,
            "test_results": {
                "total": total,
                "skipped": skipped,
                "executed": executed,
                "failures": failures,
                "errors": errors
            },
            "checks": checks,
            "gradle_exit_code": result.returncode
        }

        (EVIDENCE / "check-results.json").write_text(
            json.dumps(report, indent=2), encoding="utf-8"
        )

        print(json.dumps(report, indent=2))

        if not all(checks.values()):
            raise SystemExit("CHECK FAILED: inspect the evidence files.")

    print("CHECK PASSED: reference solution tests completed.")


if __name__ == "__main__":
    main()
