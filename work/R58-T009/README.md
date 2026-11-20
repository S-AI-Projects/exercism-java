# Task R58-T009 Evidence: Parallel Letter Frequency Isolated Reference Runner

This directory contains the verification harness and evidence for Task R58-T009 (creating a focused reference runner for `parallel-letter-frequency` that tests the reference from `exercises/practice/parallel-letter-frequency/.meta/config.json` in an isolated temporary copy, reports the real case count, and propagates failures while strictly protecting unsolved learner starter files).

## Quick Run

Run from the repository root:

```bash
# 1. Run focused course check entry point:
python3 tools/course_checks/r58-t009.py

# 2. Run complete verification check:
python3 work/R58-T009/check.py
```

## Structure

- `check.py`: Automated verification suite using Python `subprocess` and isolated `tempfile` scratch directories:
  1. Dynamically resolves `files.solution`, `files.test`, `files.example`, and `files.invalidator` from `exercises/practice/parallel-letter-frequency/.meta/config.json`.
  2. Ensures all declared paths are relative, do not escape the exercise root, and point to existing files.
  3. Tests three deliberately invalid metadata fixtures:
     - `missing reference`: `.meta/src/reference/java/MissingReference.java` $\implies$ rejected with `missing file`.
     - `missing test`: `src/test/java/MissingTest.java` $\implies$ rejected with `missing file`.
     - `outside-exercise traversal`: `../../README.md` $\implies$ rejected with `escapes exercise`.
  4. Validates canonical UUIDs and `@DisplayName` annotations from `tests.toml` and `ParallelLetterFrequencyTest.java`.
  5. Verifies anchor test case `large texts` containing `"it's the result of forty years underground! Allow me to indulge my fancy."` (and substring `"s the result of forty years underground! Allow me to indulge my fancy."`).
  6. Asserts learner starter stub `ParallelLetterFrequency.java` remains unsolved (`UnsupportedOperationException`) and pristine in the working tree.
  7. Copies exercise with dotfiles to a temporary directory, substitutes the maintained reference into `src/main/java/ParallelLetterFrequency.java`, un-disables all test methods, and executes `./gradlew test --no-daemon`.
  8. Asserts 13 executed tests, 13 passed, 0 failures, 0 errors, 0 skipped.
  9. Evaluates deliberate mutant failure (`countLetters()` returning `Collections.emptyMap()`) and asserts rejection with non-zero child exit and assertion failures.
  10. Evaluates empty test selection (`--tests NoSuchParallelLetterFrequencyTestClass`) and asserts rejection with non-zero exit and 0 executed tests.
  11. Verifies temporary directories are completely removed and learner file hashes remain identical before/after every run and in cleanup.
  12. Verifies `docs/maintenance/parallel-letter-frequency.md` correctly documents the file mapping and distinguishes generated artifacts.
  13. Records tool versions, test counts, and check evidence in `results.json` and `latest-result.json`.
- `PR_DESCRIPTION.md`: Pull Request description ready for submission to `S-AI-Projects/exercism-java`.
- `results.json` / `latest-result.json`: Machine-readable evidence of execution.

## Runner Path Resolution Summary

| Role | Declared Path | Runner Resolution & Role |
|---|---|---|
| `solution` | `src/main/java/ParallelLetterFrequency.java` | Unsolved learner stub (throws `UnsupportedOperationException`). |
| `test` | `src/test/java/ParallelLetterFrequencyTest.java` | JUnit 5 test suite (13 canonical tests) compiled into the test source set. |
| `example` | `.meta/src/reference/java/ParallelLetterFrequency.java` | Maintained reference implementation copied to scratch `src/main/java` for reference verification. |
| `invalidator` | `build.gradle` | Exercise build definition triggering cache invalidation. |

## Failure-Mode Verification Matrix

| Scenario | Subprocess Command | Expected Result | Actual Result | Verification Status |
|---|---|---|---|---|
| **Maintained Reference** | `./gradlew test --no-daemon` | Exit 0, 13 executed, 0 failures | Exit 0, 13 executed, 13 passed | **PASSED** |
| **Deliberate Mutant** | `./gradlew test --no-daemon` (empty map return) | Exit 1, failures > 0 | Exit 1, 9 failures, 0 errors | **REJECTED AS EXPECTED** |
| **Empty Selection** | `./gradlew test --no-daemon --tests NoSuchClass` | Exit 1, 0 executed | Exit 1, 0 executed | **REJECTED AS EXPECTED** |
