# Pull Request

<!-- Your content goes here: -->
# R58-T007: saddle-points: explain primitive vs boxed values in getRowMax and record verification evidence

## Description
Provides learner guidance connecting the `saddle-points` exercise specification to Java language constructs for Task R58-T007. Examined collection mutation, primitive versus boxed values, and exception contracts; identified that `getRowMax` in the reference implementation specifically relies on automatic unboxing from boxed `Integer` to primitive `int`. Developed a standalone micro-example demonstrating correct primitive value comparison alongside an exercise-relevant pitfall (boxed `Integer` reference identity comparison with `==` failing outside the $[-128, 127]$ cache). Implemented an automated verification check that exercises the full canonical test suite in an isolated scratch directory without modifying the working tree learner stub.

## Related Issue
Fixes: #7

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
- `exercises/practice/saddle-points/.docs/hints.md`:
  - Added learner guidance connecting the saddle points domain specification to Java's `List<List<Integer>>` representation.
  - Examined collection mutation, exception contracts, and primitive vs boxed values; selected primitive vs boxed values as the construct used by `getRowMax`.
  - Provided a standalone snippet demonstrating `Collections.max` auto-unboxing to `int` and numeric comparison with `==` (`true`).
  - Contrasted with the boxed `Integer` pitfall where comparing instances representing 128 with `==` yields `false` due to object reference identity comparison and the JLS §5.1.7 Integer cache boundary.
- `docs/maintenance/saddle-points.md`:
  - Documented the construct examination, contract analysis, pitfall mechanics, and complete test suite verification table across all 9 canonical cases.
- `work/R58-T007/SaddlePointsBoxedPrimitiveExample.java`:
  - Standalone executable snippet producing outputs `true` and `false` as asserted by the checker.
- `work/R58-T007/check.py`:
  - Automated verification script using Python subprocess and isolated temporary directory.
  - Resolves solution, test, and example paths dynamically from `config.json`.
  - Asserts that all 9 canonical test cases pass against the reference implementation.
  - Asserts that the learner starter stub remains unsolved (`UnsupportedOperationException`) and pristine.
  - Asserts micro-example outputs `["true", "false"]` matching published hint.
  - Records tool versions, inputs, and results.
- `tools/course_checks/r58-t007.py`:
  - Course verification entry point delegating to `work/R58-T007/check.py`.
- `work/R58-T007/README.md`:
  - Execution instructions and task structure documentation.
- `work/R58-T007/results.json` and `latest-result.json`:
  - Recorded verification results and tool versions.

## Screenshots / Recordings
Not applicable — no UI changes.

## Testing
- Automated verification executed via `python3 work/R58-T007/check.py` and `python3 tools/course_checks/r58-t007.py`.
- Maintained reference executed in an isolated temporary directory via `./gradlew test --no-daemon`:
  - 9 tests executed, 9 passed, 0 failures, 0 errors, 0 skipped.
  - All 9 named canonical cases confirmed passing.
- Micro-example compiled with `javac` and executed with `java`:
  - Output verified: `['true', 'false']`.
- Published hints confirmed in agreement with micro-example and reference constructs.
- Working tree learner starter stub `exercises/practice/saddle-points/src/main/java/Matrix.java` verified untouched and unsolved (`UnsupportedOperationException`).

## Checklist
- [x] I have tested my changes locally.
- [x] I have added or updated tests, if needed.
- [x] I have updated documentation, if needed.
- [x] I have followed the project's coding guidelines.
- [x] I have run the relevant tests and checks.
- [x] I have addressed previous review feedback, if applicable.

## Additional Notes
- Assigned working branch: `student/e26b07f0710/R58-007` (and `R58-T007` / `student/e26b07f0710-R58-T007`).
- Base repository: `S-AI-Projects/exercism-java` on `main`.

<!-- DO NOT EDIT BELOW THIS LINE! -->
---

Reviewer Resources:

[Track Policies](https://github.com/exercism/java/blob/main/POLICIES.md#event-checklist)
