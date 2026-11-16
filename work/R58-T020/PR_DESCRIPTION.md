# Pull Request

## Summary
- Add a decision table for overwrite on non-full/full buffers, overwrite after a read, and clear followed by wrap-around.
- Explain the specified empty-read and full-write exceptions without inventing behavior for unsupported capacities.
- Add an executable contract probe and isolated reference-test checker.

## Verification
- Command: `python3 work/R58-T020/check.py`
- Result details, executed test counts, failure/skip counts, and tool versions: `work/R58-T020/latest-result.json`
- The result file is generated and pushed by the batch verification script after the task checker passes.
- Learner starter files are preserved by the isolated checker.

Closes #20

<!-- DO NOT EDIT BELOW THIS LINE! -->
---

Reviewer Resources:

[Track Policies](https://github.com/exercism/java/blob/main/POLICIES.md#event-checklist)
