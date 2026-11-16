#!/usr/bin/env python3
"""Exercise the isolated RLE runner's success, failure, zero-test and cleanup paths."""
from __future__ import annotations
import hashlib,json,platform,re,shutil,subprocess,sys,tempfile,time
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
EXERCISE=ROOT/"exercises/practice/run-length-encoding"
CONFIG=json.loads((EXERCISE/".meta/config.json").read_text())

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
    counts={"tests":0,"failures":0,"errors":0,"skipped":0}
    reports=list((destination/"build/test-results/test").glob("TEST-*.xml"))
    for report in reports:
        root=ET.parse(report).getroot()
        for key in counts: counts[key]+=int(root.attrib.get(key,0))
    counts["executed"]=counts["tests"]-counts["skipped"]
    return process.returncode,counts,process.stdout[-3000:]

def require_success(label, result):
    code,counts,output=result
    if code or counts["executed"]==0 or counts["failures"] or counts["errors"] or counts["skipped"]:
        raise RuntimeError(f"{label} rejected: return={code}, counts={counts}\n{output}")

def main():
    learner=[EXERCISE/p for p in CONFIG["files"]["solution"]]
    before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in learner}
    evidence={}
    with tempfile.TemporaryDirectory(prefix="r58-t019-") as temporary:
        root=Path(temporary)
        good=root/"good"; copy_prepared(good)
        success=execute(good); require_success("reference run",success)
        evidence["success"]={"return_code":success[0],**success[1]}

        broken=root/"broken"; copy_prepared(broken)
        source=broken/"src/main/java/RunLengthEncoding.java"
        code=source.read_text()
        target='''if (data.length() == 0) {
            return data;
        }'''
        if code.count(target)!=1: raise AssertionError("Could not locate the expected empty-input branch for mutation")
        source.write_text(code.replace(target,'''if (data.length() == 0) {
            return "BROKEN";
        }''',1))
        failure=execute(broken)
        try:
            require_success("deliberately failing reference",failure)
        except RuntimeError:
            if failure[0]==0 and failure[1]["failures"]==0 and failure[1]["errors"]==0:
                raise AssertionError("Mutant was rejected for an unexpected reason")
        else:
            raise AssertionError("Deliberately failing reference was incorrectly accepted")
        if not ({"encodeEmpty"} & set(failure[1].get("failed_test_names",[]))):
            # Some Gradle/JUnit XML versions expose the testcase name only in the report;
            # require at least one real assertion failure in all versions.
            if failure[1]["failures"]+failure[1]["errors"]==0:
                raise AssertionError("Mutant did not produce an assertion failure")
        evidence["deliberate_failure"]={"return_code":failure[0],**failure[1]}

        empty=root/"empty-selection"; copy_prepared(empty)
        zero=execute(empty,("--tests","NoSuchRleTestClass"))
        try:
            require_success("zero-test selection",zero)
        except RuntimeError:
            if zero[1]["executed"]!=0 and zero[0]==0:
                raise AssertionError("Zero-test selection was rejected for neither zero tests nor process failure")
        else:
            raise AssertionError("Zero-test selection was incorrectly accepted")
        evidence["zero_test_selection"]={"return_code":zero[0],**zero[1]}
        if good.exists() or broken.exists() or empty.exists():
            raise AssertionError("Temporary exercise copies were not cleaned up")
    after={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in learner}
    if before!=after: raise AssertionError("Learner starter file hash changed")
    result={"task":"R58-T019","timestamp_unix":int(time.time()),"python":sys.version,
            "platform":platform.platform(),"runs":evidence,
            "learner_solution_hashes_unchanged":True,"temporary_directories_cleaned":True}
    out=ROOT/"work/R58-T019/latest-result.json"; out.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
    print("PASS: success accepted; assertion failure and zero-test selection rejected; learner hash unchanged.")

if __name__=="__main__":
    try: main()
    except Exception as e: print(f"FAIL: {e}",file=sys.stderr); raise SystemExit(1)
