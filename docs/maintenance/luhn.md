# Luhn reference: complexity and scaling

## Supported input sizes

The exercise does not specify a maximum candidate length. The benchmark therefore uses three valid inputs already grounded in the exercise's examples/tests, with 3, 9 and 16 digits after removing spaces:

| Digits | Input | Correctness precondition |
| ---: | --- | --- |
| 3 | `059` | `isValid` must return true |
| 9 | `055444285` | `isValid` must return true |
| 16 | `4539319503436467` | `isValid` must return true |

The benchmark asserts validity before collecting timings. It performs a warm-up, then takes five repetitions of 20,000 calls per input and reports the median nanoseconds per call. The measured values and environment are written to `work/R58-T015/latest-result.json` by the checker.

## Cost of `isValid`

Let `n` be the number of characters in the input. Removing spaces, reversing the sanitized string, scanning each character, and summing the computed digits each require work proportional to `n`. The per-character operations are constant-time, so the overall running time is **O(n)**.

The sanitized string, reversed string, and list of computed digits can each grow proportionally to the input length. Auxiliary space is therefore **O(n)**. The implementation is linear, but it is not constant-space.

The timing probe separates algorithm timing from JVM startup and compilation: compilation occurs before the probe runs, and the median is computed from five in-process repetitions. Microbenchmark values are environment-sensitive and are not evidence of a speedup. The asymptotic conclusion follows from the loops and intermediate data structures, not from extrapolating three measurements.
