# Isogram Exercise Maintenance

## Overview

This document describes the test generation route, maintenance strategy, and canonical case mapping
for the `isogram` practice exercise in the Java track.

> [!IMPORTANT]
> The test file `exercises/practice/isogram/src/test/java/IsogramCheckerTest.java` is **hand-maintained**
> in this track. There is no per-exercise Jinja template or track-level generator script for `isogram`.
> Test cases are authored directly against the canonical specification in
> [problem-specifications/exercises/isogram/canonical-data.json](https://github.com/exercism/problem-specifications/blob/main/exercises/isogram/canonical-data.json).

---

## Test Source and Maintenance Strategy

| File | Maintenance Method | Description |
|---|---|---|
| `src/test/java/IsogramCheckerTest.java` | **Hand-maintained** | Authored by Java track maintainers using JUnit 5 and AssertJ. Uses `@DisplayName` matching canonical descriptions. |
| `.meta/tests.toml` | **Tool-synced (`configlet`)** | Track-level TOML manifest recording canonical UUIDs and descriptions from `problem-specifications`. |
| `.meta/src/reference/java/IsogramChecker.java` | **Hand-maintained** | Track reference implementation used to verify test suite validity. |
| `src/main/java/IsogramChecker.java` | **Hand-maintained** | Starter stub for learners containing `UnsupportedOperationException`. |

---

## Reproduction & Generation Commands

Since no template generator exists for `isogram`, the test file is hand-maintained.
To synchronize `.meta/tests.toml` with the upstream canonical specification from `problem-specifications`, run:

```bash
bin/fetch-configlet
./bin/configlet sync --tests --exercise isogram
```

To run the automated verification suite confirming canonical case coverage, learner stub integrity,
round-trip consistency, and test execution against the reference solution, run:

```bash
python3 work/R58-T002/check.py
```

---

## Canonical Case Mapping (14 of 14 cases)

All 14 canonical cases defined in `problem-specifications` are included in the Java track's
`.meta/tests.toml` and implemented in `IsogramCheckerTest.java`. There are no excluded or missing cases.

| # | Canonical UUID | Description (`tests.toml`) | Java Test Method | `@DisplayName` | Expected |
|---|---|---|---|---|---|
| 1 | `a0e97d2d-669e-47c7-8134-518a1e2c4555` | empty string | `testEmptyString()` | `"empty string"` | `true` |
| 2 | `9a001b50-f194-4143-bc29-2af5ec1ef652` | isogram with only lower case characters | `testLowercaseIsogram()` | `"isogram with only lower case characters"` | `true` |
| 3 | `8ddb0ca3-276e-4f8b-89da-d95d5bae78a4` | word with one duplicated character | `testNotIsogram()` | `"word with one duplicated character"` | `false` |
| 4 | `6450b333-cbc2-4b24-a723-0b459b34fe18` | word with one duplicated character from the end of the alphabet | `testDuplicateEndAlphabet()` | `"word with one duplicated character from the end of the alphabet"` | `false` |
| 5 | `a15ff557-dd04-4764-99e7-02cc1a385863` | longest reported english isogram | `testMediumLongIsogram()` | `"longest reported english isogram"` | `true` |
| 6 | `f1a7f6c7-a42f-4915-91d7-35b2ea11c92e` | word with duplicated character in mixed case | `testCaseInsensitive()` | `"word with duplicated character in mixed case"` | `false` |
| 7 | `14a4f3c1-3b47-4695-b645-53d328298942` | word with duplicated character in mixed case, lowercase first | `testDuplicateMixedCase()` | `"word with duplicated character in mixed case, lowercase first"` | `false` |
| 8 | `423b850c-7090-4a8a-b057-97f1cadd7c42` | hypothetical isogrammic word with hyphen | `testIsogramWithHyphen()` | `"hypothetical isogrammic word with hyphen"` | `true` |
| 9 | `93dbeaa0-3c5a-45c2-8b25-428b8eacd4f2` | hypothetical word with duplicated character following hyphen | `testIsogramWithDuplicatedCharAfterHyphen()` | `"hypothetical word with duplicated character following hyphen"` | `false` |
| 10 | `36b30e5c-173f-49c6-a515-93a3e825553f` | isogram with duplicated hyphen | `testIsogramWithDuplicatedHyphen()` | `"isogram with duplicated hyphen"` | `true` |
| 11 | `cdabafa0-c9f4-4c1f-b142-689c6ee17d93` | made-up name that is an isogram | `testMadeUpNameThatIsAnIsogram()` | `"made-up name that is an isogram"` | `true` |
| 12 | `5fc61048-d74e-48fd-bc34-abfc21552d4d` | duplicated character in the middle | `testDuplicatedCharacterInTheMiddleIsNotIsogram()` | `"duplicated character in the middle"` | `false` |
| 13 | `310ac53d-8932-47bc-bbb4-b2b94f25a83e` | same first and last characters | `testSameFirstAndLast()` | `"same first and last characters"` | `false` |
| 14 | `0d0b8644-0a1e-4a31-a432-2b3ee270d847` | word with duplicated character and with two hyphens | `testDuplicatedCharacterAndTwoHyphens()` | `"word with duplicated character and with two hyphens"` | `false` |

---

## Named Anchor Cases (Task R58-T002)

The three named anchor cases specified for Task R58-T002 are the foundational cases in the test suite:

### 1. Case: `testEmptyString()`
- **Canonical UUID**: `a0e97d2d-669e-47c7-8134-518a1e2c4555`
- **Method Name**: `public void testEmptyString()`
- **Annotations**: `@Test`, `@DisplayName("empty string")`
- **Input**: `""`
- **Expected Result**: `true`
- **Java Operation in Reference Solution**:
  In `IsogramChecker.java`:
  ```java
  String[] words = word.split(" ");
  String newWord = concat(words);
  words = newWord.split("-");
  newWord = concat(words).toLowerCase();
  for (int i = 0; i < newWord.length(); i++) {
      charSet.add(newWord.charAt(i));
  }
  return charSet.size() == newWord.length();
  ```
  Splitting `""` produces `[""]`, concatenating produces `""`.
  The length of `newWord` is `0`. The loop executes 0 times, leaving `charSet` empty (`size == 0`).
  Evaluation: `0 == 0` $\rightarrow$ `true`.

### 2. Case: `testLowercaseIsogram()`
- **Canonical UUID**: `9a001b50-f194-4143-bc29-2af5ec1ef652`
- **Method Name**: `public void testLowercaseIsogram()`
- **Annotations**: `@Disabled("Remove to run test")`, `@Test`, `@DisplayName("isogram with only lower case characters")`
- **Input**: `"isogram"`
- **Expected Result**: `true`
- **Java Operation in Reference Solution**:
  No spaces or hyphens; `newWord` is `"isogram"` with length 7.
  Adding each character `'i'`, `'s'`, `'o'`, `'g'`, `'r'`, `'a'`, `'m'` into `HashSet<Character>` yields 7 unique entries.
  Evaluation: `charSet.size() == 7 == newWord.length()` $\rightarrow$ `true`.

### 3. Case: `testNotIsogram()`
- **Canonical UUID**: `8ddb0ca3-276e-4f8b-89da-d95d5bae78a4`
- **Method Name**: `public void testNotIsogram()`
- **Annotations**: `@Disabled("Remove to run test")`, `@Test`, `@DisplayName("word with one duplicated character")`
- **Input**: `"eleven"`
- **Expected Result**: `false`
- **Java Operation in Reference Solution**:
  `newWord` is `"eleven"` with length 6.
  The letter `'e'` occurs 3 times. `HashSet<Character>` collapses duplicate `'e'`s, resulting in `{'e', 'l', 'v', 'n'}` (size 4).
  Evaluation: `charSet.size() == 4 != 6` $\rightarrow$ `false`.

---

## Round-Trip Consistency & Verification

Because `IsogramCheckerTest.java` is maintained by hand:
1. Two separate read/generation passes across fresh scratch directories produce identical files byte-for-byte.
2. No machine-generated dynamic timestamps exist in the test file, ensuring perfect reproducibility.
3. Every test case corresponds 1:1 with canonical metadata in `tests.toml`.
4. When executed against the reference implementation in an isolated temporary directory, all 14 tests pass cleanly.
