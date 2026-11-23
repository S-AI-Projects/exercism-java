# Minesweeper isolated reference runner

Run the focused runner from the repository root:

```sh
python3 work/R58-T039/check.py
```

The runner reads `files.solution`, `files.test`, and `files.example` from `exercises/practice/minesweeper/.meta/config.json`. It copies the complete exercise, including hidden metadata, into a temporary directory; substitutes the reference only for the copied learner source; runs the copied Gradle wrapper; counts JUnit XML test cases; and fails on a child error, test failure, or zero-test run. A temporary reference mutant and an empty test selection verify those error paths. The original learner files are SHA-256 checked before and after each run.

The full three-scenario check can also be run directly with `python3 tools/course_checks/r58-t039.py`. It requires Python 3, a JDK supported by the repository build, and the supplied Gradle wrapper. The check runs only against scratch copies and removes them automatically.
