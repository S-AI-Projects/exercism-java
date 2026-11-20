# Pull Request

<!-- Your content goes here: -->
# R58-T005: knapsack: computational cost analysis and domain benchmarking

## Description
Analyzed and explained the computational cost of the reference implementation in `exercises/practice/knapsack/.meta/src/reference/java/Knapsack.java` for Task R58-T005. Defined input size in terms of item records ($N$) and capacity bound ($W$), evaluated three valid domain input sizes from the canonical test suite, counted operations and branches across all cases, executed empirical micro-benchmarking reporting medians over 7 repetitions under constant conditions after asserting correctness, and distinguished pure algorithm work from process startup and compilation overhead.

## Related Issue
Fixes: #5

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
- `exercises/practice/knapsack/.meta/src/reference/java/Knapsack.java`:
  - Added documentation explaining $\Theta(N \cdot W)$ time and space complexity and memoization grid structure.
  - Preserved exact public API contract `int maximumValue(int maximumWeight, List<Item> items)`.
- `docs/maintenance/knapsack.md`:
  - Detailed the input size definition in terms of item records ($N$) and carrying capacity ($W$).
  - Constructed an exact branch and operation count table for the reference 2D DP algorithm.
  - Recorded empirical micro-benchmarking measurements across 3 valid domain sizes: Small (`example knapsack`, 55 cells, 250 ns), Medium (`8 items`, 945 cells, 1,250 ns), and Large (`15 items`, 12,016 cells, 13,875 ns).
  - Provided a comparative analysis distinguishing pure algorithm execution ($\approx 0.25 - 13.88\ \mu\text{s}$) from JVM process startup, reflection, and Gradle test build time ($\approx 2.7\ \text{s}$).
- `work/R58-T005/original/Knapsack.java`: Preserved pristine snapshot of original reference for baseline comparison.
- `work/R58-T005/check.py`: Implemented automated verification script using Python subprocess and isolated temporary directories to run `./gradlew test` and in-process timing.
- `tools/course_checks/r58-t005.py`: Added course check runner entry point.
- `work/R58-T005/results.json` and `latest-result.json`: Recorded verification results, exact operation counts, and tool versions.
- `work/R58-T005/README.md`: Documented task purpose, structure, and execution instructions.

## Screenshots / Recordings
Not applicable — no UI changes.

## Testing
- Automated verification executed via `python3 work/R58-T005/check.py` and `python3 tools/course_checks/r58-t005.py`.
- Gradle test suite executed via `./gradlew test` in an isolated scratch directory with all tests enabled:
  - 7 executed, 7 passed, 0 failures, 0 errors, 0 skipped.
- Gradle checkstyle and build validated cleanly via `./gradlew check`:
  - `:practice:knapsack:checkstyleMain` PASSED
  - `:practice:knapsack:checkstyleTest` PASSED
  - `:practice:knapsack:test` PASSED
- Correctness asserted for all three domain sizes prior to empirical timing.
- Working tree learner starter stub `exercises/practice/knapsack/src/main/java/Knapsack.java` verified to remain unsolved (`UnsupportedOperationException`) and unmodified.

## Checklist
- [x] I have tested my changes locally.
- [x] I have added or updated tests, if needed.
- [x] I have updated documentation, if needed.
- [x] I have followed the project's coding guidelines.
- [x] I have run the relevant tests and checks.
- [x] I have addressed previous review feedback, if applicable.

## Additional Notes
- Assigned working branch: `student/e26b07f0710/R58-T005` (and `R58-T005` / `student/e26b07f0710-R58-T005`).
- Base repository: `S-AI-Projects/exercism-java` on `main`.

<!-- DO NOT EDIT BELOW THIS LINE! -->
---

Reviewer Resources:

[Track Policies](https://github.com/exercism/java/blob/main/POLICIES.md#event-checklist)
