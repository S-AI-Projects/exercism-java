# Pull Request

<!-- Your content goes here: -->
# R58-T009: parallel-letter-frequency: create isolated reference runner and verify test suite

## Description
Implements an isolated, focused runner for `parallel-letter-frequency` for Task R58-T009. Resolves solution, test, and reference paths dynamically from `exercises/practice/parallel-letter-frequency/.meta/config.json`. Copies the exercise (including dotfiles) to an isolated temporary directory, substitutes the maintained reference into `src/main/java/ParallelLetterFrequency.java`, enables all 13 JUnit 5 canonical test cases exclusively in the temporary copy, and executes `./gradlew test --no-daemon`. Reports exact case counts (13 executed, 13 passed) and verifies that the anchor test case `large texts` (testing text containing `"it's the result of forty years underground! Allow me to indulge my fancy."`) and all other `@DisplayName` cases pass against the reference. Confirms failure propagation for a deliberately broken mutant reference and rejection of an empty test selection. Ensures temporary scratch directories are cleaned up and proves that the unsolved working-tree learner starter stub (`UnsupportedOperationException`) remains completely untouched (SHA-256 integrity verified before and after each run).

## Related Issue
Fixes: #9

## Type of Change
- [ ] Bug Fix
- [ ] New Feature
- [ ] UI/UX Improvement
- [ ] Performance Improvement
- [x] Tests
- [x] Documentation
- [x] Refactoring / Maintenance
- [ ] CI/CD

## Changes Made
- `docs/maintenance/parallel-letter-frequency.md`:
  - Documented runner contract, discovery mechanism, and `.meta/config.json` dynamic file resolution.
  - Formulated a comprehensive table distinguishing maintained source files from ephemeral generated artifacts (`build/`, `.gradle/`).
  - Documented failure-mode coverage across maintained reference execution, deliberate mutant failure, and empty test selection.
  - Documented anchor test case details (`large texts`) and reproduction instructions.
- `tools/course_checks/r58-t009.py`:
  - Added focused course check entry point delegating to `work/R58-T009/check.py`.
- `work/R58-T009/check.py`:
  - Automated verification script using Python `subprocess` and isolated temporary scratch directories.
  - Resolves file roles from `.meta/config.json` and validates path sanitization and containment.
  - Tests three deliberate negative metadata fixtures (missing reference, missing test, and outside traversal).
  - Cross-references canonical UUIDs and `@DisplayName` annotations against `tests.toml` and `ParallelLetterFrequencyTest.java`.
  - Executes reference against all 13 canonical tests in temporary isolation (13 passed, 0 failures, 0 errors, 0 skipped).
  - Evaluates deliberate mutant failure and empty test selection, asserting appropriate failure exit codes and rejection.
  - Validates temporary directory removal and working-tree learner stub integrity (`UnsupportedOperationException` and SHA-256 hashes unchanged).
- `work/R58-T009/README.md`:
  - Execution instructions, task structure, and failure-mode verification matrix.
- `work/R58-T009/results.json` and `latest-result.json`:
  - Machine-readable evidence of execution, test counts, tool versions, and scenario outcomes.

## Screenshots / Recordings
Not applicable — no UI changes.

## Testing
- Automated verification executed via `python3 work/R58-T009/check.py` and `python3 tools/course_checks/r58-t009.py`.
- Metadata validation:
  - Real metadata verified valid: all paths resolve inside `exercises/practice/parallel-letter-frequency`.
  - Missing reference fixture: rejected with `missing file`.
  - Missing test fixture: rejected with `missing file`.
  - Outside-exercise traversal fixture: rejected with `escapes exercise`.
- Canonical tests and anchor case:
  - All 13 canonical tests verified matching `tests.toml`.
  - Anchor case `large texts` containing text `"it's the result of forty years underground! Allow me to indulge my fancy."` verified present and passing.
- Maintained reference execution in isolated temporary directory:
  - 13 tests executed, 13 passed, 0 failures, 0 errors, 0 skipped.
- Failure-mode propagation:
  - Deliberately failing mutant: correctly rejected with non-zero exit and 9 test failures.
  - Empty test selection (`--tests NoSuchClass`): correctly rejected with non-zero exit and 0 executed tests.
- Working tree learner starter stub `exercises/practice/parallel-letter-frequency/src/main/java/ParallelLetterFrequency.java` verified untouched and unsolved (`UnsupportedOperationException`).

## Checklist
- [x] I have tested my changes locally.
- [x] I have added or updated tests, if needed.
- [x] I have updated documentation, if needed.
- [x] I have followed the project's coding guidelines.
- [x] I have run the relevant tests and checks.
- [x] I have addressed previous review feedback, if applicable.

## Additional Notes
- Assigned working branch: `student/e26b07f0710/R58-T009` (and `R58-T009`).
- Base repository: `S-AI-Projects/exercism-java` on `main`.

<!-- DO NOT EDIT BELOW THIS LINE! -->
---

Reviewer Resources:

[Track Policies](https://github.com/exercism/java/blob/main/POLICIES.md#event-checklist)
