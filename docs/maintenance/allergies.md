# Allergies Exercise Maintenance

## Overview
This document tracks the canonical test case coverage and rationales for the `allergies` practice exercise in the Java track.

The universal canonical specification defines 50 test cases for `allergies`.
In the Java track:
- Total canonical test cases: 50
- Included cases: 50
- Excluded cases: 0

## Canonical Test Case Mapping (Selected UUIDs)

The table below maps the selected canonical test cases to their Java test implementation in `AllergiesTest.java` and details the underlying Java operations in the reference solution (`Allergies.java`).

| Canonical UUID | Canonical Description | Java Test Method | JUnit `@DisplayName` | Status | Rationale & Java Operation |
|---|---|---|---|---|---|
| `17fc7296-2440-4ac4-ad7b-d07c321bc5a0` | testing for eggs allergy -> not allergic to anything | `eggsNotAllergicToAnything()` | `"not allergic to anything"` | Included | Score is 0 (no allergies). Evaluates `allergies.isAllergicTo(Allergen.EGGS)` via bitwise AND `(score & allergen.getScore()) != 0` -> `(0 & 1) != 0` -> `false`. Asserts `isFalse()`. |
| `07ced27b-1da5-4c2e-8ae2-cb2791437546` | testing for eggs allergy -> allergic only to eggs | `eggsAllergicOnlyToEggs()` | `"allergic only to eggs"` | Included | Score is 1 (only EGGS). Evaluates `allergies.isAllergicTo(Allergen.EGGS)` via bitwise AND `(score & allergen.getScore()) != 0` -> `(1 & 1) != 0` -> `true`. Asserts `isTrue()`. |
| `5035b954-b6fa-4b9b-a487-dae69d8c5f96` | testing for eggs allergy -> allergic to eggs and something else | `eggsAllergicToEggsAndSomethingElse()` | `"allergic to eggs and something else"` | Included | Score is 3 (EGGS = 1, PEANUTS = 2). Evaluates `allergies.isAllergicTo(Allergen.EGGS)` via bitwise AND `(score & allergen.getScore()) != 0` -> `(3 & 1) != 0` -> `true`. Asserts `isTrue()`. |

## Reference Implementation Details
In `Allergies.java`, allergen checking is implemented using bitwise flag masking against allergen values defined in the `Allergen` enum:
```java
boolean isAllergicTo(Allergen allergen) {
    return (score & allergen.getScore()) != 0;
}
```
Allergen values:
- `EGGS`: 1 ($2^0$)
- `PEANUTS`: 2 ($2^1$)
- `SHELLFISH`: 4 ($2^2$)
- `STRAWBERRIES`: 8 ($2^3$)
- `TOMATOES`: 16 ($2^4$)
- `CHOCOLATE`: 32 ($2^5$)
- `POLLEN`: 64 ($2^6$)
- `CATS`: 128 ($2^7$)

Values greater than 255 (i.e. bits $\ge 8$) do not match any allergen bit in the enum and are naturally ignored by the bitwise AND operation.
