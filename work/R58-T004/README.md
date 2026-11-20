# Work Directory for Task R58-T004

## Exercise: `yacht`

This directory contains the verification harness, original reference snapshot, and recorded evidence for Task R58-T004.

### Purpose

The task verifies:
1. Dynamic path resolution from `exercises/practice/yacht/.meta/config.json`.
2. Clean mapping of canonical test cases between `exercises/practice/yacht/.meta/tests.toml` and `exercises/practice/yacht/src/test/java/YachtTest.java` (all 29 cases).
3. Maintenance of the learner starter stub (`exercises/practice/yacht/src/main/java/Yacht.java`), which must remain unsolved (`UnsupportedOperationException`) and unchanged.
4. Correctness of the maintained reference implementation (`exercises/practice/yacht/.meta/src/reference/java/Yacht.java`), passing all 29 tests in an isolated temporary environment.
5. Scoped readability improvements in `Yacht.java`:
   - Renaming ambiguous local state `occurrences` -> `dieFaceCounts` in `case FULL_HOUSE`.
   - Extracting coherent calculation `private Map<Integer, Long> dieFrequencies()` to eliminate duplicate frequency stream grouping across `FULL_HOUSE` and `FOUR_OF_A_KIND`.
   - Clarifying lambda parameter `x` -> `entry` in `FOUR_OF_A_KIND`.
   - Documenting domain invariants (5 dice, faces 1..6, Full House 3+2 rule, Four of a Kind 4*face rule).
   - Preserving exact constructor signature, `score()` return type, and behavioral ordering.
6. Before/after equivalence: Both the original snapshot (`work/R58-T004/original/Yacht.java`) and the refactored reference pass the identical enabled test suite with matching test counts.
7. Complete documentation in `docs/maintenance/yacht.md`.

### Running the Checks

To execute the verification script directly:
```bash
python3 work/R58-T004/check.py
```

Or via the course check harness:
```bash
python3 tools/course_checks/r58-t004.py
```

### Artifacts

- `original/Yacht.java`: Baseline original reference implementation snapshot.
- `check.py`: Automated verification script using Python subprocess and isolated temp directories.
- `results.json`: Complete execution record including tool versions, test counts, named case statuses, and diff analysis.
- `latest-result.json`: Mirror of the latest check results for automated grading.
- `PR_DESCRIPTION.md`: Standardized pull request description matching the required template.
