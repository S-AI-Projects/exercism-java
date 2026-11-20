# Saddle Points: Language Construct Analysis & Learner Guidance

## Overview

This maintenance document records the analysis of language constructs used in the `saddle-points` practice exercise reference implementation (`Matrix.java`) for Task R58-T007. It evaluates collection mutation, primitive versus boxed values, and exception contracts, explains the specific construct used by `getRowMax(row)`, documents a standalone micro-example demonstrating correct primitive unboxing alongside an exercise-relevant pitfall, and details the test verification results.

---

## Problem Contract & Domain Model

In the `saddle-points` problem, a matrix coordinate $(r, c)$ is considered a saddle point if and only if:
1. It is greater than or equal to every element in its row ($v \ge \max(\text{row } r)$).
2. It is less than or equal to every element in its column ($v \le \min(\text{col } c)$).

In the Java track:
- The matrix constructor accepts a `List<List<Integer>> values`.
- The coordinates are returned as a `Set<MatrixCoordinate>` using 1-based indexing.

---

## Language Construct Examination

We examined three candidate Java language constructs in relation to helper methods such as `getRowMax`:

### 1. Collection Mutation
- **Definition**: Modifying an existing collection in-place (e.g. `list.add()`, `list.remove()`, or in-place sorting `Collections.sort()`).
- **Observation**: `getRowMax(row)` executes `Collections.max(values.get(row))`. `Collections.max` iterates over the list to identify the maximum element using its natural ordering. Neither the list nor its internal elements are modified.
- **Verdict**: **Not used** by `getRowMax`.

### 2. Exception Contracts
- **Definition**: Explicitly declaring or checking method preconditions, throwing checked/unchecked exceptions, or using `Optional` throwing semantics (e.g. `orElseThrow()`).
- **Observation**: While `Collections.max` throws `NoSuchElementException` if passed an empty collection, `getRowMax` does not declare `throws`, catch exceptions, or document an exception contract. (By contrast, `getColumnMin` in the reference explicitly defines `.orElseThrow(() -> new IllegalArgumentException("Column cannot be empty"))`).
- **Verdict**: **Not used** by `getRowMax`.

### 3. Primitive versus Boxed Values
- **Definition**: Distinction between primitive types (`int`, `double`) and boxed wrapper types (`Integer`, `Double`), including automatic boxing and unboxing (JLS §5.1.7 and §5.1.8).
- **Observation**:
  - The input matrix stores boxed objects: `List<List<Integer>> values`.
  - Generic collections in Java cannot hold primitive types directly.
  - `Collections.max(values.get(row))` operates on `Collection<? extends T>` and returns an `Integer`.
  - However, `getRowMax` declares its return type as primitive `int`:
    ```java
    private int getRowMax(final int row) {
        return Collections.max(values.get(row));
    }
    ```
  - Java automatically unboxes the resulting `Integer` object into a primitive `int` via `Integer.intValue()`.
  - Furthermore, in `getSaddlePoints()`, the coordinate value is extracted into a primitive `int`:
    ```java
    final int coordinateValue = values.get(row).get(column);
    if (coordinateValue == getRowMax(row) && coordinateValue == getColumnMin(column))
    ```
  - Because `coordinateValue`, `getRowMax(row)`, and `getColumnMin(column)` are all primitive `int`s, Java's `==` operator performs **primitive numeric value comparison**.
- **Verdict**: **Actually used** by `getRowMax`.

---

## Micro-Example & Exercise-Relevant Pitfall

### Standalone Snippet (`SaddlePointsBoxedPrimitiveExample.java`)

```java
import java.util.Collections;
import java.util.List;

public class SaddlePointsBoxedPrimitiveExample {
    public static void main(String[] args) {
        // Construct used by getRowMax: auto-unboxing Collections.max to primitive int
        List<Integer> row = List.of(128, 64, 32);
        int coordinateValue = row.get(0);
        int rowMax = Collections.max(row);
        boolean primitiveComparison = coordinateValue == rowMax;
        System.out.println(primitiveComparison); // true

        // Contrasting pitfall: comparing boxed Integer objects using == (outside [-128, 127] cache)
        Integer boxedCoordinate = Integer.valueOf(128);
        Integer boxedRowMax = Integer.valueOf(128);
        boolean boxedReferenceComparison = boxedCoordinate == boxedRowMax;
        System.out.println(boxedReferenceComparison); // false
    }
}
```

### Pitfall Analysis & Contrasting Outcomes

1. **Why Primitive Equality Succeeds (`true`)**:
   Primitive `int` variables hold raw 32-bit two's complement integers. The `==` operator directly compares their bit patterns and numerical values. Because $128 = 128$, `primitiveComparison` evaluates to `true`.

2. **Why Boxed Equality Fails (`false`)**:
   Boxed `Integer` variables hold object references (memory pointers to heap allocations). The `==` operator compares reference identity, asking whether both operands point to the exact same object in memory.
   According to JLS §5.1.7, the JVM caches `Integer` instances only for values in the range $[-128, 127]$.
   - For values within $[-128, 127]$, autoboxing reuses cached objects, so `==` can deceptively evaluate to `true`.
   - For values outside $[-128, 127]$ (such as $128$), boxing allocates distinct objects on the heap. Even though both hold the numeric value $128$, `boxedCoordinate == boxedRowMax` evaluates to `false`.

### Relevance to Saddle Points
If a learner implements `getRowMax` or `getSaddlePoints` using boxed `Integer` types:
```java
Integer coordinateValue = values.get(row).get(column);
Integer rowMax = Collections.max(values.get(row));
if (coordinateValue == rowMax) // BUG: fails for values outside [-128, 127] or separate objects
```
Their solution might pass simple tests that only use single-digit numbers (like $1, 2, 3$), but fail on matrices containing larger values or distinct object allocations.
Unboxing to primitive `int` (as the maintained reference does) ensures consistent, correct numeric equality across all inputs.

---

## Test Suite Verification

All 9 test cases from `exercises/practice/saddle-points/src/test/java/MatrixTest.java` and `.meta/tests.toml` pass cleanly against the maintained reference:

| # | Test Method | Display Name | Canonical UUID | Result |
|---|---|---|---|---|
| 1 | `testCanIdentifySingleSaddlePoint` | Can identify single saddle point | `3e374e63-a2e0-4530-a39a-d53c560382bd` | **PASSED** |
| 2 | `testCanIdentifyThatEmptyMatrixHasNoSaddlePoints` | Can identify that empty matrix has no saddle points | `6b501e2b-6c1f-491f-b1bb-7f278f760534` | **PASSED** |
| 3 | `testCanIdentifyLackOfSaddlePointsWhenThereAreNone` | Can identify lack of saddle points when there are none | `8c27cc64-e573-4fcb-a099-f0ae863fb02f` | **PASSED** |
| 4 | `testCanIdentifyMultipleSaddlePointsInAColumn` | Can identify multiple saddle points in a column | `6d1399bd-e105-40fd-a2c9-c6609507d7a3` | **PASSED** |
| 5 | `testCanIdentifyMultipleSaddlePointsInARow` | Can identify multiple saddle points in a Row | `3e81dce9-53b3-44e6-bf26-e328885fd5d1` | **PASSED** |
| 6 | `testCanIdentifySaddlePointInBottomRightCorner` | Can identify saddle point in bottom right corner | `88868621-b6f4-4837-bb8b-3fad8b25d46b` | **PASSED** |
| 7 | `testCanIdentifySaddlePointsInANonSquareMatrix` | Can identify saddle points in a non square matrix | `5b9499ca-fcea-4195-830a-9c4584a0ee79` | **PASSED** |
| 8 | `testCanIdentifyThatSaddlePointsInASingleColumnMatrixAreThoseWithMinimumValue` | Can identify that saddle points in a single column matrix are those with the minimum value | `ee99ccd2-a1f1-4283-ad39-f8c70f0cf594` | **PASSED** |
| 9 | `testCanIdentifyThatSaddlePointsInASingleRowMatrixAreThoseWithMaximumValue` | Can identify that saddle points in a single row matrix are those with the maximum value | `63abf709-a84b-407f-a1b3-456638689713` | **PASSED** |

---

## Verification Command

Execute the automated verification check from the repository root:

```bash
python3 work/R58-T007/check.py
# or
python3 tools/course_checks/r58-t007.py
```
