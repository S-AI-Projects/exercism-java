# Largest-series-product: maintained file map

## File roles from `.meta/config.json`

The runner reads the `files` object in `exercises/practice/largest-series-product/.meta/config.json`. It does not guess files by searching for matching names.

| Role | Configured path | Purpose |
| --- | --- | --- |
| `solution` | `src/main/java/LargestSeriesProductCalculator.java` | Learner starter implementation |
| `test` | `src/test/java/LargestSeriesProductCalculatorTest.java` | JUnit contract tests |
| `example` | `.meta/src/reference/java/LargestSeriesProductCalculator.java` | Maintained reference implementation |
| `invalidator` | `build.gradle` | Exercise build configuration |

All configured paths must be relative to this exercise directory, must remain inside it after resolution, and must name existing files. The runner resolves these entries from the JSON `files` object. The JUnit source is compiled as the test source set; the maintained reference is copied into the scratch `src/main/java` source set for local reference testing. The learner starter file remains untouched.

## Reproduction

```bash
python3 tools/course_checks/r58-t018.py
python3 work/R58-T018/check.py
```

The focused metadata checker first validates the real configuration, then deliberately tests three invalid fixtures: a missing reference file, a missing test file, and a parent-directory path that escapes the exercise. Each fixture must be rejected for the intended reason.

The full task checker also runs the enabled JUnit suite against the reference in an isolated temporary copy and records the executed test count and tool environment.
