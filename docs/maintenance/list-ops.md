# ListOps reference readability change

`exercises/practice/list-ops/.meta/src/reference/java/ListOps.java` is the maintained reference. `src/main/java/ListOps.java` remains the learner stub; `src/test/java/ListOpsTest.java` contains the exercise tests and `.meta/tests.toml` contains canonical case metadata.

Run the focused coursework check with:

```sh
python3 work/R58-T034/check.py
```

The change is limited to `foldRight`: `acc` and `i` are renamed to `accumulator`, `index`, and `element`, and a comment states the right-to-left folding invariant. The function still passes each element as the first argument and the accumulated value as the second, preserving the public API and ordering behavior.

The checker compiles a small parity harness against the reference from `main` and the refactored reference, compares their outputs, then runs the exercise tests against the refactored reference in a temporary copy.
