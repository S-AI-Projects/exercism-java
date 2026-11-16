#!/usr/bin/env python3
"""Validate OCR metadata mapping and run all enabled tests against the reference."""
from __future__ import annotations
import hashlib, json, platform, re, shutil, subprocess, sys, tempfile, time
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXERCISE = ROOT / "exercises/practice/ocr-numbers"

def run(command, cwd):
    return subprocess.run(command, cwd=cwd, text=True, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT)

def main():
    focused = run([sys.executable, "tools/course_checks/r58-t012.py"], ROOT)
    if focused.returncode:
        raise RuntimeError(f"Focused mapping check failed:\n{focused.stdout}")
    config = json.loads((EXERCISE / ".meta/config.json").read_text())
    learner_files = [EXERCISE / p for p in config["files"]["solution"]]
    hashes_before = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in learner_files}
    with tempfile.TemporaryDirectory(prefix="r58-t012-") as temporary:
        scratch = Path(temporary) / "ocr-numbers"
        shutil.copytree(EXERCISE, scratch, ignore=shutil.ignore_patterns("build", ".gradle"))
        scratch_config = json.loads((scratch / ".meta/config.json").read_text())
        source_dir = scratch / "src/main/java"
        source_dir.mkdir(parents=True, exist_ok=True)
        for relative in scratch_config["files"]["example"]:
            source = scratch / relative
            if not source.is_file():
                raise FileNotFoundError(f"Missing configured reference source: {relative}")
            shutil.copy2(source, source_dir / source.name)
        for relative in scratch_config["files"]["test"]:
            path = scratch / relative
            path.write_text(re.sub(r'^\s*@Disabled\("Remove to run test"\)\s*\n', "",
                                   path.read_text(), flags=re.M))
        process = run(["./gradlew", "test", "--no-daemon"], scratch)
        reports = list((scratch / "build/test-results/test").glob("TEST-*.xml"))
        totals = {"tests": 0, "failures": 0, "errors": 0, "skipped": 0}
        for report in reports:
            root = ET.parse(report).getroot()
            for key in totals:
                totals[key] += int(root.attrib.get(key, 0))
        totals["executed"] = totals["tests"] - totals["skipped"]
        if process.returncode or totals["executed"] == 0 or totals["failures"] or totals["errors"] or totals["skipped"]:
            raise RuntimeError(f"Gradle verification failed: {totals}\n{process.stdout[-5000:]}")
    hashes_after = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in learner_files}
    if hashes_before != hashes_after:
        raise RuntimeError("Learner starter source changed during verification")
    result = {"task":"R58-T012","timestamp_unix":int(time.time()),"python":sys.version,
              "platform":platform.platform(),"command":"./gradlew test --no-daemon",
              "return_code":process.returncode,**totals,
              "learner_solution_hashes_unchanged":True,
              "source_of_truth":"tests.toml is Configlet-synced; JUnit test source is maintained by hand."}
    output=ROOT/"work/R58-T012/latest-result.json"
    output.write_text(json.dumps(result,indent=2)+"\n")
    print(focused.stdout, end="")
    print(json.dumps(result,indent=2))
    print(f"PASS: {totals['executed']} tests executed with no skips or failures.")

if __name__ == "__main__":
    try: main()
    except Exception as exc:
        print(f"FAIL: {exc}",file=sys.stderr); raise SystemExit(1)
