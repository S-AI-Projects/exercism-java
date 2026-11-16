#!/usr/bin/env python3
"""Run metadata path fixtures and Largest Series Product reference tests."""
from __future__ import annotations
import hashlib,json,platform,re,shutil,subprocess,sys,tempfile,time
import xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
EXERCISE=ROOT/"exercises/practice/largest-series-product"
CONFIG=json.loads((EXERCISE/".meta/config.json").read_text())

def main():
    focused=subprocess.run([sys.executable,"tools/course_checks/r58-t018.py"],cwd=ROOT,
                            text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    if focused.returncode: raise RuntimeError(f"Metadata validation failed:\n{focused.stdout}")
    learner=[EXERCISE/p for p in CONFIG["files"]["solution"]]
    before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in learner}
    with tempfile.TemporaryDirectory(prefix="r58-t018-") as tmp:
        scratch=Path(tmp)/"largest-series-product"
        shutil.copytree(EXERCISE,scratch,ignore=shutil.ignore_patterns("build",".gradle"))
        for relative in CONFIG["files"]["example"]:
            src=scratch/relative
            if not src.is_file(): raise FileNotFoundError(src)
            dst=scratch/"src/main/java"/src.name
            dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dst)
        for relative in CONFIG["files"]["test"]:
            path=scratch/relative
            path.write_text(re.sub(r'^\s*@Disabled\("Remove to run test"\)\s*\n',"",
                                   path.read_text(),flags=re.M))
        test=subprocess.run(["./gradlew","test","--no-daemon"],cwd=scratch,text=True,
                            stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        counts={"tests":0,"failures":0,"errors":0,"skipped":0}
        for report in (scratch/"build/test-results/test").glob("TEST-*.xml"):
            root=ET.parse(report).getroot()
            for key in counts: counts[key]+=int(root.attrib.get(key,0))
        counts["executed"]=counts["tests"]-counts["skipped"]
        if test.returncode or not counts["executed"] or counts["failures"] or counts["errors"] or counts["skipped"]:
            raise RuntimeError(f"Reference tests failed: {counts}\n{test.stdout[-4000:]}")
    after={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in learner}
    if before!=after: raise AssertionError("Learner starter source changed")
    result={"task":"R58-T018","timestamp_unix":int(time.time()),"python":sys.version,
            "platform":platform.platform(),"tests":counts,"metadata_fixture_check":focused.stdout,
            "learner_solution_hashes_unchanged":True}
    out=ROOT/"work/R58-T018/latest-result.json"; out.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
    print("PASS: real metadata and all three negative fixtures behave as expected.")

if __name__=="__main__":
    try: main()
    except Exception as e: print(f"FAIL: {e}",file=sys.stderr); raise SystemExit(1)
