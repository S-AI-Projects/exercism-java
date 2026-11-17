# R58-T014 evidence

Run from the repository root:

```bash
python3 work/R58-T014/check.py
```

The checker compares the original Connect reference snapshot with the refactored reference in two isolated temporary copies. Both copies use the same enabled JUnit suite. The check fails if either run fails, if the executed test counts differ, or if learner starter-file hashes change.

The scoped change clarifies row/column dimensions, player connection directions, and the one-cell target-edge invariant. No public API, dependency, or connectivity behavior is intentionally changed.

Execution evidence is generated in `latest-result.json` when run. No local execution result is claimed in this commit.
