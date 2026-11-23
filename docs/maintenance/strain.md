# Strain `keep` scaling note

The maintained implementation is `exercises/practice/strain/.meta/src/reference/java/Strain.java`; the learner stub is `src/main/java/Strain.java`. Run the reference tests and measurement with:

```sh
python3 work/R58-T035/check.py
```

The checker uses valid integer lists of 1,000, 10,000, and 100,000 elements. It verifies the retained values before measuring and counts predicate calls. Since `keep` delegates to one pass over the input, the expected predicate-call counts are exactly the input lengths. One recorded run on OpenJDK 21.0.12.1 produced:

| Input size | Predicate calls | Retained values | Median time (ns) |
| ---: | ---: | ---: | ---: |
| 1,000 | 1,000 | 500 | 48,209 |
| 10,000 | 10,000 | 5,000 | 336,458 |
| 100,000 | 100,000 | 50,000 | 741,583 |

The checker writes the latest run to `work/R58-T035/benchmark.csv`; timing values will vary by runtime and machine.

The measurements characterize this machine and runtime only. JVM startup, compilation, garbage collection, and timing noise affect elapsed time; the operation counts are the stronger evidence for linear scaling. No comparative speedup is claimed.
