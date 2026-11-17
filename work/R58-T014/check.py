#!/usr/bin/env python3
"""Compare Connect reference behavior before and after the scoped readability refactor."""
from __future__ import annotations
import hashlib, json, platform, re, shutil, subprocess, sys, tempfile, time
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
EXERCISE=ROOT/"exercises/practice/connect"
CONFIG=json.loads((EXERCISE/".meta/config.json").read_text())
ORIGINAL=ROOT/"work/R58-T014/original/Connect.java"

def run(exercise):
    p=subprocess.run(["./gradlew","test","--no-daemon"],cwd=exercise,text=True,
                     stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    totals={"tests":0,"failures":0,"errors":0,"skipped":0}
    reports=list((exercise/"build/test-results/test").glob("TEST-*.xml"))
    for report in reports:
        root=ET.parse(report).getroot()
        for key in totals: totals[key]+=int(root.attrib.get(key,0))
    totals["executed"]=totals["tests"]-totals["skipped"]
    return p.returncode,totals,p.stdout[-4000:]

def prepare(destination, connect_source):
    shutil.copytree(EXERCISE,destination,ignore=shutil.ignore_patterns("build",".gradle"))
    for relative in CONFIG["files"]["example"]:
        src=destination/relative
        if src.name=="Connect.java" and connect_source is not None: src=connect_source
        if not src.is_file(): raise FileNotFoundError(src)
        target=destination/"src/main/java"/src.name
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(src,target)
    for relative in CONFIG["files"]["test"]:
        path=destination/relative
        path.write_text(re.sub(r'^\s*@Disabled\("Remove to run test"\)\s*\n',"",
                               path.read_text(),flags=re.M))

def main():
    if not ORIGINAL.is_file(): raise FileNotFoundError(ORIGINAL)
    solution=[EXERCISE/p for p in CONFIG["files"]["solution"]]
    before_hash={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in solution}
    with tempfile.TemporaryDirectory(prefix="r58-t014-") as tmp:
        root=Path(tmp)
        before=root/"before"; after=root/"after"
        prepare(before,ORIGINAL); prepare(after,None)
        bcode,bstats,bout=run(before)
        acode,astats,aout=run(after)
        for label,code,stats,output in (("before",bcode,bstats,bout),("after",acode,astats,aout)):
            if code or not stats["executed"] or stats["failures"] or stats["errors"] or stats["skipped"]:
                raise RuntimeError(f"{label} reference verification failed: {stats}\n{output}")
        if bstats["tests"]!=astats["tests"] or bstats["executed"]!=astats["executed"]:
            raise AssertionError("Before/after test counts differ")
    after_hash={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in solution}
    if before_hash!=after_hash: raise AssertionError("Learner starter files changed")
    result={"task":"R58-T014","timestamp_unix":int(time.time()),"python":sys.version,
            "platform":platform.platform(),"before":bstats,"after":astats,
            "learner_solution_hashes_unchanged":True}
    output=ROOT/"work/R58-T014/latest-result.json"
    output.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
    print("PASS: original and refactored Connect references pass the same enabled test suite.")

if __name__=="__main__":
    try: main()
    except Exception as e: print(f"FAIL: {e}",file=sys.stderr); raise SystemExit(1)
