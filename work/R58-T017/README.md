# R58-T017 evidence

Run from the repository root:

```bash
python3 work/R58-T017/check.py
```

The checker runs the enabled Raindrops JUnit suite against the maintained reference in an isolated temporary copy. It compiles and executes the standalone primitive-`int` modulo example and asserts its two output lines: `true` for the remainder-based divisibility check and `false` for the deliberately incorrect division-based check.

The learner solution source is hashed before and after verification. Tool versions, test counts and the micro-example output are recorded in `latest-result.json` when run.

No local execution result is claimed in this commit.
