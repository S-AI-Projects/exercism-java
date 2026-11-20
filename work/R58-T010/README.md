# Task R58-T010 Evidence: Zebra Puzzle Guidance and Isolated Reference Runner

This directory contains the verification harness and evidence for Task R58-T010 (expanding learner guidance for `zebra-puzzle` around the JUnit 5 `@Test @DisplayName` cases, proving why their expected outcomes follow from the 15 specification statements, separating specified behavior from inputs outside the exercise contract, and executing an isolated reference test runner).

## Quick Run

Run from the repository root:

```bash
# 1. Run focused course check entry point:
python3 tools/course_checks/r58-t010.py

# 2. Run complete verification check:
python3 work/R58-T010/check.py
```

## Structure

- `check.py`: Automated verification suite using Python `subprocess` and isolated `tempfile` scratch directories:
  1. Dynamically resolves `files.solution`, `files.test`, `files.example`, and `files.invalidator` from `exercises/practice/zebra-puzzle/.meta/config.json`.
  2. Ensures all declared paths are relative, do not escape the exercise root, and point to existing files.
  3. Tests three deliberately invalid metadata fixtures:
     - `missing reference`: `.meta/src/reference/java/MissingReference.java` $\implies$ rejected with `missing file`.
     - `missing test`: `src/test/java/MissingTest.java` $\implies$ rejected with `missing file`.
     - `outside-exercise traversal`: `../../README.md` $\implies$ rejected with `escapes exercise`.
  4. Validates canonical UUIDs and `@DisplayName` annotations from `tests.toml` and `ZebraPuzzleTest.java`.
  5. Asserts learner starter stub `ZebraPuzzle.java` remains unsolved (`UnsupportedOperationException`) and pristine in the working tree.
  6. Copies exercise with dotfiles to a temporary directory, substitutes the maintained reference into `src/main/java/ZebraPuzzle.java`, un-disables all test methods, and executes `./gradlew test --no-daemon`.
  7. Asserts 2 executed tests, 2 passed, 0 failures, 0 errors, 0 skipped.
  8. Executes standalone contract probe `ZebraPuzzleContractProbe.java` asserting water drinker, zebra owner, order independence, and idempotence.
  9. Evaluates deliberate mutant failure (`getWaterDrinker()` returning `"Englishman"`) and asserts rejection with non-zero child exit and assertion failures.
  10. Evaluates empty test selection (`--tests NoSuchZebraTestClass`) and asserts rejection with non-zero exit and 0 executed tests.
  11. Verifies temporary directories are completely removed and learner file hashes remain identical before/after every run and in cleanup.
  12. Verifies `exercises/practice/zebra-puzzle/.docs/hints.md` and `docs/maintenance/zebra-puzzle.md` correctly document the decision table and explicit statements for unspecified behavior.
  13. Records tool versions, test counts, and check evidence in `results.json` and `latest-result.json`.
- `ZebraPuzzleContractProbe.java`: Standalone probe exercising `ZebraPuzzle` contract boundaries and invariants.
- `PR_DESCRIPTION.md`: Pull Request description ready for submission to `S-AI-Projects/exercism-java`.
- `results.json` / `latest-result.json`: Machine-readable evidence of execution.

## Runner Path Resolution Summary

| Role | Declared Path | Runner Resolution & Role |
|---|---|---|
| `solution` | `src/main/java/ZebraPuzzle.java` | Unsolved learner stub (throws `UnsupportedOperationException`). |
| `test` | `src/test/java/ZebraPuzzleTest.java` | JUnit 5 test suite (2 canonical tests) compiled into the test source set. |
| `example` | `.meta/src/reference/java/ZebraPuzzle.java` | Maintained reference implementation copied to scratch `src/main/java` for reference verification. |
| `invalidator` | `build.gradle` | Exercise build definition triggering cache invalidation. |

## Canonical Case & Decision Table

| Test Case | Query Invocation | Applicable Constraints & Input Conditions | Required Result | Contract Reason & Deduction |
|---|---|---|---|---|
| `resident who drinks water` | `zebraPuzzle.getWaterDrinker()` | Statements 1, 4, 5, 8, 9, 10, 13, 15: Norwegian in House 1, Blue in House 2, Milk in House 3; Green drinks Coffee, Ukrainian drinks Tea, Football drinks Orange juice. Yellow/Painter in House 1. All other beverages eliminated for House 1. | `"Norwegian"` | Only the Norwegian residing in House 1 can drink water without violating any beverage, color, or hobby constraint. |
| `resident who owns zebra` | `zebraPuzzle.getZebraOwner()` | Statements 1–15: Full constraint propagation fixes House 5 as Green/Coffee/Japanese/Chess. Pets for Houses 1–4 are Fox, Horse, Snails, Dog. All other pets eliminated for House 5. | `"Japanese"` | The Japanese resident in House 5 is the sole inhabitant who can own the zebra under the complete constraint set. |

## Full 5-House Assignment Matrix

| Attribute | House 1 | House 2 | House 3 | House 4 | House 5 |
|---|---|---|---|---|---|
| **Position** | First | Second | Middle | Fourth | Fifth |
| **Color** | Yellow | Blue | Red | Ivory | Green |
| **Nationality** | Norwegian | Ukrainian | Englishman | Spaniard | Japanese |
| **Beverage** | Water | Tea | Milk | Orange juice | Coffee |
| **Pet** | Fox | Horse | Snails | Dog | Zebra |
| **Hobby** | Painter | Reading | Dancing | Football | Chess |

## Failure-Mode Verification Matrix

| Scenario | Subprocess Command | Expected Result | Actual Result | Verification Status |
|---|---|---|---|---|
| **Maintained Reference** | `./gradlew test --no-daemon` | Exit 0, 2 executed, 0 failures | Exit 0, 2 executed, 2 passed | **PASSED** |
| **Contract Probe** | `java ZebraPuzzleContractProbe` | Exit 0, 5 invariants verified | Exit 0, contract verified | **PASSED** |
| **Deliberate Mutant** | `./gradlew test --no-daemon` (returns `"Englishman"`) | Exit 1, failures > 0 | Exit 1, 1 failure, 0 errors | **REJECTED AS EXPECTED** |
| **Empty Selection** | `./gradlew test --no-daemon --tests NoSuchZebraTestClass` | Exit 1, 0 executed | Exit 1, 0 executed | **REJECTED AS EXPECTED** |
