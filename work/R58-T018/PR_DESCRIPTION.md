# Pull Request

## Summary
- Document the solution, test, example, and invalidator paths declared in config.json.
- Add a focused checker that resolves configured paths safely and rejects missing or escaping paths.
- Verify the real metadata and run the reference tests in an isolated copy.

## Verification
- Command: `python3 work/R58-T018/check.py`
- Result details, executed test counts, failure/skip counts, and tool versions: `work/R58-T018/latest-result.json`
- The result file is generated and pushed by the batch verification script after the task checker passes.
- Learner starter files are preserved by the isolated checker.

Closes #18

<!-- DO NOT EDIT BELOW THIS LINE! -->
---

Reviewer Resources:

[Track Policies](https://github.com/exercism/java/blob/main/POLICIES.md#event-checklist)
