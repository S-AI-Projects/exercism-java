# Pull Request

## Summary
- Document the canonical Configlet-managed test metadata and the manually maintained Java JUnit source.
- Map three canonical UUIDs to their JUnit methods and expected outputs.
- Add focused Configlet/source reproducibility and isolated reference-test checks.

## Verification
- Command: `python3 work/R58-T012/check.py`
- Result details, executed test counts, failure/skip counts, and tool versions: `work/R58-T012/latest-result.json`
- The result file is generated and pushed by the batch verification script after the task checker passes.
- Learner starter files are preserved by the isolated checker.

Closes #12

<!-- DO NOT EDIT BELOW THIS LINE! -->
---

Reviewer Resources:

[Track Policies](https://github.com/exercism/java/blob/main/POLICIES.md#event-checklist)
