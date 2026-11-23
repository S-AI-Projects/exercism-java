"""Shared isolated reference-test runner for the coursework checks."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Callable, Sequence


ROOT = Path(__file__).resolve().parents[2]
LOCAL_JDKS = (Path("/opt/homebrew/opt/openjdk@21"), Path("/opt/homebrew/opt/openjdk"))


def java_environment() -> dict[str, str]:
    environment = dict(os.environ)
    local_jdk = next((candidate for candidate in LOCAL_JDKS if candidate.is_dir()), None)
    if local_jdk is not None and not environment.get("JAVA_HOME"):
        environment["JAVA_HOME"] = str(local_jdk)
        environment["PATH"] = str(local_jdk / "bin") + os.pathsep + environment.get("PATH", "")
    return environment


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_config(slug: str) -> tuple[Path, dict[str, Any]]:
    exercise = ROOT / "exercises" / "practice" / slug
    config_path = exercise / ".meta" / "config.json"
    if not config_path.is_file():
        raise RuntimeError(f"Missing exercise config: {config_path.relative_to(ROOT)}")
    config = json.loads(config_path.read_text(encoding="utf-8"))
    validate_files_config(exercise, config)
    return exercise, config


def validate_files_config(exercise: Path, config: dict[str, Any]) -> dict[str, list[Path]]:
    files = config.get("files")
    if not isinstance(files, dict):
        raise RuntimeError("config.json must contain a files object")
    resolved: dict[str, list[Path]] = {}
    for role, names in files.items():
        if not isinstance(names, list):
            raise RuntimeError(f"files.{role} must be an array")
        resolved[role] = []
        for name in names:
            if not isinstance(name, str):
                raise RuntimeError(f"files.{role} entries must be strings")
            candidate = (exercise / name).resolve()
            if not candidate.is_relative_to(exercise.resolve()):
                raise RuntimeError(f"files.{role} escapes the exercise: {name}")
            if not candidate.is_file():
                raise RuntimeError(f"files.{role} is missing: {name}")
            resolved[role].append(candidate)
    return resolved


def run_reference_tests(
    slug: str,
    evidence_dir: Path,
    *,
    mutation: Callable[[Path], None] | None = None,
    expected_failure: str | None = None,
    test_arguments: Sequence[str] = (),
) -> dict[str, Any]:
    """Copy an exercise including dotfiles, install its reference as solution, and run Gradle."""
    exercise, config = load_config(slug)
    learner_files = [exercise / name for name in config["files"].get("solution", [])]
    before = {str(path.relative_to(ROOT)): sha256(path) for path in learner_files}
    evidence_dir.mkdir(parents=True, exist_ok=True)
    started = time.time()
    with tempfile.TemporaryDirectory(prefix=f"sai-{slug}-") as temporary:
        scratch = Path(temporary) / slug
        shutil.copytree(exercise, scratch, ignore=shutil.ignore_patterns("build", ".gradle"))
        example_files = config["files"].get("example", [])
        solution_files = config["files"].get("solution", [])
        if len(example_files) != len(solution_files):
            raise RuntimeError("example and solution arrays must have the same length")
        for example_name, solution_name in zip(example_files, solution_files):
            source = scratch / example_name
            destination = scratch / solution_name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            if mutation is not None:
                mutation(destination)
        wrapper = scratch / "gradlew"
        if not wrapper.is_file():
            wrapper_source = ROOT / "exercises/practice/alphametics"
            shutil.copy2(wrapper_source / "gradlew", wrapper)
            shutil.copytree(wrapper_source / "gradle", scratch / "gradle")
        wrapper.chmod(wrapper.stat().st_mode | 0o111)
        try:
            process = subprocess.run(
                [str(wrapper), "test", "--no-daemon", "--console=plain", *test_arguments],
                cwd=scratch,
                capture_output=True,
                text=True,
                timeout=300,
                env=java_environment(),
            )
            exit_code = process.returncode
            stdout = process.stdout
            stderr = process.stderr
        except subprocess.TimeoutExpired as error:
            exit_code = -1
            stdout = error.stdout.decode(errors="replace") if isinstance(error.stdout, bytes) else (error.stdout or "")
            stderr = error.stderr.decode(errors="replace") if isinstance(error.stderr, bytes) else (error.stderr or "")
        test_count = failure_count = skipped_count = 0
        failed_cases: list[str] = []
        for report in (scratch / "build" / "test-results" / "test").glob("*.xml"):
            suite = ET.parse(report).getroot()
            test_count += int(suite.attrib.get("tests", 0))
            failure_count += int(suite.attrib.get("failures", 0)) + int(suite.attrib.get("errors", 0))
            skipped_count += int(suite.attrib.get("skipped", 0))
            for case in suite.findall("testcase"):
                failure = case.find("failure")
                if failure is None:
                    failure = case.find("error")
                if failure is not None:
                    failed_cases.append(case.attrib.get("name", "unknown"))
                    if failure.text:
                        failed_cases.append(failure.text)
        after = {str(path.relative_to(ROOT)): sha256(path) for path in learner_files}
        if before != after:
            raise RuntimeError("Learner source files changed while the isolated checker ran")
        result = {
            "exercise": slug,
            "exit_code": exit_code,
            "tests": test_count,
            "failures": failure_count,
            "skipped": skipped_count,
            "failed_cases": failed_cases,
            "elapsed_seconds": round(time.time() - started, 3),
            "learner_hashes_unchanged": True,
            "stdout_tail": stdout[-3000:],
            "stderr_tail": stderr[-3000:],
        }
    (evidence_dir / "reference-test-results.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    if expected_failure is not None:
        if result["exit_code"] == 0 or not any(expected_failure in case for case in result["failed_cases"]):
            raise RuntimeError(f"Expected test failure {expected_failure!r} did not occur")
    elif result["exit_code"] != 0 or result["tests"] == 0 or result["failures"] != 0:
        raise RuntimeError(f"Reference test run failed; see {evidence_dir / 'reference-test-results.json'}")
    return result


def record_versions(evidence_dir: Path) -> None:
    versions: dict[str, str] = {"python": subprocess.check_output(["python3", "--version"], text=True).strip()}
    for command, args in (("java", ["-version"]), ("git", ["--version"])):
        try:
            result = subprocess.run([command, *args], capture_output=True, text=True, timeout=10, env=java_environment())
            versions[command] = (result.stdout + result.stderr).strip().splitlines()[0]
        except (OSError, subprocess.SubprocessError, IndexError):
            versions[command] = "unavailable"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    (evidence_dir / "tool-versions.json").write_text(json.dumps(versions, indent=2) + "\n", encoding="utf-8")
