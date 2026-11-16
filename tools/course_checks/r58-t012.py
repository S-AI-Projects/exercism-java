#!/usr/bin/env python3
"""Focused OCR metadata-to-JUnit mapping and maintained-source reproducibility check."""
from __future__ import annotations
import json
import shutil
import tempfile
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXERCISE = ROOT / "exercises/practice/ocr-numbers"
CASES = {
    "5ee54e1a-b554-4bf3-a056-9a7976c3f7e8": ("Recognizes 0", "testReaderRecognizesSingle0"),
    "027ada25-17fd-4d78-aee6-35a19623639d": ("Recognizes 1", "testReaderRecognizesSingle1"),
    "3cce2dbd-01d9-4f94-8fae-419a822e89bb": (
        "Unreadable but correctly sized inputs return ?",
        "testReaderReturnsQuestionMarkForUnreadableButCorrectlySizedInput",
    ),
}

def main() -> None:
    config = json.loads((EXERCISE / ".meta/config.json").read_text())
    tests = tomllib.loads((EXERCISE / ".meta/tests.toml").read_text())
    test_path = EXERCISE / config["files"]["test"][0]
    source = test_path.read_text()
    for uuid, (description, method) in CASES.items():
        assert uuid in tests, f"Missing canonical test UUID: {uuid}"
        assert tests[uuid]["description"] == description, f"Unexpected TOML description for {uuid}"
        assert f'@DisplayName("{description}")' in source, f"Missing JUnit display name: {description}"
        assert f"void {method}(" in source, f"Missing JUnit method: {method}"
    assert not list(EXERCISE.rglob("*.j2")) and not list(EXERCISE.rglob("*.jinja")),
        "Unexpected per-exercise Jinja template found; review the source-of-truth documentation"
    with tempfile.TemporaryDirectory(prefix="r58-t012-source-") as temporary:
        root = Path(temporary)
        copies = []
        for name in ("first", "second"):
            target = root / name
            shutil.copytree(EXERCISE, target, ignore=shutil.ignore_patterns("build", ".gradle"))
            copies.append((target / config["files"]["test"][0]).read_bytes())
        assert copies[0] == copies[1], "Maintained JUnit source differs between clean copies"
    print("PASS: three canonical UUIDs map to the maintained JUnit test cases.")
    print("PASS: two fresh copies contain byte-identical Java test source.")
    print("NOTE: Configlet syncs tests.toml; the JUnit source is maintained by hand.")

if __name__ == "__main__":
    main()
