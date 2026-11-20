# Work Directory for Task R58-T005

## Exercise: `knapsack`

This directory contains the verification harness, original reference snapshot, and recorded evidence for Task R58-T005.

### Purpose

The task verifies and explains the computational cost of the reference implementation for the `knapsack` practice exercise:
1. Dynamic path resolution from `exercises/practice/knapsack/.meta/config.json`.
2. Clean mapping and validation of canonical test cases between `exercises/practice/knapsack/.meta/tests.toml` and `exercises/practice/knapsack/src/test/java/KnapsackTest.java` (7 active cases).
3. Maintenance of the learner starter stub (`exercises/practice/knapsack/src/main/java/Knapsack.java`), which must remain unsolved (`UnsupportedOperationException`) and unchanged.
4. Correctness of the maintained reference implementation (`exercises/practice/knapsack/.meta/src/reference/java/Knapsack.java`), passing all 7 tests in an isolated temporary environment.
5. In-depth computational cost explanation:
   - Defining input size in terms of item records ($N$) and capacity limit ($W$), with an allocated state grid of $(N+1) \times (W+1)$ cells.
   - Counting executed operations and branches across three valid input sizes from the exercise domain: Small (`example knapsack`, $N=4, W=10$), Medium (`8 items`, $N=8, W=104$), and Large (`15 items`, $N=15, W=750$).
   - Formulating an exact operation and branch table.
   - Performing in-process timing with at least 5 repetitions (7 executed) after asserting correctness, holding input and environment constant, and reporting median times.
   - Explicitly distinguishing pure algorithm work (microseconds) from process-startup, class loading, and Gradle compilation overhead (seconds).
6. Comprehensive maintenance documentation in `docs/maintenance/knapsack.md`.

### Running the Checks

To execute the verification script directly:
```bash
python3 work/R58-T005/check.py
```

Or via the course check harness:
```bash
python3 tools/course_checks/r58-t005.py
```

### Artifacts

- `original/Knapsack.java`: Baseline original reference implementation snapshot.
- `check.py`: Automated verification script using Python subprocess and isolated temp directories.
- `results.json`: Complete execution record including tool versions, test counts, named case statuses, operation counts, and timing data.
- `latest-result.json`: Mirror of the latest check results for automated grading.
- `PR_DESCRIPTION.md`: Standardized pull request description matching the required template.
