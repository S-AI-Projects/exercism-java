# Pull Request

## Summary
- Add a debugging hint explaining seven-bit payload groups and the continuation bit.
- Record the smallest multi-byte diagnostic input, expected bytes, deliberate six-bit mutant, and rejecting canonical test.
- Add an isolated checker that verifies the original reference and proves the mutant is rejected.

## Verification
- Command: `python3 work/R58-T013/check.py`
- Result details, executed test counts, failure/skip counts, and tool versions: `work/R58-T013/latest-result.json`
- The result file is generated and pushed by the batch verification script after the task checker passes.
- Learner starter files are preserved by the isolated checker.

Closes #13

<!-- DO NOT EDIT BELOW THIS LINE! -->
---

Reviewer Resources:

[Track Policies](https://github.com/exercism/java/blob/main/POLICIES.md#event-checklist)
