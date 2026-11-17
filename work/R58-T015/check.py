#!/usr/bin/env python3
"""Run Luhn tests and collect five-sample medians for three valid input sizes."""
from __future__ import annotations
import hashlib,json,platform,re,shutil,subprocess,sys,tempfile,time
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
EXERCISE=ROOT/"exercises/practice/luhn"
CONFIG=json.loads((EXERCISE/".meta/config.json").read_text())
PROBE=ROOT/"work/R58-T015/LuhnScalingProbe.java"

def main():
    learner=[EXERCISE/p for p in CONFIG["files"]["solution"]]
    hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in learner}
    with tempfile.TemporaryDirectory(prefix="r58-t015-") as tmp:
        scratch=Path(tmp)/"luhn"
        shutil.copytree(EXERCISE,scratch,ignore=shutil.ignore_patterns("build",".gradle"))
        for relative in CONFIG["files"]["example"]:
            source=scratch/relative
            if not source.is_file(): raise FileNotFoundError(source)
            target=scratch/"src/main/java"/source.name
            target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(source,target)
        for relative in CONFIG["files"]["test"]:
            path=scratch/relative
            path.write_text(re.sub(r'^\s*@Disabled\("Remove to run test"\)\s*\n',"",
                                   path.read_text(),flags=re.M))
        test=subprocess.run(["./gradlew","test","--no-daemon"],cwd=scratch,text=True,
                            stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        totals={"tests":0,"failures":0,"errors":0,"skipped":0}
        reports=list((scratch/"build/test-results/test").glob("TEST-*.xml"))
        for report in reports:
            root=ET.parse(report).getroot()
            for key in totals: totals[key]+=int(root.attrib.get(key,0))
        totals["executed"]=totals["tests"]-totals["skipped"]
        if test.returncode or not totals["executed"] or totals["failures"] or totals["errors"] or totals["skipped"]:
            raise RuntimeError(f"Gradle tests failed: {totals}\n{test.stdout[-4000:]}")
        classes=Path(tmp)/"classes"; classes.mkdir()
        reference=scratch/"src/main/java/LuhnValidator.java"
        compile_result=subprocess.run(["javac","-d",str(classes),str(reference),str(PROBE)],
                                      text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        if compile_result.returncode: raise RuntimeError(f"Benchmark compilation failed:\n{compile_result.stdout}")
        benchmark=subprocess.run(["java","-cp",str(classes),"LuhnScalingProbe"],text=True,
                                 stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        if benchmark.returncode: raise RuntimeError(f"Benchmark failed:\n{benchmark.stdout}")
        lines=benchmark.stdout.strip().splitlines()
        if len(lines)!=3 or any("repetitions=5" not in line or "median_ns_per_call=" not in line for line in lines):
            raise AssertionError(f"Expected three five-repetition medians, got: {lines}")
    if hashes!={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in learner}:
        raise AssertionError("Learner starter file changed")
    result={"task":"R58-T015","timestamp_unix":int(time.time()),"python":sys.version,
            "platform":platform.platform(),"tests":totals,"benchmark_lines":lines,
            "valid_inputs":{"3_digits":"059","9_digits":"055444285","16_digits":"4539319503436467"},
            "repetitions_per_size":5,"calls_per_repetition":20000,
            "learner_solution_hashes_unchanged":True}
    output=ROOT/"work/R58-T015/latest-result.json"
    output.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
    print("PASS: all reference tests pass and three valid sizes have five-sample medians.")

if __name__=="__main__":
    try: main()
    except Exception as e: print(f"FAIL: {e}",file=sys.stderr); raise SystemExit(1)
