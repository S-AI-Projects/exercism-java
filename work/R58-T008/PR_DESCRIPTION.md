# Pull Request

<!-- Your content goes here: -->
# R58-T008: bob: validate metadata file paths and verify reference test suite

## Description
Makes the metadata in `exercises/practice/bob/.meta/config.json` understandable and verifiable for Task R58-T008. Explains how the test runner deterministically resolves `src/test/java/BobTest.java` and `.meta/src/reference/java/Bob.java` through the explicit `files` mapping rather than heuristic file searching. Distinguishes maintained source files from generated artifacts (`tests.toml`, `build/`, `.gradle/`). Implemented automated verification validating the real configuration and asserting that three deliberately invalid metadata fixtures (missing reference, missing test, and outside-exercise traversal) fail for the intended reasons. Verified all 26 canonical tests pass against the maintained reference in an isolated temporary copy without modifying the working tree learner stub.

## Related Issue
Fixes: #8

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
- `docs/maintenance/bob.md`:
  - Documented the `files` object schema from `.meta/config.json` (`solution`, `test`, `example`, `invalidator`, `editor`).
  - Explained the runner path resolution and discovery mechanism for `BobTest.java` and `Bob.java`.
  - Formulated a comprehensive table distinguishing maintained source files from generated artifacts (`build/`, `.gradle/`, `.meta/tests.toml`).
  - Documented the three deliberate negative metadata fixtures and reproduction instructions.
- `tools/course_checks/r58-t008.py`:
  - Added focused course check validating real `config.json` file containment and testing the three negative path fixtures.
- `work/R58-T008/check.py`:
  - Automated verification script using Python subprocess and isolated temporary directories.
  - Validates real metadata containment and tests the three negative path fixtures.
  - Copies exercise to a temporary directory, substitutes the reference implementation into `src/main/java/Bob.java`, and executes `./gradlew test --no-daemon`.
  - Asserts all 26 canonical test cases pass with 0 failures, 0 errors, and 0 skipped.
  - Verifies that working tree learner starter stub `src/main/java/Bob.java` remains unsolved (`UnsupportedOperationException`) and pristine.
- `work/R58-T008/README.md`:
  - Execution instructions and task structure documentation.
- `work/R58-T008/results.json` and `latest-result.json`:
  - Recorded verification results and tool versions.

## Screenshots / Recordings
Not applicable — no UI changes.

## Testing
- Automated verification executed via `python3 work/R58-T008/check.py` and `python3 tools/course_checks/r58-t008.py`.
- Metadata validation:
  - Real metadata verified valid: all paths resolve inside `exercises/practice/bob`.
  - Missing reference fixture: rejected with `missing file`.
  - Missing test fixture: rejected with `missing file`.
  - Outside-exercise traversal fixture: rejected with `escapes exercise`.
- Maintained reference executed in an isolated temporary directory via `./gradlew test --no-daemon`:
  - 26 tests executed, 26 passed, 0 failures, 0 errors, 0 skipped.
  - All 26 named canonical cases confirmed passing.
- Working tree learner starter stub `exercises/practice/bob/src/main/java/Bob.java` verified untouched and unsolved (`UnsupportedOperationException`).

## Checklist
- [x] I have tested my changes locally.
- [x] I have added or updated tests, if needed.
- [x] I have updated documentation, if needed.
- [x] I have followed the project's coding guidelines.
- [x] I have run the relevant tests and checks.
- [x] I have addressed previous review feedback, if applicable.

## Additional Notes
- Assigned working branch: `student/e26b07f0710/R58-T008` (and `R58-T008` / `student/e26b07f0710-R58-T008`).
- Base repository: `S-AI-Projects/exercism-java` on `main`.

<!-- DO NOT EDIT BELOW THIS LINE! -->
---

Reviewer Resources:

[Track Policies](https://github.com/exercism/java/blob/main/POLICIES.md#event-checklist)
