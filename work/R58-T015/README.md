# R58-T015 evidence

Run from the repository root:

```bash
python3 work/R58-T015/check.py
```

The checker runs the enabled Luhn JUnit suite against the maintained reference in a temporary copy, then compiles and runs `LuhnScalingProbe.java` against that same reference. It validates three known-valid inputs before timing and records five repetitions of 20,000 in-process calls per size, reporting the median.

The reference comment explains O(n) time and O(n) auxiliary space. Timings are recorded as observations, not as proof of asymptotic complexity or a speedup. The learner solution file is hashed before and after.

Execution evidence is generated in `latest-result.json` when run. No local execution result is claimed in this commit.
