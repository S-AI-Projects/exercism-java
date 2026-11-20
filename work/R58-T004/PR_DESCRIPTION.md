# Pull Request

<!-- Your content goes here: -->
# R58-T004: yacht: clarify reference implementation readability and frequency calculation

## Description
Refactored the reference implementation in `exercises/practice/yacht/.meta/src/reference/java/Yacht.java` for Task R58-T004 to improve readability while preserving the exact public interface and canonical behavior. Renamed ambiguous local state `occurrences` to `dieFaceCounts`, extracted duplicate frequency stream grouping into `dieFrequencies()`, clarified lambda parameter `entry`, and documented domain invariants.

## Related Issue
Fixes: #4

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
- `exercises/practice/yacht/.meta/src/reference/java/Yacht.java`:
  - Extracted helper method `private Map<Integer, Long> dieFrequencies()` to eliminate duplicate stream grouping across `FULL_HOUSE` and `FOUR_OF_A_KIND`.
  - Renamed ambiguous local state variable `Collection<Long> occurrences` to `Collection<Long> dieFaceCounts` to distinguish frequency counts from observed dice values.
  - Clarified lambda parameter in `FOUR_OF_A_KIND` from `x` to `entry`.
  - Documented exercise-specific invariants for dice rolls (5 dice, 1..6 faces) and category rules (Full House 3+2, Four of a Kind >= 4).
  - Preserved constructor `Yacht(int[], YachtCategory)` and `score()` contract.
- `docs/maintenance/yacht.md`: Added comprehensive maintenance documentation, traced local state for baseline cases, and verified before/after parity.
- `work/R58-T004/original/Yacht.java`: Preserved pristine snapshot of original reference for reproducible before/after comparison.
- `work/R58-T004/check.py`: Implemented verification script using Python subprocess and isolated temporary directories to run `./gradlew test` on both before/after implementations.
- `tools/course_checks/r58-t004.py`: Added course check runner entry point.
- `work/R58-T004/results.json` and `latest-result.json`: Recorded verification results and tool versions.

## Screenshots / Recordings
Not applicable — no UI changes.

## Testing
- Automated test suite executed via `python3 work/R58-T004/check.py` and `python3 tools/course_checks/r58-t004.py`.
- Both original reference and refactored reference executed via `./gradlew test` in isolated scratch directories with all tests enabled:
  - 29 executed, 29 passed, 0 failures, 0 errors, 0 skipped.
  - Parity confirmed across all 29 canonical test cases.
- Gradle checkstyle validated cleanly via `./exercises/gradlew -p exercises ":practice:yacht:check" --exclude-task test`.
- Verified working tree learner starter stub `exercises/practice/yacht/src/main/java/Yacht.java` remains unsolved (`UnsupportedOperationException`) and completely unmodified.

## Checklist
- [x] I have tested my changes locally.
- [x] I have added or updated tests, if needed.
- [x] I have updated documentation, if needed.
- [x] I have followed the project's coding guidelines.
- [x] I have run the relevant tests and checks.
- [x] I have addressed previous review feedback, if applicable.

## Additional Notes
- Assigned working branch: `student/e26b07f0710/R58-T004` (and `R58-T004` / `student/e26b07f0710-R58-T004`).
- Base repository: `S-AI-Projects/exercism-java` on `main`.

<!-- DO NOT EDIT BELOW THIS LINE! -->
---

Reviewer Resources:

[Track Policies](https://github.com/exercism/java/blob/main/POLICIES.md#event-checklist)
