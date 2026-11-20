# Task R58-T008 Evidence: Bob Metadata Path Validation & Reference Verification

This directory contains the verification harness and evidence for Task R58-T008 (making the metadata in `exercises/practice/bob/.meta/config.json` understandable and verifiable).

## Quick Run

Run from the repository root:

```bash
# 1. Run focused metadata validation and negative path fixtures:
python3 tools/course_checks/r58-t008.py

# 2. Run complete verification check (metadata, negative fixtures, and isolated Gradle reference tests):
python3 work/R58-T008/check.py
```

## Structure

- `check.py`: Automated verification suite using Python `subprocess` and isolated `tempfile` scratch directories:
  1. Dynamically resolves `files.solution`, `files.test`, `files.example`, and `files.invalidator` from `exercises/practice/bob/.meta/config.json`.
  2. Ensures all declared paths are relative, do not escape the exercise root, and point to existing files.
  3. Tests three deliberately invalid metadata fixtures:
     - `missing reference`: `.meta/src/reference/java/MissingReference.java` $\implies$ rejected with `missing file`.
     - `missing test`: `src/test/java/MissingTest.java` $\implies$ rejected with `missing file`.
     - `outside-exercise traversal`: `../../README.md` $\implies$ rejected with `escapes exercise`.
  4. Validates canonical UUIDs and `@DisplayName` annotations from `tests.toml` and `BobTest.java`.
  5. Asserts learner starter stub `Bob.java` remains unsolved (`UnsupportedOperationException`) and pristine in the working tree.
  6. Copies exercise with dotfiles to a temporary directory, substitutes the maintained reference into `src/main/java/Bob.java`, un-disables all test methods, and executes `./gradlew test --no-daemon`.
  7. Asserts 26 executed tests, 26 passed, 0 failures, 0 errors, 0 skipped.
  8. Verifies `docs/maintenance/bob.md` correctly documents the file mapping and distinguishes generated artifacts.
  9. Records tool versions, test counts, and check evidence in `results.json` and `latest-result.json`.
- `PR_DESCRIPTION.md`: Complete Pull Request description ready for submission to `S-AI-Projects/exercism-java`.
- `results.json` / `latest-result.json`: Machine-readable evidence of execution.

## Runner Path Resolution Summary

| Role | Declared Path | Runner Resolution & Role |
|---|---|---|
| `solution` | `src/main/java/Bob.java` | Unsolved learner stub (throws `UnsupportedOperationException`). |
| `test` | `src/test/java/BobTest.java` | JUnit 5 test suite (26 canonical tests) compiled into the test source set. |
| `example` | `.meta/src/reference/java/Bob.java` | Maintained reference implementation copied to scratch `src/main/java` for reference verification. |
| `invalidator` | `build.gradle` | Exercise build definition triggering cache invalidation. |
