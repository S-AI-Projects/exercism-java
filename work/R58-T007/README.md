# Task R58-T007 Evidence: Saddle Points

This directory contains the verification harness and evidence for Task R58-T007 (connecting the `saddle-points` specification to Java language constructs).

## Quick Run

From the repository root:

```bash
python3 work/R58-T007/check.py
# or
python3 tools/course_checks/r58-t007.py
```

## Structure

- `SaddlePointsBoxedPrimitiveExample.java`: Standalone micro-example demonstrating:
  1. Primitive unboxing from `Collections.max` as used in `getRowMax`, evaluating `coordinateValue == rowMax` (`true`).
  2. Contrasting pitfall of comparing boxed `Integer` wrapper objects with `==` outside the $[-128, 127]$ cache (`false`).
- `check.py`: Automated verification suite using Python subprocess and isolated temporary directories:
  1. Resolves paths dynamically from `exercises/practice/saddle-points/.meta/config.json`.
  2. Validates canonical UUIDs and `@DisplayName` annotations from `tests.toml` and `MatrixTest.java`.
  3. Asserts learner starter stub `Matrix.java` remains unsolved (`UnsupportedOperationException`) and pristine.
  4. Copies exercise with dotfiles to a temporary directory, substitutes the reference implementation into `src/main/java`, strips `@Disabled`, and runs `./gradlew test`.
  5. Compiles and executes `SaddlePointsBoxedPrimitiveExample.java`, asserting both output lines (`true` and `false`).
  6. Verifies that `exercises/practice/saddle-points/.docs/hints.md` contains the required guidance, snippet, and pitfall explanation.
  7. Records all test counts, tool versions, and check assertions in `results.json` and `latest-result.json`.
- `PR_DESCRIPTION.md`: Complete Pull Request description ready for submission to `S-AI-Projects/exercism-java`.
- `results.json` / `latest-result.json`: Machine-readable evidence of execution.

## Language Construct Summary

| Candidate Construct | Used by `getRowMax`? | Reason |
|---|---|---|
| **Collection Mutation** | No | `Collections.max` and `List.get` only read list elements; no modifications occur. |
| **Exception Contracts** | No | `getRowMax` does not declare, catch, or specify an exception contract (unlike `getColumnMin`). |
| **Primitive vs. Boxed Values** | **Yes** | `values` is `List<List<Integer>>` (boxed `Integer`). `Collections.max` returns `Integer`, which is automatically unboxed into the primitive `int` return type of `getRowMax`. In `getSaddlePoints()`, both values are primitive `int`s, ensuring `==` performs numeric equality rather than reference identity comparison. |
