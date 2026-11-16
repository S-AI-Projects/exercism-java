#!/usr/bin/env python3
"""Exercise the isolated RLE runner's success, failure, zero-test and cleanup paths."""
from __future__ import annotations
import hashlib,json,platform,re,shutil,subprocess,sys,tempfile,time
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
EXERCISE=ROOT/"exercises/practice/run-length-encoding"
CONFIG=json.loads((EXERCISE/".meta/config.json").read_text())

def hashes(paths):
    return {str(path):hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}

def assert_learner_unchanged(paths, before, label):
    if hashes(paths)!=before:
        raise AssertionError(f"Learner starter source changed during {label}")

def copy_prepared(destination):
    shutil.copytree(EXERCISE,destination,ignore=shutil.ignore_patterns("build",".gradle"))
    for relative in CONFIG["files"]["example"]:
        source=destination/relative
        if not source.is_file(): raise FileNotFoundError(source)
        target=destination/"src/main/java"/source.name
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(source,target)
    for relative in CONFIG["files"]["test"]:
        path=destination/relative
        path.write_text(re.sub(r'^\s*@Disabled\("Remove to run test"\)\s*\n',"",
                               path.read_text(),flags=re.M))

def execute(destination, extra=()):
    process=subprocess.run(["./gradlew","test","--no-daemon",*extra],cwd=destination,
                            text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    counts={"tests":0,"failures":0,"errors":0,"skipped":0,"failed_test_names":[]}
    reports=list((destination/"build/test-results/test").glob("TEST-*.xml"))
    for report in reports:
        root=ET.parse(report).getroot()
        for key in ("tests","failures","errors","skipped"):
            counts[key]+=int(root.attrib.get(key,0))
        for case in root.iter("testcase"):
            if case.find("failure") is not None or case.find("error") is not None:
                counts["failed_test_names"].append(case.attrib.get("name",""))
    counts["executed"]=counts["tests"]-counts["skipped"]
    return process.returncode,counts,process.stdout[-3000:]

def require_success(label, result):
    code,counts,output=result
    if code or counts["executed"]==0 or counts["failures"] or counts["errors"] or counts["skipped"]:
        raise RuntimeError(f"{label} rejected: return={code}, counts={counts}\n{output}")

def main():
    learner=[EXERCISE/p for p in CONFIG["files"]["solution"]]
    before=hashes(learner)
    evidence={}
    temporary_root=None
    try:
        with tempfile.TemporaryDirectory(prefix="r58-t019-") as temporary:
            temporary_root=Path(temporary)
            good=temporary_root/"good"; copy_prepared(good)
            success=execute(good); require_success("reference run",success)
            assert_learner_unchanged(learner,before,"successful run")
            evidence["success"]={"return_code":success[0],**success[1],
                                 "learner_hashes_unchanged":True}

            broken=temporary_root/"broken"; copy_prepared(broken)
            source=broken/"src/main/java/RunLengthEncoding.java"
            code=source.read_text()
            if code.count("return data;")!=1:
                raise AssertionError("Could not locate the expected empty-input return")
            source.write_text(code.replace("return data;", 'return "BROKEN";', 1))
            failure=execute(broken)
            assert_learner_unchanged(learner,before,"deliberately failing run")
            try:
                require_success("deliberately failing reference",failure)
            except RuntimeError:
                if "empty string" not in failure[1]["failed_test_names"]:
                    raise AssertionError(f"Mutant did not fail the enabled empty-string assertion: {failure[1]}")
            else:
                raise AssertionError("Deliberately failing reference was incorrectly accepted")
            evidence["deliberate_failure"]={"return_code":failure[0],**failure[1],
                                            "learner_hashes_unchanged":True}

            empty=temporary_root/"empty-selection"; copy_prepared(empty)
            zero=execute(empty,("--tests","NoSuchRleTestClass"))
            assert_learner_unchanged(learner,before,"zero-test run")
            try:
                require_success("zero-test selection",zero)
            except RuntimeError:
                if zero[1]["executed"]!=0:
                    raise AssertionError(f"Expected zero executed tests, got {zero[1]}")
            else:
                raise AssertionError("Zero-test selection was incorrectly accepted")
            evidence["zero_test_selection"]={"return_code":zero[0],**zero[1],
                                             "learner_hashes_unchanged":True}
    finally:
        assert_learner_unchanged(learner,before,"final cleanup")
    if temporary_root is None or temporary_root.exists():
        raise AssertionError("Temporary directory was not cleaned up")
    result={"task":"R58-T019","timestamp_unix":int(time.time()),"python":sys.version,
            "platform":platform.platform(),"runs":evidence,
            "learner_solution_hashes_unchanged":True,"temporary_directories_cleaned":True}
    out=ROOT/"work/R58-T019/latest-result.json"; out.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
    print("PASS: success accepted; encodeEmpty and zero-test runs rejected; learner hash unchanged.")

if __name__=="__main__":
    try: main()
    except Exception as e: print(f"FAIL: {e}",file=sys.stderr); raise SystemExit(1)
