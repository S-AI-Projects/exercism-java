# Pull Request

## Summary
- Rename ambiguous board dimension and player-connectivity state in the maintained reference.
- Explain the 1x1 target-edge invariant without changing the public API or connectivity algorithm.
- Add a before/after isolated test comparison using the original reference snapshot.

## Verification
- Command: `python3 work/R58-T014/check.py`
- Result details, executed test counts, failure/skip counts, and tool versions: `work/R58-T014/latest-result.json`
- The result file is generated and pushed by the batch verification script after the task checker passes.
- Learner starter files are preserved by the isolated checker.

Closes #14

<!-- DO NOT EDIT BELOW THIS LINE! -->
---

Reviewer Resources:

[Track Policies](https://github.com/exercism/java/blob/main/POLICIES.md#event-checklist)
