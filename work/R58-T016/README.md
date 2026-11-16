# R58-T016 evidence

Run from the repository root:

```bash
python3 work/R58-T016/check.py
```

The checker runs every enabled JUnit case against the maintained reference in a temporary copy. It then compiles the reference and the independent alphabet-lookup alternative and asserts that both produce the expected output for all 10 exercise cases, including wrap-around, uppercase, spaces, digits and punctuation.

The alternative is kept under this task's `work/` directory and is not copied into the learner solution path. The check records test counts and comparison output in `latest-result.json`, and verifies that learner starter files remain unchanged.

Execution evidence is generated when the command is run; no local execution result is claimed in this commit.
