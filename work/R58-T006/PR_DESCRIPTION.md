# Pull Request

<!-- Your content goes here: -->
# R58-T006: split-second-stopwatch: compare reference with discrete duration accumulation approach

## Description
Analyzed and compared the maintained reference implementation in `exercises/practice/split-second-stopwatch/.meta/src/reference/java/SplitSecondStopwatch.java` (Continuous Wall-Clock / Epoch Offset Model) with an independently written alternative implementation (Discrete Duration Accumulation Model) for Task R58-T006. Verified both implementations against all 29 tests in `SplitSecondStopwatchTest.java`, including all named anchor cases, achieving 100% agreement. Documented architectural trade-offs, state handling, memory usage, and worked examples without publishing full learner solutions.

## Related Issue
Fixes: #6

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
- `docs/maintenance/split-second-stopwatch.md`:
  - Documented the split-second-stopwatch contract, state transition matrix, and error conditions.
  - Analyzed Approach 1 (Maintained Reference: continuous epoch timestamps `mockTime`, `currentLapStart`, lazy delta subtraction via `switch (state)` in `getCurrentLapTime()`).
  - Analyzed Approach 2 (Alternative: discrete duration accumulation, eager state filtering in `advanceTime()`, branch-free reads in `currentLap()` and `total()`).
  - Formulated a detailed comparison matrix across mathematical modeling, control flow, lap storage, memory overhead, and wall-clock portability.
  - Explained when the alternative is clearer (discrete simulations, turn-based loops, branch-free reads, reduced mutable state) and what extra work/memory it requires (re-formatting `previousLaps()` on demand, inability to passively read continuous hardware clocks).
  - Recorded 100% agreement evidence across all 29 test cases.
- `exercises/practice/split-second-stopwatch/.docs/hints.md`:
  - Added approach guidance explaining the trade-offs between continuous epoch offsets and discrete duration accumulation.
  - Included a step-by-step worked example tracing a runner's interval workout (start -> lap -> pause -> resume) across state transitions.
  - Avoided publishing a full solution listing to maintain learner pedagogical goals.
- `work/R58-T006/AlternativeSplitSecondStopwatch.java`:
  - Created standalone alternative implementation using discrete second counters (`currentLapSeconds`, `totalLapSeconds`, `List<Integer> previousLapDurations`).
- `work/R58-T006/check.py`:
  - Implemented automated verification script using Python `subprocess` and isolated `tempfile` scratch directories.
  - Dynamically resolves paths from `.meta/config.json`.
  - Executes isolated `./gradlew test` runs on both reference and alternative.
  - Verifies child exit codes, test counts, 0 failures, 0 errors, 0 skips, and 100% agreement on all test cases.
  - Confirms working tree learner starter stub remains unsolved (`UnsupportedOperationException`) and unmodified.
- `tools/course_checks/r58-t006.py`: Standard course runner delegating to `work/R58-T006/check.py`.
- `work/R58-T006/results.json` & `latest-result.json`: Recorded execution evidence, tool versions, and test results.
- `work/R58-T006/README.md`: Work directory documentation and execution instructions.

## Screenshots / Recordings
Not applicable — no UI changes.

## Testing
- Automated verification executed via:
  - `python3 work/R58-T006/check.py`
  - `python3 tools/course_checks/r58-t006.py`
- Test results:
  - Reference: 29 executed, 29 passed, 0 failures, 0 errors, 0 skipped.
  - Alternative: 29 executed, 29 passed, 0 failures, 0 errors, 0 skipped.
  - Agreement: 100% agreement across all 29 cases.
- Verified named anchor cases:
  1. `startInitiatesTimeTrackingForCurrentLap()` ("start initiates time tracking for current lap", UUID: `491487b1-593d-423e-a075-aa78d449ff1f`) -> PASSED
  2. `lapAddsCurrentLapToPreviousLaps()` ("lap adds current lap to previous laps", UUID: `091966e3-ed25-4397-908b-8bb0330118f8`) -> PASSED
  3. `supportsVeryLongLaps()` ("supports very long laps", UUID: `0b01751a-cb57-493f-bb86-409de6e84306`) -> PASSED
- Gradle checkstyle and build verified:
  - `./gradlew check` passed cleanly.
- Working tree integrity:
  - `exercises/practice/split-second-stopwatch/src/main/java/SplitSecondStopwatch.java` verified unsolved and unmodified.

## Checklist
- [x] I have tested my changes locally.
- [x] I have added or updated tests, if needed.
- [x] I have updated documentation, if needed.
- [x] I have followed the project's coding guidelines.
- [x] I have run the relevant tests and checks.
- [x] I have addressed previous review feedback, if applicable.

## Additional Notes
- Assigned working branch: `student/e26b07f0710/R58-T006` (and `R58-T006`).
- PR Base Repository: `S-AI-Projects/exercism-java` on `main`.

<!-- DO NOT EDIT BELOW THIS LINE! -->
---

Reviewer Resources:

[Track Policies](https://github.com/exercism/java/blob/main/POLICIES.md#event-checklist)
