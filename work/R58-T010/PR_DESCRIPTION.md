# Pull Request

<!-- Your content goes here: -->
# R58-T010: zebra-puzzle: expand guidance with decision table and verify test suite

## Description
Expands the guidance for the `zebra-puzzle` practice exercise around the canonical JUnit 5 test cases (`@Test @DisplayName("resident who drinks water")` and `@Test @DisplayName("resident who owns zebra")`) for Task R58-T010. Formulates a complete deductive breakdown demonstrating how both expected outcomes follow inexorably from the 15 specification statements. Establishes a comprehensive decision table linking input queries and constraints to required outcomes, and provides an explicit statement distinguishing specified contract behavior from inputs outside the exercise contract (e.g., query methods for unspecified attributes, dynamic rules, and extraneous exception rules). Implements an automated verification check using Python `subprocess` and isolated scratch directories to validate real metadata, reject negative fixtures, verify reference execution (2 executed, 2 passed), run a standalone contract probe, verify failure-mode propagation, and protect unsolved working-tree learner starter files (`UnsupportedOperationException` and SHA-256 integrity preserved).

## Related Issue
Fixes: #10

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
- `exercises/practice/zebra-puzzle/.docs/hints.md`:
  - Added comprehensive learner guidance for the Zebra Puzzle constraint satisfaction problem.
  - Provided step-by-step deductive analysis across positional anchors, house colors, beverages, pets, and hobbies.
  - Built a full 5x5 house assignment matrix connecting all 25 attribute slots.
  - Created a decision table connecting each `@DisplayName` case and method invocation (`getWaterDrinker()`, `getZebraOwner()`) to its required outcome.
  - Added an explicit statement separating specified behavior from inputs outside the exercise contract (parameterless methods, no intermediate query methods, no dynamic configuration, no extra exception rules, strict string formatting, call-ordering independence, and algorithm neutrality).
- `docs/maintenance/zebra-puzzle.md`:
  - Documented problem contract, domain model, and canonical test suite metadata (`tests.toml` UUIDs and `@DisplayName` annotations).
  - Provided complete constraint satisfaction flowchart and assignment matrix.
  - Established the decision table and specification boundary analysis.
  - Documented file roles, separating maintained source files from ephemeral build artifacts (`build/`, `.gradle/`).
  - Recorded failure-mode coverage across maintained reference execution, deliberate mutant rejection, and empty test selection rejection.
- `work/R58-T010/ZebraPuzzleContractProbe.java`:
  - Standalone executable probe verifying `ZebraPuzzle` invariants: water drinker equals `"Norwegian"`, zebra owner equals `"Japanese"`, invocation order independence, idempotence on repeated calls, and strict String return typing.
- `tools/course_checks/r58-t010.py`:
  - Added course verification entry point delegating to `work/R58-T010/check.py`.
- `work/R58-T010/check.py`:
  - Automated verification script using Python `subprocess` and isolated temporary scratch directories.
  - Dynamically resolves file paths from `.meta/config.json` and asserts path containment.
  - Tests three deliberate negative fixtures (missing reference, missing test, and outside traversal).
  - Validates canonical UUIDs and `@DisplayName` annotations against `tests.toml` and `ZebraPuzzleTest.java`.
  - Executes reference against all canonical tests in temporary isolation (2 executed, 2 passed, 0 failures, 0 errors, 0 skipped).
  - Executes `ZebraPuzzleContractProbe.java` against compiled reference classes.
  - Evaluates deliberate mutant failure (`getWaterDrinker()` returning `"Englishman"`) and empty test selection, asserting appropriate non-zero child exit codes and failure rejection.
  - Asserts temporary scratch directories are cleanly removed and confirms working-tree learner starter stub remains unsolved and pristine.
- `work/R58-T010/README.md`:
  - Execution instructions, task structure, full house assignment matrix, decision table, and failure-mode verification matrix.
- `work/R58-T010/results.json` and `latest-result.json`:
  - Machine-readable evidence of execution, test counts, tool versions, and scenario outcomes.

## Screenshots / Recordings
Not applicable — no UI changes.

## Testing
- Automated verification executed via `python3 work/R58-T010/check.py` and `python3 tools/course_checks/r58-t010.py`.
- Metadata validation:
  - Real metadata verified valid: all paths resolve cleanly inside `exercises/practice/zebra-puzzle`.
  - Missing reference fixture: rejected with `missing file`.
  - Missing test fixture: rejected with `missing file`.
  - Outside-exercise traversal fixture: rejected with `escapes exercise`.
- Canonical tests:
  - UUID `16efb4e4-8ad7-4d5e-ba96-e5537b66fd42` (`resident who drinks water`) verified present and asserting `"Norwegian"`.
  - UUID `084d5b8b-24e2-40e6-b008-c800da8cd257` (`resident who owns zebra`) verified present and asserting `"Japanese"`.
- Maintained reference execution in isolated temporary directory:
  - 2 tests executed, 2 passed, 0 failures, 0 errors, 0 skipped.
- Contract probe execution:
  - 5 contract checks verified (waterDrinker, zebraOwner, order independence, idempotence, String type).
- Failure-mode propagation:
  - Deliberately failing mutant: correctly rejected with non-zero child exit and 1 test failure.
  - Empty test selection (`--tests NoSuchZebraTestClass`): correctly rejected with non-zero child exit and 0 executed tests.
- Working tree learner starter stub `exercises/practice/zebra-puzzle/src/main/java/ZebraPuzzle.java` verified untouched and unsolved (`UnsupportedOperationException`).

## Checklist
- [x] I have tested my changes locally.
- [x] I have added or updated tests, if needed.
- [x] I have updated documentation, if needed.
- [x] I have followed the project's coding guidelines.
- [x] I have run the relevant tests and checks.
- [x] I have addressed previous review feedback, if applicable.

## Additional Notes
- Assigned working branch: `student/e26b07f0710/R58-T010` (and `R58-T010`).
- Base repository: `S-AI-Projects/exercism-java` on `main`.

<!-- DO NOT EDIT BELOW THIS LINE! -->
---

Reviewer Resources:

[Track Policies](https://github.com/exercism/java/blob/main/POLICIES.md#event-checklist)
