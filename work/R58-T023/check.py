#!/usr/bin/env python3
"""
Verification check for Task R58-T023 (bowling mutation-driven regression).

Verifies:
1. Reference solution passes all tests in a temporary directory.
2. A deliberate mutant (wrong second bonus roll lookup for consecutive strikes)
   FAILS the named test: consecutiveStrikesEachGetTheTwoRollBonus
   (@DisplayName "consecutive strikes each get the two roll bonus").
3. The original passes and the mutant fails; changing only formatting is not valid.
4. Working tree learner stub remains unsolved.
5. Reports executed test counts; exits non-zero on assertion failures.

Named anchored cases:
- aStrikeEarnsTenPointsInFrameWithASingleRoll
  UUID: 75269642-2b34-4b72-95a4-9be28ab16902
- pointsScoredInTheTwoRollsAfterAStrikeAreCountedTwiceAsABonus
  UUID: 037f978c-5d01-4e49-bdeb-9e20a2e6f9a6
- consecutiveStrikesEachGetTheTwoRollBonus
  UUID: 1635e82b-14ec-4cd1-bce4-4ea14bd13a49  <-- the rejecting case
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import tomllib
import xml.etree.ElementTree as ET

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
WORK_DIR = os.path.join(REPO_ROOT, "work", "R58-T023")
EXERCISE_DIR = os.path.join(REPO_ROOT, "exercises", "practice", "bowling")

NAMED_CASES = [
    {
        "method": "aStrikeEarnsTenPointsInFrameWithASingleRoll",
        "display_name": "a strike earns ten points in a frame with a single roll",
        "uuid": "75269642-2b34-4b72-95a4-9be28ab16902",
        "input": [10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        "expected": 10,
    },
    {
        "method": "pointsScoredInTheTwoRollsAfterAStrikeAreCountedTwiceAsABonus",
        "display_name": "points scored in the two rolls after a strike are counted twice as a bonus",
        "uuid": "037f978c-5d01-4e49-bdeb-9e20a2e6f9a6",
        "input": [10, 5, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        "expected": 26,
    },
    {
        "method": "consecutiveStrikesEachGetTheTwoRollBonus",
        "display_name": "consecutive strikes each get the two roll bonus",
        "uuid": "1635e82b-14ec-4cd1-bce4-4ea14bd13a49",
        "input": [10, 10, 10, 5, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        "expected": 81,
    },
]

# The mutant: change nextNextRoll to use next.first instead of nextNext.first
# when next is a strike — wrong second bonus roll for consecutive strikes.
MUTANT_LINE_ORIGINAL = "        return next.isStrike() ? nextNext.first : next.second;"
MUTANT_LINE_MUTATED  = "        return next.isStrike() ? next.first : next.second; // MUTANT: wrong second bonus"


def get_env():
    env = os.environ.copy()
    jdk = "/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home"
    if os.path.exists(jdk):
        env["JAVA_HOME"] = jdk
        env["PATH"] = f"/opt/homebrew/opt/openjdk@21/bin:{env.get('PATH', '')}"
    return env


def get_tool_versions(env):
    versions = {"python": sys.version.split()[0]}
    try:
        proc = subprocess.run(["java", "-version"], env=env, capture_output=True, text=True)
        versions["java"] = (proc.stderr or proc.stdout).splitlines()[0].strip()
    except Exception as e:
        versions["java"] = f"unknown: {e}"
    try:
        proc = subprocess.run(
            ["./gradlew", "--version"],
            cwd=EXERCISE_DIR,
            env=env,
            capture_output=True,
            text=True,
        )
        for line in proc.stdout.splitlines():
            if line.startswith("Gradle "):
                versions["gradle"] = line.strip()
                break
    except Exception as e:
        versions["gradle"] = f"unknown: {e}"
    return versions


def copy_exercise_with_reference(base_dir, config, mutant=False):
    """Copy exercise to temp dir, substitute reference, optionally inject mutant."""
    scratch = os.path.join(base_dir, "bowling")
    shutil.copytree(EXERCISE_DIR, scratch)

    solution_rel = config["files"]["solution"][0]
    test_rel = config["files"]["test"][0]
    example_rels = config["files"]["example"]

    # Copy all reference files
    for ref_rel in example_rels:
        dest_path = os.path.join(scratch, solution_rel)
        ref_path = os.path.join(scratch, ref_rel)
        if ref_rel.endswith("BowlingGame.java"):
            shutil.copy2(ref_path, dest_path)
        else:
            # Frame.java goes alongside BowlingGame.java in src/main/java
            dest_dir = os.path.dirname(os.path.join(scratch, solution_rel))
            shutil.copy2(ref_path, os.path.join(dest_dir, os.path.basename(ref_rel)))

    # Inject mutant into Frame.java if requested
    if mutant:
        frame_dest = os.path.join(
            scratch, os.path.dirname(solution_rel), "Frame.java"
        )
        with open(frame_dest) as f:
            content = f.read()
        assert MUTANT_LINE_ORIGINAL in content, "Original mutant line not found in Frame.java"
        content = content.replace(MUTANT_LINE_ORIGINAL, MUTANT_LINE_MUTATED)
        with open(frame_dest, "w") as f:
            f.write(content)

    # Enable all disabled tests
    scratch_test = os.path.join(scratch, test_rel)
    with open(scratch_test) as f:
        tc = f.read()
    tc = tc.replace('@Disabled("Remove to run test")', "")
    with open(scratch_test, "w") as f:
        f.write(tc)

    return scratch


def run_gradle_test(scratch_dir, env):
    return subprocess.run(
        ["./gradlew", "test"],
        cwd=scratch_dir,
        env=env,
        capture_output=True,
        text=True,
    )


def parse_xml_results(scratch_dir):
    xml_file = os.path.join(
        scratch_dir, "build", "test-results", "test", "TEST-BowlingGameTest.xml"
    )
    assert os.path.isfile(xml_file), f"JUnit XML not found: {xml_file}"
    tree = ET.parse(xml_file)
    root = tree.getroot()
    total = int(root.attrib.get("tests", 0))
    skipped = int(root.attrib.get("skipped", 0))
    failures = int(root.attrib.get("failures", 0))
    errors = int(root.attrib.get("errors", 0))
    passed = total - skipped - failures - errors

    # Build dict: display_name -> status
    case_results = {}
    for tc in root.findall("testcase"):
        name = tc.attrib.get("name", "")
        if tc.find("failure") is not None:
            status = "FAILED"
        elif tc.find("skipped") is not None:
            status = "SKIPPED"
        elif tc.find("error") is not None:
            status = "ERROR"
        else:
            status = "PASSED"
        case_results[name] = status

    return {
        "total": total,
        "passed": passed,
        "skipped": skipped,
        "failures": failures,
        "errors": errors,
        "case_results": case_results,
    }


def main():
    os.makedirs(WORK_DIR, exist_ok=True)
    env = get_env()
    tool_versions = get_tool_versions(env)

    print("Tool versions:")
    for k, v in tool_versions.items():
        print(f"  {k}: {v}")

    # Load config
    config_file = os.path.join(EXERCISE_DIR, ".meta", "config.json")
    with open(config_file) as f:
        config = json.load(f)

    solution_rel = config["files"]["solution"][0]

    # === Step 1: tests.toml parses, named UUIDs present ===
    print("\n=== Step 1: Validate tests.toml ===")
    toml_file = os.path.join(EXERCISE_DIR, ".meta", "tests.toml")
    with open(toml_file, "rb") as f:
        toml_data = tomllib.load(f)
    for case in NAMED_CASES:
        assert case["uuid"] in toml_data, f"UUID {case['uuid']} not in tests.toml"
        print(f"  UUID {case['uuid']} -> '{toml_data[case['uuid']]['description']}' OK")

    # === Step 2: Learner stub unsolved ===
    print("\n=== Step 2: Learner stub remains unsolved ===")
    learner_stub_path = os.path.join(EXERCISE_DIR, solution_rel)
    with open(learner_stub_path) as f:
        stub_content = f.read()
    assert "UnsupportedOperationException" in stub_content, "Learner stub must remain unsolved!"
    print("  Confirmed: stub throws UnsupportedOperationException.")

    results = {
        "status": "RUNNING",
        "tool_versions": tool_versions,
        "inputs": {
            "named_cases": NAMED_CASES,
            "mutant": {
                "file": "Frame.java",
                "original": MUTANT_LINE_ORIGINAL.strip(),
                "mutated": MUTANT_LINE_MUTATED.strip(),
                "description": "Uses next.first instead of nextNext.first for the second strike bonus roll",
            },
        },
        "checks": {},
    }

    # === Step 3: Reference passes all tests ===
    print("\n=== Step 3: Reference solution passes all tests ===")
    with tempfile.TemporaryDirectory() as tmp:
        scratch = copy_exercise_with_reference(tmp, config, mutant=False)
        proc = run_gradle_test(scratch, env)
        print(f"  Gradle exit code: {proc.returncode}")
        assert proc.returncode == 0, f"Reference failed gradle!\nSTDERR: {proc.stderr[-1000:]}"

        ref_results = parse_xml_results(scratch)
        print(f"  Total: {ref_results['total']}, Passed: {ref_results['passed']}, "
              f"Failures: {ref_results['failures']}, Skipped: {ref_results['skipped']}")
        assert ref_results["total"] > 0, "Zero tests run!"
        assert ref_results["failures"] == 0, f"Reference has failures: {ref_results['failures']}"
        assert ref_results["errors"] == 0

        # Named cases all pass with reference
        for case in NAMED_CASES:
            status = ref_results["case_results"].get(case["display_name"], "NOT FOUND")
            assert status == "PASSED", f"Named case '{case['display_name']}' expected PASSED, got {status}"
            print(f"  [NAMED CASE] '{case['display_name']}' -> PASSED ✓")

        results["checks"]["reference"] = {
            "exit_code": proc.returncode,
            **{k: v for k, v in ref_results.items() if k != "case_results"},
            "named_cases": {c["method"]: "PASSED" for c in NAMED_CASES},
        }

    # === Step 4: Mutant fails the rejecting test ===
    print("\n=== Step 4: Mutant fails 'consecutive strikes each get the two roll bonus' ===")
    rejecting_case = NAMED_CASES[2]  # consecutiveStrikesEachGetTheTwoRollBonus

    with tempfile.TemporaryDirectory() as tmp:
        scratch = copy_exercise_with_reference(tmp, config, mutant=True)
        proc = run_gradle_test(scratch, env)
        print(f"  Gradle exit code (mutant): {proc.returncode} (expected non-zero)")

        mutant_results = parse_xml_results(scratch)
        print(f"  Total: {mutant_results['total']}, Passed: {mutant_results['passed']}, "
              f"Failures: {mutant_results['failures']}")

        rejecting_status = mutant_results["case_results"].get(
            rejecting_case["display_name"], "NOT FOUND"
        )
        assert rejecting_status == "FAILED", (
            f"Expected mutant to FAIL '{rejecting_case['display_name']}', "
            f"but got: {rejecting_status}"
        )
        print(f"  [REJECTING CASE] '{rejecting_case['display_name']}' -> FAILED ✓ (mutant correctly caught)")

        # Other named cases (non-consecutive-strike) should still pass
        for case in NAMED_CASES[:2]:
            status = mutant_results["case_results"].get(case["display_name"], "NOT FOUND")
            assert status == "PASSED", f"Non-rejecting case '{case['display_name']}' should still pass, got {status}"
            print(f"  [OTHER NAMED CASE] '{case['display_name']}' -> {status}")

        results["checks"]["mutant"] = {
            "exit_code": proc.returncode,
            **{k: v for k, v in mutant_results.items() if k != "case_results"},
            "rejecting_case": rejecting_case["display_name"],
            "rejecting_case_status": rejecting_status,
            "expected_rejecting_status": "FAILED",
        }

    # === Step 5: Working tree not modified ===
    with open(learner_stub_path) as f:
        assert f.read() == stub_content, "Working tree was modified!"
    print("\n  Working tree integrity verified: untouched.")

    results["status"] = "PASSED"
    results_file = os.path.join(WORK_DIR, "results.json")
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nAll assertions passed! Evidence saved to {results_file}")
    sys.exit(0)


if __name__ == "__main__":
    main()
