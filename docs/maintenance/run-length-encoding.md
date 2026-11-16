# Run-length-encoding: isolated reference runner

## Runner contract

The task runner reads the exercise's `.meta/config.json` and uses its `files.solution`, `files.test`, and `files.example` entries. It copies the exercise, including dotfiles, into a temporary directory, copies the configured reference source into the scratch `src/main/java` source set, and enables the learner-disabled JUnit cases only in the temporary test copy. It invokes the supplied Gradle wrapper and reads the JUnit XML reports to distinguish executed, skipped, failed and errored tests.

The learner solution source in the working tree is never overwritten. Temporary directories are managed with Python's `TemporaryDirectory`, so they are removed after normal completion or exceptions.

## Failure-mode coverage

The focused checker exercises three outcomes:

| Scenario | Expected runner behavior |
| --- | --- |
| Maintained reference | Accept only when Gradle exits successfully and at least one test executes with no skips, failures or errors |
| Deliberately broken empty-input branch | Reject because the enabled `encodeEmpty` assertion fails |
| Test filter matching no test class | Reject because the executed test count is zero or Gradle reports the empty selection as an error |

It hashes the configured learner solution file before and after all three runs and requires the hashes to match.

## Reproduction

```bash
python3 work/R58-T019/check.py
```

The command invokes the reusable focused runner at `tools/course_checks/r58-t019.py`. It writes the exact run statuses, test counts, environment and cleanup/hash checks to `work/R58-T019/latest-result.json`.
