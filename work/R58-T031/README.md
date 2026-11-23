# R58-T031 evidence

This check parses the canonical TOML, verifies the ten-case include/exclude counts and the three UUID-to-test rationales, then runs the enabled Java tests against the maintained reference in an isolated temporary copy. It records the test count, tool versions, and learner-file integrity in this directory.

Command: `python3 work/R58-T031/check.py`
