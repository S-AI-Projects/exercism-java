# Pull Request

## Summary
- Add a reusable runner that copies the exercise, substitutes the reference only in a temporary copy, and reports real JUnit counts.
- Exercise success, deliberate assertion failure, and zero-test selection behavior.
- Verify learner-source hashes and temporary-directory cleanup.

## Verification
- Command: `python3 work/R58-T019/check.py`
- Result details, executed test counts, failure/skip counts, and tool versions: `work/R58-T019/latest-result.json`
- The result file is generated and pushed by the batch verification script after the task checker passes.
- Learner starter files are preserved by the isolated checker.

Closes #19

<!-- DO NOT EDIT BELOW THIS LINE! -->
---

Reviewer Resources:

[Track Policies](https://github.com/exercism/java/blob/main/POLICIES.md#event-checklist)
