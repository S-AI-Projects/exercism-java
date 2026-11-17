# R58-T018 evidence

Run from the repository root:

```bash
python3 work/R58-T018/check.py
```

The checker invokes `tools/course_checks/r58-t018.py` to validate every role in the real `.meta/config.json` `files` object. It also checks three negative fixtures: missing reference, missing test, and path traversal outside the exercise. It then runs the enabled Gradle test suite against the configured reference in a temporary copy.

The learner solution file is hashed before and after. Test counts and metadata fixture results are written to `latest-result.json` when the check runs. No local execution result is claimed in this commit.
