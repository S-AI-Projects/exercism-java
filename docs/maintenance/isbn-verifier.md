# ISBN-Verifier Exercise Maintenance

## Overview

This document describes the test generation approach and canonical case mapping for the
`isbn-verifier` practice exercise in the Java track.

> [!IMPORTANT]
> The test file `exercises/practice/isbn-verifier/src/test/java/IsbnVerifierTest.java`
> is **hand-maintained** in this track. There is no per-exercise Jinja template or
> track-level generator script for `isbn-verifier`. Test cases are authored directly
> against the canonical specification in `problem-specifications`.

---

## Test Source

| File | Maintained by |
|---|---|
| `src/test/java/IsbnVerifierTest.java` | **Hand-maintained** by Java track contributors |
| `.meta/tests.toml` | Auto-synced via `configlet sync` from [problem-specifications](https://github.com/exercism/problem-specifications/blob/main/exercises/isbn-verifier/canonical-data.json) |
| `.meta/src/reference/java/IsbnVerifier.java` | Hand-maintained reference implementation |

---

## Generation / Regeneration Command

Since no generator exists for this exercise, the test file is maintained by hand.
To sync `tests.toml` with the upstream canonical specification, run:

```bash
bin/fetch-configlet
./bin/configlet sync --update --exercise isbn-verifier
```

To verify the test file is consistent with the canonical spec, compare the test methods
in `IsbnVerifierTest.java` against the `description` values in `.meta/tests.toml`.

---

## Canonical Case Mapping

The table below maps the 21 canonical test UUIDs to the corresponding Java test methods.
One additional hand-maintained test (`validIsbnNumberWithCheckDigitPaddedWithLettersIsInvalid`)
exists in the Java track but is **not** present in `problem-specifications`; it covers a
Java-specific edge case with letter padding around an otherwise-valid ISBN.

| Canonical UUID | Description (from tests.toml) | Java Test Method | `@DisplayName` |
|---|---|---|---|
| `0caa3eac-d2e3-4c29-8df8-b188bc8c9292` | valid isbn | `validIsbnNumber()` | `"valid isbn"` |
| `19f76b53-7c24-45f8-87b8-4604d0ccd248` | **invalid isbn check digit** | `invalidIsbnCheckDigit()` | `"invalid isbn check digit"` |
| `4164bfee-fb0a-4a1c-9f70-64c6a1903dcd` | **valid isbn with a check digit of 10** | `validIsbnNumberWithCheckDigitOfTen()` | `"valid isbn with a check digit of 10"` |
| `3ed50db1-8982-4423-a993-93174a20825c` | check digit is a character other than X | `checkDigitIsACharacterOtherThanX()` | `"check digit is a character other than X"` |
| `9416f4a5-fe01-4b61-a07b-eb75892ef562` | invalid check digit in isbn is not treated as zero | `invalidCheckDigitInIsbn()` | `"invalid check digit in isbn is not treated as zero"` |
| `c19ba0c4-014f-4dc3-a63f-ff9aefc9b5ec` | invalid character in isbn is not treated as zero | `invalidCharacterInIsbn()` | `"invalid character in isbn is not treated as zero"` |
| `28025280-2c39-4092-9719-f3234b89c627` | X is only valid as a check digit | `xIsOnlyValidAsACheckDigit()` | `"X is only valid as a check digit"` |
| `8005b57f-f194-44ee-88d2-a77ac4142591` | only one check digit is allowed | `onlyOneCheckDigitIsAllowed()` | `"only one check digit is allowed"` |
| `fdb14c99-4cf8-43c5-b06d-eb1638eff343` | X is not substituted by the value 10 | `xIsNotSubstitutedByTheValue10()` | `"X is not substituted by the value 10"` |
| `f6294e61-7e79-46b3-977b-f48789a4945b` | valid isbn without separating dashes | `validIsbnWithoutSeparatingDashes()` | `"valid isbn without separating dashes"` |
| `185ab99b-3a1b-45f3-aeec-b80d80b07f0b` | isbn without separating dashes and X as check digit | `isbnWithoutSeparatingDashesAndXAsCheckDigit()` | `"isbn without separating dashes and X as check digit"` |
| `7725a837-ec8e-4528-a92a-d981dd8cf3e2` | isbn without check digit and dashes | `isbnWithoutCheckDigitAndDashes()` | `"isbn without check digit and dashes"` |
| `47e4dfba-9c20-46ed-9958-4d3190630bdf` | too long isbn and no dashes | `tooLongIsbnAndNoDashes()` | `"too long isbn and no dashes"` |
| `737f4e91-cbba-4175-95bf-ae630b41fb60` | too short isbn | `tooShortIsbn()` | `"too short isbn"` |
| `5458a128-a9b6-4ff8-8afb-674e74567cef` | isbn without check digit | `isbnWithoutCheckDigit()` | `"isbn without check digit"` |
| `70b6ad83-d0a2-4ca7-a4d5-a9ab731800f7` | check digit of X should not be used for 0 | `checkDigitOfXShouldNotBeUsedForZero()` | `"check digit of X should not be used for 0"` |
| `94610459-55ab-4c35-9b93-ff6ea1a8e562` | empty isbn | `emptyIsbn()` | `"empty isbn"` |
| `7bff28d4-d770-48cc-80d6-b20b3a0fb46c` | input is 9 characters | `inputIsNineCharacters()` | `"input is 9 characters"` |
| `ed6e8d1b-382c-4081-8326-8b772c581fec` | invalid characters are not ignored after checking length | `invalidCharactersAreNotIgnoredAfterCheckingLength()` | `"invalid characters are not ignored after checking length"` |
| `daad3e58-ce00-4395-8a8e-e3eded1cdc86` | invalid characters are not ignored before checking length | `invalidCharactersAreNotIgnoredBeforeCheckingLength()` | `"invalid characters are not ignored before checking length"` |
| `fb5e48d8-7c03-4bfb-a088-b101df16fdc3` | input is too long but contains a valid isbn | `inputIsTooLongButContainsAValidIsbn()` | `"input is too long but contains a valid isbn"` |
| *(hand-maintained, no UUID)* | valid isbn with check digit padded with letters is invalid | `validIsbnNumberWithCheckDigitPaddedWithLettersIsInvalid()` | `"valid isbn with check digit padded with letters is invalid"` |

---

## Named Cases (Anchored for Task R58-T022)

| Case | UUID | Java Method | Input | Expected | Java Operation |
|---|---|---|---|---|---|
| `invalidIsbnCheckDigit()` | `19f76b53-7c24-45f8-87b8-4604d0ccd248` | `invalidIsbnCheckDigit()` | `"3-598-21508-9"` | `false` | Strip dashes → `"3598215089"`. Sum = `(3×10 + 5×9 + 9×8 + 8×7 + 2×6 + 1×5 + 5×4 + 0×3 + 8×2 + 9×1)` = `237`. `237 % 11 = 6 ≠ 0` → invalid |
| `invalidIsbnCheckDigit()` with `assertThat(isbnVerifier.isValid(` | *same as above* | *same as above* | `"3-598-21508-9"` | `false` | *same* |
| `validIsbnNumberWithCheckDigitOfTen()` | `4164bfee-fb0a-4a1c-9f70-64c6a1903dcd` | `validIsbnNumberWithCheckDigitOfTen()` | `"3-598-21507-X"` | `true` | Strip dashes → `"359821507X"`. X = 10. Sum = `(3×10 + 5×9 + 9×8 + 8×7 + 2×6 + 1×5 + 5×4 + 0×3 + 7×2 + 10×1)` = `231`. `231 % 11 = 0` → valid |

---

## Round-Trip Consistency

Since the test file is **hand-maintained** (not generated from a template), a round-trip
comparison is performed by:
1. Making two clean copies of `IsbnVerifierTest.java`.
2. Verifying they are byte-for-byte identical (no timestamp or generated fields exist).
3. Confirming the set of `@DisplayName` values in the test file matches 1:1 with the
   `description` values in `tests.toml` (with one known extra hand-maintained case).

The command to reproduce the test coverage check is:

```bash
python3 work/R58-T022/check.py
```
