# R58-T020 evidence

Run from the repository root:

```bash
python3 work/R58-T020/check.py
```

The checker runs all enabled JUnit cases against the maintained reference in an isolated temporary copy, then compiles and executes `CircularBufferContractProbe.java`. The probe asserts the selected overwrite, read-position, clear/wrap-around and exception contracts shown in the exercise hints.

The check does not infer behavior for zero or negative capacity. It hashes the learner solution before and after, and records test counts and probe output in `latest-result.json` when run.

No local execution result is claimed in this commit.
