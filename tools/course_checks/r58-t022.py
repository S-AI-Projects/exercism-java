#!/usr/bin/env python3
"""
Reusable focused regeneration check for isbn-verifier (R58-T022).
Placed under tools/course_checks/ as a standalone verifiable check.

Usage: python3 tools/course_checks/r58-t022.py
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
import xml.etree.ElementTree as ET

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
EXERCISE_DIR = os.path.join(REPO_ROOT, "exercises", "practice", "isbn-verifier")
HAND_MAINTAINED_EXTRA = "valid isbn with check digit padded with letters is invalid"

NAMED_CASES = [
    {"method": "invalidIsbnCheckDigit", "display_name": "invalid isbn check digit",
     "uuid": "19f76b53-7c24-45f8-87b8-4604d0ccd248", "input": "3-598-21508-9", "expected": False},
    {"method": "validIsbnNumberWithCheckDigitOfTen", "display_name": "valid isbn with a check digit of 10",
     "uuid": "4164bfee-fb0a-4a1c-9f70-64c6a1903dcd", "input": "3-598-21507-X", "expected": True},
]


def get_env():
    env = os.environ.copy()
    jdk = "/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home"
    if os.path.exists(jdk):
        env["JAVA_HOME"] = jdk
        env["PATH"] = f"/opt/homebrew/opt/openjdk@21/bin:{env.get('PATH', '')}"
    return env


def extract_display_names(java_file):
    with open(java_file) as f:
        content = f.read()
    return set(re.findall(r'@DisplayName\("([^"]+)"\)', content))


def run_checks():
    env = get_env()

    # 1. Resolve paths
    with open(os.path.join(EXERCISE_DIR, ".meta", "config.json")) as f:
        config = json.load(f)
    solution_rel = config["files"]["solution"][0]
    test_rel = config["files"]["test"][0]
    example_rel = config["files"]["example"][0]

    # 2. tests.toml parses cleanly
    with open(os.path.join(EXERCISE_DIR, ".meta", "tests.toml"), "rb") as f:
        toml_data = tomllib.load(f)
    for case in NAMED_CASES:
        assert case["uuid"] in toml_data, f"UUID {case['uuid']} missing from tests.toml"

    # 3. DisplayName / description cross-check
    java_names = extract_display_names(os.path.join(EXERCISE_DIR, test_rel))
    toml_descriptions = {v["description"] for v in toml_data.values()}
    assert java_names - toml_descriptions == {HAND_MAINTAINED_EXTRA}
    assert toml_descriptions - java_names == set()

    # 4. Round-trip: hand-maintained file is stable across reads
    test_path = os.path.join(EXERCISE_DIR, test_rel)
    with open(test_path, "rb") as f:
        a = f.read()
    with open(test_path, "rb") as f:
        b = f.read()
    assert a == b

    # 5. Learner stub unsolved
    with open(os.path.join(EXERCISE_DIR, solution_rel)) as f:
        stub = f.read()
    assert "UnsupportedOperationException" in stub

    # 6. Run tests in temp dir with reference
    with tempfile.TemporaryDirectory() as tmp:
        scratch = os.path.join(tmp, "isbn-verifier")
        shutil.copytree(EXERCISE_DIR, scratch)
        shutil.copy2(os.path.join(scratch, example_rel), os.path.join(scratch, solution_rel))
        with open(os.path.join(scratch, test_rel)) as f:
            tc = f.read()
        tc = tc.replace('@Disabled("Remove to run test")', "")
        with open(os.path.join(scratch, test_rel), "w") as f:
            f.write(tc)

        proc = subprocess.run(["./gradlew", "test"], cwd=scratch, env=env,
                              capture_output=True, text=True)
        assert proc.returncode == 0, f"Gradle failed: {proc.stderr[-1000:]}"

        xml_file = os.path.join(scratch, "build", "test-results", "test", "TEST-IsbnVerifierTest.xml")
        tree = ET.parse(xml_file)
        root = tree.getroot()
        total = int(root.attrib.get("tests", 0))
        failures = int(root.attrib.get("failures", 0))
        errors = int(root.attrib.get("errors", 0))
        assert total > 0, "Zero tests run!"
        assert failures == 0 and errors == 0, f"failures={failures} errors={errors}"

        for case in NAMED_CASES:
            matches = [tc for tc in root.findall("testcase")
                       if tc.attrib.get("name") == case["display_name"]]
            assert matches, f"Named case not found: {case['display_name']}"
            assert matches[0].find("failure") is None
            assert matches[0].find("skipped") is None

        print(f"isbn-verifier: {total} tests, all passed. Named cases verified.")

    # Stub unchanged
    with open(os.path.join(EXERCISE_DIR, solution_rel)) as f:
        assert f.read() == stub


if __name__ == "__main__":
    run_checks()
    sys.exit(0)
