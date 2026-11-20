# Work Directory for Task R58-T006

## Exercise: `split-second-stopwatch`

This directory contains the alternative implementation, verification harness, and recorded evidence for Task R58-T006.

### Purpose

The task compares the maintained reference technique in `exercises/practice/split-second-stopwatch/.meta/src/reference/java/SplitSecondStopwatch.java` with an independently written alternative for the same contract:
1. Dynamic path resolution from `exercises/practice/split-second-stopwatch/.meta/config.json`.
2. Validation of all 29 canonical test cases between `exercises/practice/split-second-stopwatch/.meta/tests.toml` and `exercises/practice/split-second-stopwatch/src/test/java/SplitSecondStopwatchTest.java`.
3. Preservation of the learner starter stub (`exercises/practice/split-second-stopwatch/src/main/java/SplitSecondStopwatch.java`), which remains unsolved (`UnsupportedOperationException`) and unmodified.
4. Evaluation of Approach 1 (Maintained Reference: Continuous Wall-Clock / Epoch Offset Model) passing all 29 tests in an isolated scratch directory.
5. Implementation of Approach 2 (`AlternativeSplitSecondStopwatch.java`: Discrete Duration Accumulation Model) passing all 29 tests with 100% agreement.
6. Documentation of architectural trade-offs, state handling, memory overhead, and worked examples in:
   - `docs/maintenance/split-second-stopwatch.md`
   - `exercises/practice/split-second-stopwatch/.docs/hints.md`

### Running the Checks

To execute the verification script directly:
```bash
python3 work/R58-T006/check.py
```

Or via the course check harness:
```bash
python3 tools/course_checks/r58-t006.py
```

### Artifacts

- `AlternativeSplitSecondStopwatch.java`: Independently written discrete duration accumulation alternative.
- `check.py`: Automated verification script using Python subprocess and isolated temporary directories.
- `results.json`: Complete execution record including tool versions, test counts, named case statuses, and agreement evidence.
- `latest-result.json`: Mirror of the latest check results for automated grading.
- `PR_DESCRIPTION.md`: Pull request description formatted for submission to `S-AI-Projects/exercism-java`.
