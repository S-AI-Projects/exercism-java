# Sum of Multiples maintained files

The exercise file-role map is declared in `exercises/practice/sum-of-multiples/.meta/config.json`. The focused checker parses the `files` object, resolves every declared path relative to the exercise directory, rejects traversal outside that directory, and verifies that each path exists.

| Config role | Declared file | Role and maintenance status |
| --- | --- | --- |
| `solution` | `src/main/java/SumOfMultiples.java` | Learner implementation stub; leave unsolved. |
| `test` | `src/test/java/SumOfMultiplesTest.java` | Exercise test source generated from canonical case metadata; do not edit it directly. |
| `example` | `.meta/src/reference/java/SumOfMultiples.java` | Maintained reference implementation used by the isolated checker. |
| `invalidator` | `build.gradle` | Maintained build file used to invalidate learner builds when needed. |

This exercise currently declares no `editor` role in `config.json`; the checker validates every declared role rather than inventing an editor path.

Canonical test cases are recorded in `.meta/tests.toml`. The checker also verifies that missing solution/reference paths, missing test paths, and paths escaping the exercise are rejected. Run the path and reference checks with:

```sh
python3 work/R58-T038/check.py
```
