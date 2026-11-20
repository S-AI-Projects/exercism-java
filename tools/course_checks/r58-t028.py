#!/usr/bin/env python3
"""Validate Exercism exercise file roles and paths in .meta/config.json."""

import json
import sys
import tempfile
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[2]
EXERCISE = ROOT / "exercises/practice/nucleotide-count"


class ConfigProblem(Exception):
    def __init__(self, code, detail):
        super().__init__(detail)
        self.code = code
        self.detail = detail


def validate(config_path, exercise_root):
    try:
        config = json.loads(Path(config_path).read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise ConfigProblem("invalid_config", str(error)) from error

    files = config.get("files")
    if not isinstance(files, dict):
        raise ConfigProblem("missing_files_object", "config must contain a files object")

    root = Path(exercise_root).resolve()
    checked = []
    for role, paths in files.items():
        if not isinstance(paths, list):
            raise ConfigProblem("invalid_role", f"files.{role} must be a list")
        for raw_path in paths:
            if not isinstance(raw_path, str) or not raw_path:
                raise ConfigProblem("invalid_path", f"files.{role} contains an empty or non-string path")
            relative = PurePosixPath(raw_path)
            if relative.is_absolute() or ".." in relative.parts:
                raise ConfigProblem("outside_exercise", f"files.{role} path escapes exercise: {raw_path}")
            resolved = (root / Path(*relative.parts)).resolve()
            try:
                resolved.relative_to(root)
            except ValueError as error:
                raise ConfigProblem("outside_exercise", f"files.{role} path escapes exercise: {raw_path}") from error
            if not resolved.is_file():
                raise ConfigProblem("missing_file", f"files.{role} path does not exist: {raw_path}")
            checked.append({"role": role, "path": raw_path})

    for required_role in ("solution", "test", "example"):
        if not files.get(required_role):
            raise ConfigProblem("missing_role", f"files.{required_role} must declare at least one file")
    return checked


def fixture_config(root, paths):
    for path in paths:
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("fixture\n")
    config_path = root / ".meta/config.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps({"files": {
        "solution": ["src/main/java/Solution.java"],
        "test": ["src/test/java/ExerciseTest.java"],
        "example": [".meta/src/reference/java/Example.java"],
    }}))
    return config_path


def run_fixtures():
    fixtures = [
        ("missing_reference", ["src/main/java/Solution.java", "src/test/java/ExerciseTest.java"],
         "missing_file", "files.example path does not exist"),
        ("missing_test", ["src/main/java/Solution.java", ".meta/src/reference/java/Example.java"],
         "missing_file", "files.test path does not exist"),
        ("outside_exercise", ["src/main/java/Solution.java", "src/test/java/ExerciseTest.java",
                              ".meta/src/reference/java/Example.java"], "outside_exercise",
         "files.example path escapes exercise"),
    ]
    outcomes = []
    for name, existing_paths, expected_code, expected_detail in fixtures:
        with tempfile.TemporaryDirectory(prefix=f"r58-t028-{name}-") as temporary:
            root = Path(temporary) / "exercise"
            root.mkdir()
            config_path = fixture_config(root, existing_paths)
            config = json.loads(config_path.read_text())
            if name == "outside_exercise":
                config["files"]["example"] = ["../../outside/Example.java"]
                config_path.write_text(json.dumps(config))
            actual = None
            try:
                validate(config_path, root)
            except ConfigProblem as error:
                actual = {"code": error.code, "detail": error.detail}
            if actual is None or actual["code"] != expected_code or expected_detail not in actual["detail"]:
                raise AssertionError(f"Fixture {name} did not fail for the intended reason: {actual}")
            outcomes.append({"name": name, "expected_code": expected_code, "actual": actual,
                             "passed": True})
    return outcomes


def main():
    checked = validate(EXERCISE / ".meta/config.json", EXERCISE)
    fixture_results = run_fixtures()
    print(json.dumps({"real_config": {"passed": True, "checked_files": checked,
                                       "editor_role_declared": "editor" in json.loads((EXERCISE / ".meta/config.json").read_text())["files"]},
                      "fixtures": fixture_results}, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (ConfigProblem, AssertionError) as error:
        print(json.dumps({"passed": False, "error": str(error)}), file=sys.stderr)
        sys.exit(1)
