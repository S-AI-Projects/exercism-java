# Gigasecond mutation check

The maintained reference is `exercises/practice/gigasecond/.meta/src/reference/java/Gigasecond.java`; the learner stub is `src/main/java/Gigasecond.java`. The Java test source is `src/test/java/GigasecondTest.java`, with canonical case metadata in `.meta/tests.toml`.

Run the focused reference and mutation check with:

```sh
python3 work/R58-T033/check.py
```

The check copies the exercise to a temporary directory, installs the reference in the copy, and first runs the original. It then changes only the duration in that temporary reference from 1,000,000,000 to 999,999,999 seconds. The existing `modernTime` assertion rejects this deliberate off-by-one mutant: input `2011-04-25` must produce `2043-01-01T01:46:40`, while the mutant produces `2043-01-01T01:46:39`. The repository reference itself remains unchanged by the mutation check.
