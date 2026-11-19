# House Exercise Maintenance

## Overview
This document describes the readability improvements made to the reference implementation of the `house` practice exercise in the Java track for Task R58-T024.

The exercise requires generating verses of the cumulative nursery rhyme *"This is the House that Jack Built"*, which illustrates linguistic recursive clausal embedding.

---

## Readability Improvements in `House.java`

### 1. Eliminating Ambiguous Local State (Identifier Shadowing)
- **`verse(int verseNumber)`**:
  - *Original*: `StringBuilder verse = new StringBuilder();` shadowed the method name `verse()`.
  - *Improved*: Renamed the local variable to `StringBuilder rhyme`.
- **`verses(int startVerse, int endVerse)`**:
  - *Original*: `String[] verses = new String[endVerse - startVerse + 1];` shadowed the method name `verses()`.
  - *Improved*: Renamed the local array to `String[] verseCollection`.

### 2. Extracting Coherent Calculation (`relativeClause`)
- *Original*: The loop body inside `verse()` constructed `" that " + ACTIONS[i] + " the " + CHARACTERS[i]` inline using string concatenation inside `StringBuilder.append(...)`.
- *Improved*: Extracted `private String relativeClause(int index)` which explicitly encapsulates the formation of each relative clause:
  ```java
  private String relativeClause(int index) {
      return " that " + ACTIONS[index] + " the " + CHARACTERS[index];
  }
  ```
- This directly reflects the linguistic principle of recursive embedding highlighted in the exercise instructions, separating the introductory clause (`"This is the " + CHARACTERS[...]`) from the cascading qualifying clauses.

### 3. Avoiding Inefficient String Concatenation in `StringBuilder`
- *Original*: `verse.append("This is the " + CHARACTERS[verseNumber - 1]);` defeated the purpose of `StringBuilder` by concatenating strings before appending.
- *Improved*: Chained appends: `rhyme.append("This is the ").append(CHARACTERS[verseNumber - 1]);`.

---

## Behavioral Baseline Verification

The following existing cases serve as the baseline and were verified before and after refactoring:

| Test Method | JUnit `@DisplayName` | Input | Expected Output |
|---|---|---|---|
| `verseOne()` | `"verse one - the house that jack built"` | `house.verse(1)` | `"This is the house that Jack built."` |
| `verseTwo()` | `"verse two - the malt that lay"` | `house.verse(2)` | `"This is the malt that lay in the house that Jack built."` |
| `verseThree()` | `"verse three - the rat that ate"` | `house.verse(3)` | `"This is the rat that ate the malt that lay in the house that Jack built."` |
| `multipleVerses()` | `"multiple verses"` | `house.verses(4, 8)` | Verses 4 through 8 joined with newline |
| `wholeRhyme()` | `"full rhyme"` | `house.sing()` | All 12 verses joined with newline |

---

## Verification
Automated checks are executed via:
```bash
python3 work/R58-T024/check.py
```
All 14 tests pass, zero regressions, and the learner starter stub remains unsolved.
