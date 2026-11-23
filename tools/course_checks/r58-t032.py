#!/usr/bin/env python3
"""Verify prism case metadata, its documented mapping, and sync reproducibility."""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from common import record_versions, run_reference_tests  # noqa: E402

TASK = "R58-T032"
SLUG = "prism"
EVIDENCE = ROOT / "work" / TASK
SELECTED = {
    "ec65d3b3-f7bf-4015-8156-0609c141c4c4": ("zero prisms", "testZeroPrisms"),
    "ec0ca17c-0c5f-44fb-89ba-b76395bdaf1c": ("one prism one hit", "testOnePrismOneHit"),
    "0db955f2-0a27-4c82-ba67-197bd6202069": ("one prism zero hits", "testOnePrismHitsZero"),
}


def sync_in_fresh_track(copy_root: Path, configlet: Path) -> tuple[bytes, bytes]:
    shutil.copy2(ROOT / "config.json", copy_root / "config.json")
    shutil.copytree(ROOT / "docs", copy_root / "docs", ignore=shutil.ignore_patterns("*.png", "*.jpg"))
    shutil.copytree(
        ROOT / "exercises/practice/prism",
        copy_root / "exercises/practice/prism",
        ignore=shutil.ignore_patterns("build", ".gradle"),
    )
    result = subprocess.run(
        [str(configlet), "--track-dir", str(copy_root), "sync", "--exercise", SLUG, "--tests", "include", "--offline", "--update", "--yes"],
        cwd=copy_root,
        capture_output=True,
        text=True,
        timeout=120,
    )
    (EVIDENCE / f"configlet-{copy_root.name}.log").write_text(
        result.stdout + result.stderr, encoding="utf-8"
    )
    if result.returncode != 0:
        raise RuntimeError(f"Configlet sync failed in {copy_root.name}; see the saved log")
    exercise = copy_root / "exercises/practice/prism"
    return (
        (exercise / ".meta/tests.toml").read_bytes(),
        (exercise / "src/test/java/PrismTest.java").read_bytes(),
    )


def main() -> int:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    record_versions(EVIDENCE)
    configlet = ROOT / "bin/configlet"
    if not configlet.is_file():
        raise RuntimeError("Configlet is missing; run ./bin/fetch-configlet first")
    with tempfile.TemporaryDirectory(prefix="prism-sync-") as temporary:
        first_root = Path(temporary) / "first"
        second_root = Path(temporary) / "second"
        first_root.mkdir()
        second_root.mkdir()
        first = sync_in_fresh_track(first_root, configlet)
        second = sync_in_fresh_track(second_root, configlet)
    if first != second:
        raise RuntimeError("Two fresh Configlet synchronizations produced different test inputs")
    metadata = tomllib.loads(first[0].decode("utf-8"))
    entries = {key: value for key, value in metadata.items() if isinstance(value, dict)}
    java_tests = first[1].decode("utf-8")
    display_names = re.findall(r'@DisplayName\("([^"]+)"\)', java_tests)
    if len(entries) != 14 or len(display_names) != 14:
        raise RuntimeError(f"Expected 14 metadata and Java cases; found {len(entries)} and {len(display_names)}")
    for uuid, (description, test_method) in SELECTED.items():
        if entries.get(uuid, {}).get("description") != description or test_method not in java_tests:
            raise RuntimeError(f"Prism case mapping is incomplete for {uuid}")
    (EVIDENCE / "sync-summary.txt").write_text(
        f"Configlet cases: {len(entries)}\nJava display cases: {len(display_names)}\n"
        "Two fresh offline syncs: identical metadata and Java test source.\n",
        encoding="utf-8",
    )
    result = run_reference_tests(SLUG, EVIDENCE)
    print(
        f"{TASK}: 14 cases mapped; fresh syncs match; {result['tests']} cases discovered, "
        f"{result['failures']} failures, {result['skipped']} skipped"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
