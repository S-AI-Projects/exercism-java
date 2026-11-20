# Yacht Exercise Maintenance

## Overview
This document describes the scoped readability improvements made to the reference implementation of the `yacht` practice exercise in the Java track for Task R58-T004.

The exercise requires scoring a single throw of five six-sided dice across twelve distinct categories (e.g., Ones through Sixes, Full House, Four of a Kind, Straights, Choice, and Yacht).

---

## Readability Improvements in `Yacht.java`

### 1. Eliminating Ambiguous Local State
- **`score()` (`case FULL_HOUSE`)**:
  - *Original*: `Collection<Long> occurrences = ...`
  - *Problem*: The identifier `occurrences` was ambiguous: it could easily be misread as the set or list of faces that occurred, rather than the frequency counts of those faces.
  - *Improved*: Renamed the local variable to `Collection<Long> dieFaceCounts` to explicitly communicate that it stores the count of dice showing each distinct face.

### 2. Extracting Coherent Calculation (`dieFrequencies`)
- **Duplication in `FULL_HOUSE` and `FOUR_OF_A_KIND`**:
  - *Original*: Both `FULL_HOUSE` and `FOUR_OF_A_KIND` independently executed the identical stream grouping pipeline:
    ```java
    Arrays.stream(dice)
            .boxed()
            .collect(Collectors.groupingBy(Function.identity(), Collectors.counting()))
    ```
    In `FOUR_OF_A_KIND`, this was completely inlined into a long stream pipeline with an uncommunicative lambda variable `x -> x.getValue() >= 4`.
  - *Improved*: Extracted `private Map<Integer, Long> dieFrequencies()`:
    ```java
    // Exercise invariant: exactly 5 dice are presented, each showing face 1 through 6 inclusively.
    private Map<Integer, Long> dieFrequencies() {
        return Arrays.stream(dice)
                .boxed()
                .collect(Collectors.groupingBy(Function.identity(), Collectors.counting()));
    }
    ```
    And in `FOUR_OF_A_KIND`, renamed `x` to `entry` for readable map-entry inspection.

### 3. Documenting Exercise-Specific Invariants
- Annotated the invariant requirements directly above the logic:
  - Exactly 5 dice with faces 1 through 6 inclusively.
  - Full House invariant: exactly three dice of one face and two dice of another face; a Yacht (five of a kind) does not satisfy Full House and scores 0.
  - Four of a Kind invariant: at least four dice showing the same face, scoring 4 times that face value.

### 4. Preserving Interface and Error Contracts
- Public constructor `Yacht(int[] dice, YachtCategory yachtCategory)` preserved.
- Method signature `int score()` preserved.
- Return types, switch structure, ordering, and default fallback (0) remain identical.

---

## Tracing Yacht for Named Baseline Cases

The local state determining the outcome for key test cases:

| Test Method | JUnit `@DisplayName` | Input Dice & Category | Local State / Calculation | Result |
|---|---|---|---|---|
| `yacht()` | `"Yacht"` | `[5, 5, 5, 5, 5]`, `YACHT` | `distinct().count() == 1` -> `true` | `50` |
| `notYacht()` | `"Not Yacht"` | `[1, 3, 3, 2, 5]`, `YACHT` | `distinct().count() == 4` -> `false` | `0` |
| `yachtCountedAsThrees()` | `"Yacht counted as threes"` | `[3, 3, 3, 3, 3]`, `THREES` | `filter(n -> n == 3).sum()` | `15` |
| `fullHouseTwoSmallThreeBig()` | `"Full house two small, three big"` | `[2, 2, 4, 4, 4]`, `FULL_HOUSE` | `dieFaceCounts`: `[2, 3]` contains `2L` & `3L` | `16` |
| `fourOfAKindIsNotAFullHouse()` | `"Four of a kind is not a full house"` | `[1, 4, 4, 4, 4]`, `FULL_HOUSE` | `dieFaceCounts`: `[1, 4]` missing `2L` & `3L` | `0` |
| `yachtIsNotAFullHouse()` | `"Yacht is not a full house"` | `[2, 2, 2, 2, 2]`, `FULL_HOUSE` | `dieFaceCounts`: `[5]` missing `2L` & `3L` | `0` |
| `fourOfAKind()` | `"Four of a Kind"` | `[6, 6, 4, 6, 6]`, `FOUR_OF_A_KIND` | `dieFrequencies()`: `{4: 1, 6: 4}`, key `6` * 4 | `24` |
| `yachtCanBeScoredAsFourOfAKind()` | `"Yacht can be scored as Four of a Kind"` | `[3, 3, 3, 3, 3]`, `FOUR_OF_A_KIND` | `dieFrequencies()`: `{3: 5}`, key `3` * 4 | `12` |
| `fullHouseIsNotFourOfAKind()` | `"Full house is not Four of a Kind"` | `[3, 3, 3, 5, 5]`, `FOUR_OF_A_KIND` | `dieFrequencies()`: `{3: 3, 5: 2}`, no count >= 4 | `0` |

---

## Verification
Automated checks are executed via:
```bash
python3 work/R58-T004/check.py
```
Or via the course check harness:
```bash
python3 tools/course_checks/r58-t004.py
```
All 29 tests pass against the refactored reference with 0 failures, 0 errors, and 0 skipped. Outputs agree before and after refactoring, and the learner starter stub (`exercises/practice/yacht/src/main/java/Yacht.java`) remains unsolved and unmodified.
