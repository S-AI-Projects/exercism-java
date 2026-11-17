#!/usr/bin/env python3
"""Run the reference suite and compare two different cipher approaches."""
from __future__ import annotations
import hashlib,json,platform,re,shutil,subprocess,sys,tempfile,time
import xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
EXERCISE=ROOT/"exercises/practice/rotational-cipher"
CONFIG=json.loads((EXERCISE/".meta/config.json").read_text())

def main():
    learner=[EXERCISE/p for p in CONFIG["files"]["solution"]]
    before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in learner}
    with tempfile.TemporaryDirectory(prefix="r58-t016-") as tmp:
        scratch=Path(tmp)/"rotational-cipher"
        shutil.copytree(EXERCISE,scratch,ignore=shutil.ignore_patterns("build",".gradle"))
        for relative in CONFIG["files"]["example"]:
            src=scratch/relative; dst=scratch/"src/main/java"/src.name
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
            for k in counts: counts[k]+=int(root.attrib.get(k,0))
        counts["executed"]=counts["tests"]-counts["skipped"]
        if test.returncode or not counts["executed"] or counts["failures"] or counts["errors"] or counts["skipped"]:
            raise RuntimeError(f"Reference tests failed: {counts}\n{test.stdout[-4000:]}")
        classes=Path(tmp)/"classes"; classes.mkdir()
        sources=[scratch/"src/main/java/RotationalCipher.java",
                 ROOT/"work/R58-T016/RotationalCipherAlternative.java",
                 ROOT/"work/R58-T016/RotationalCipherComparison.java"]
        compiled=subprocess.run(["javac","-d",str(classes),*(str(p) for p in sources)],
                                text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        if compiled.returncode: raise RuntimeError(f"Comparison compilation failed:\n{compiled.stdout}")
        compared=subprocess.run(["java","-cp",str(classes),"RotationalCipherComparison"],
                                text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        if compared.returncode: raise RuntimeError(f"Approach comparison failed:\n{compared.stdout}")
    after={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in learner}
    if before!=after: raise AssertionError("Learner starter source changed")
    result={"task":"R58-T016","timestamp_unix":int(time.time()),"python":sys.version,
            "platform":platform.platform(),"reference_tests":counts,
            "approach_comparison":compared.stdout.strip(),"learner_solution_hashes_unchanged":True}
    out=ROOT/"work/R58-T016/latest-result.json"; out.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
    print("PASS: reference and alphabet-lookup alternative agree on all 10 exercise cases.")

if __name__=="__main__":
    try: main()
    except Exception as e: print(f"FAIL: {e}",file=sys.stderr); raise SystemExit(1)
