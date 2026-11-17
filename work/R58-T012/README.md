# R58-T012 evidence

Run from the repository root:

```bash
python3 work/R58-T012/check.py
```

The check verifies the three canonical UUID-to-JUnit mappings, confirms that two clean copies preserve identical maintained Java test source, then copies the exercise including dotfiles, substitutes the configured reference sources only in the temporary copy, enables learner-disabled tests in that copy, and runs Gradle. It reports the executed count and fails on zero tests, skipped tests, test failures, errors, or a non-zero Gradle exit.

Important source-of-truth finding: Configlet synchronizes `.meta/tests.toml`; the Java JUnit test class is maintained by hand. No per-exercise Jinja template was found, so this task documents the real maintenance relationship rather than inventing a template interface.

Execution evidence is generated in `latest-result.json` when the command is run. No local execution result is claimed in this commit.
