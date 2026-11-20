# Intergalactic Transmission test runner

Run the maintained reference test suite in an isolated exercise copy with:

```sh
python3 work/R58-T029/check.py
```

The focused runner is `tools/course_checks/r58-t029.py`. It reads the
`solution`, `test`, and `example` paths from
`exercises/practice/intergalactic-transmission/.meta/config.json`, copies the
exercise including hidden files to a temporary directory, and writes the
maintained example source into the copied solution path. Gradle runs there, so
the learner starter files in the working tree stay unchanged. It reports the
total, skipped, and executed JUnit case counts and returns a failure for a
non-zero Gradle exit, a reported test failure, or zero executed tests.

The repository check exercises four paths: the real reference, a deliberately
incorrect reference, a test source with no selected tests, and an interrupted
run. It records learner-file hashes before and after each run and verifies
temporary-directory cleanup, including on failure and interruption.

Requirements: Python 3, a JDK compatible with the exercise `build.gradle`, and
the supplied Gradle wrapper. The wrapper may need network access the first time
it downloads its configured Gradle distribution and dependencies.
