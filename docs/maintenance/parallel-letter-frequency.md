# Parallel Letter Frequency: Isolated Reference Runner & Maintenance Verification

## Overview

This maintenance document specifies the runner contract, metadata configuration, path resolution, and verification guarantees for the `parallel-letter-frequency` exercise in the Java track as part of Task R58-T009.

The goal of this runner is to execute the maintained reference implementation against the complete exercise test suite inside an isolated temporary directory, report exact test counts, and propagate failures, while guaranteeing that the unsolved learner starter files in the working tree remain strictly untouched.

---

## File Roles Declared in `.meta/config.json`

The Exercism test runner, CI workflows, and maintenance checkers resolve file paths dynamically from `exercises/practice/parallel-letter-frequency/.meta/config.json`. Files are never located using ad-hoc filesystem searches or hardcoded relative assumptions.

| Role | Configured Path | Purpose & Lifecycle |
|---|---|---|
| `solution` | `src/main/java/ParallelLetterFrequency.java` | **Learner Starter Implementation Stub**: Unsolved template provided to learners. Contains method stubs throwing `UnsupportedOperationException`. Must remain pristine in the working tree. |
| `test` | `src/test/java/ParallelLetterFrequencyTest.java` | **Canonical JUnit 5 Test Suite**: Contains 13 test methods specifying parallel letter counting, case-insensitivity, Unicode handling, and concurrency under large and small text batches. |
| `example` | `.meta/src/reference/java/ParallelLetterFrequency.java` | **Maintained Reference Implementation**: Canonical solution utilizing Java parallel streams (`Stream.parallel()`) and a custom accumulator (`Counts`) to tally letter frequencies. |
| `invalidator` | `build.gradle` | **Build Invalidation Trigger**: Exercise-specific Gradle build script declaring dependencies (`junit-jupiter`, `assertj-core`) and JUnit platform configuration. |

---

## Runner Path Resolution & Discovery Mechanism

1. **Dynamic Resolution via `.meta/config.json`**:
   The runner reads `exercises/practice/parallel-letter-frequency/.meta/config.json` and accesses `config["files"]["solution"]`, `config["files"]["test"]`, and `config["files"]["example"]`.

2. **Path Sanitization & Containment Check**:
   Every configured path is verified to ensure:
   - It is a relative path (not absolute).
   - It contains no parent-traversal segments (`..`) escaping the exercise directory root.
   - The resolved path is contained within `exercises/practice/parallel-letter-frequency/`.
   - The target file actually exists on disk.

3. **Temporary Isolation & Source Substitution**:
   - The exercise directory (including dotfiles such as `.meta`) is copied to a secure temporary directory managed by `tempfile.TemporaryDirectory`. Build caches (`build/`, `.gradle/`) are excluded.
   - The maintained reference source (`.meta/src/reference/java/ParallelLetterFrequency.java`) is copied into scratch `src/main/java/ParallelLetterFrequency.java`.
   - Learner-disabled test annotations (`@Disabled("Remove to run test")`) are stripped **only within the scratch copy**, enabling all 13 canonical tests.
   - The working tree learner starter files are never touched or modified.

4. **Test Execution & Reporting**:
   - The runner invokes `./gradlew test --no-daemon` in the scratch directory.
   - It parses JUnit XML test reports under `build/test-results/test/TEST-*.xml` to extract total tests, passed, failures, errors, skipped, and executed counts (`executed = total - skipped`).
   - Child process return codes and test outcomes are strictly validated.

---

## Distinguishing Maintained Sources from Generated Artifacts

To preserve repository hygiene, human-maintained files must be cleanly distinguished from ephemeral build artifacts and generated files:

| Category | Artifact Path | Origin / Description | Tracked in Git? |
|---|---|---|---|
| **Maintained Source** | `src/main/java/ParallelLetterFrequency.java` | Unsolved starter template with `UnsupportedOperationException` | **Yes** |
| **Maintained Source** | `src/test/java/ParallelLetterFrequencyTest.java` | JUnit 5 test harness with 13 `@Test` `@DisplayName` methods | **Yes** |
| **Maintained Source** | `.meta/src/reference/java/ParallelLetterFrequency.java` | Complete reference implementation using parallel streams | **Yes** |
| **Maintained Source** | `.meta/config.json` | Exercise metadata and file mappings | **Yes** |
| **Maintained Source** | `.meta/tests.toml` | Canonical problem-specifications test tracking (13 UUIDs) | **Yes** |
| **Maintained Source** | `build.gradle` | Exercise Gradle build script | **Yes** |
| **Generated Artifact** | `build/` | Compiled classes, Gradle test reports, and JUnit XML outputs | **No** (ignored) |
| **Generated Artifact** | `.gradle/` | Gradle worker and configuration caches | **No** (ignored) |

---

## Failure-Mode Coverage

The verification suite evaluates three scenarios to ensure the runner accurately discriminates between success, failure, and misconfiguration:

| Scenario | Configuration | Expected Outcome | Verification Assertion |
|---|---|---|---|
| **1. Maintained Reference** | Reference copied to scratch `src/main/java`, all 13 tests enabled. | Success | Exit code `0`, `executed == 13`, `failures == 0`, `errors == 0`, `skipped == 0`. All 13 `@DisplayName` test cases pass. |
| **2. Deliberately Failing Reference** | Reference mutated to return `Collections.emptyMap()` in `countLetters()`. | Failure | Exit code non-zero (`1`), `failures > 0` (9 failing assertions including `large texts`), correctly rejected by runner. |
| **3. Empty Test Selection** | Run with `--tests NoSuchParallelLetterFrequencyTestClass`. | Zero Tests / Error | Exit code non-zero, `executed == 0`, correctly rejected by runner. |

---

## Working Tree Integrity & Cleanup Guarantee

- **Learner File Hashing**: SHA-256 hashes of `src/main/java/ParallelLetterFrequency.java` are computed before any execution, after each scenario, and within a `finally` block. Any difference raises an immediate `AssertionError`.
- **Learner Stub State**: Confirmed to retain `UnsupportedOperationException` throughout.
- **Temporary Cleanup**: All scratch directories are allocated via Python's `tempfile.TemporaryDirectory` context manager. Directory non-existence is explicitly asserted after exit.

---

## Canonical Test Cases & Anchor Case

The suite validates all 13 canonical test cases declared in `.meta/tests.toml` and `ParallelLetterFrequencyTest.java`:

1. `no texts` (`c054d642-c1fa-4234-8007-9339f2337886`)
2. `one text with one letter` (`818031be-49dc-4675-b2f9-c4047f638a2a`)
3. `one text with multiple letters` (`c0b81d1b-940d-4cea-9f49-8445c69c17ae`)
4. `two texts with one letter` (`708ff1e0-f14a-43fd-adb5-e76750dcf108`)
5. `two texts with multiple letters` (`1b5c28bb-4619-4c9d-8db9-a4bb9c3bdca0`)
6. `ignore letter casing` (`6366e2b8-b84c-4334-a047-03a00a656d63`)
7. `ignore whitespace` (`92ebcbb0-9181-4421-a784-f6f5aa79f75b`)
8. `ignore punctuation` (`bc5f4203-00ce-4acc-a5fa-f7b865376fd9`)
9. `ignore numbers` (`68032b8b-346b-4389-a380-e397618f6831`)
10. `Unicode letters` (`aa9f97ac-3961-4af1-88e7-6efed1bfddfd`)
11. `combination of lower- and uppercase letters, punctuation and white space` (`7b1da046-701b-41fc-813e-dcfb5ee51813`)
12. `large texts` (`4727f020-df62-4dcf-99b2-a6e58319cb4f`) — **Anchor case**: tests input text containing `"it's the result of forty years underground! Allow me to indulge my fancy."`
13. `many small texts` (`adf8e57b-8e54-4483-b6b8-8b32c115884c`)

---

## Reproduction

Run the automated verification suite from the repository root:

```bash
# Focused course check entry point:
python3 tools/course_checks/r58-t009.py

# Complete verification check:
python3 work/R58-T009/check.py
```
