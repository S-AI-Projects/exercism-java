# Java note: primitive vs. boxed values in matrix calculations

## Connecting Saddle Points to Java

A saddle point in a matrix is an element that is simultaneously the maximum value in its row and the minimum value in its column.
In the Java track, the matrix input is supplied to the constructor as a `List<List<Integer>>`.

Because Java generic collections cannot store primitive types directly, the input elements are stored as boxed `Integer` wrapper objects.

## Language Constructs in the Reference Implementation

When implementing row and column extrema helpers such as `getRowMax(row)`:

- **Collection Mutation**: Not used. Finding the maximum value with `Collections.max(values.get(row))` only reads the row elements. It does not alter the list, append elements, or remove elements.
- **Exception Contracts**: Not defined by `getRowMax`. Although `Collections.max` throws `NoSuchElementException` when given an empty collection, `getRowMax` does not declare, catch, or specify an exception contract (unlike `getColumnMin`, which defines an explicit `.orElseThrow(...)` contract).
- **Primitive versus Boxed Values**: **Actually used by `getRowMax`**. `values.get(row)` is a `List<Integer>`, so `Collections.max(...)` returns a boxed `Integer`. However, `getRowMax` declares a primitive `int` return type:

```java
private int getRowMax(final int row) {
    return Collections.max(values.get(row));
}
```

Java automatically unboxes the resulting `Integer` object into a primitive `int` (`Integer.intValue()`).
Similarly, in `getSaddlePoints()`, matrix coordinates are extracted into a primitive `int coordinateValue`:

```java
final int coordinateValue = values.get(row).get(column);

if (coordinateValue == getRowMax(row) && coordinateValue == getColumnMin(column)) {
    result.add(new MatrixCoordinate(row + 1, column + 1));
}
```

Because both `coordinateValue` and `getRowMax(row)` evaluate to primitive `int`s, the `==` operator performs primitive numeric value comparison.

## Standalone Snippet and Exercise-Relevant Pitfall

### Correct Primitive Unboxing

When values are unboxed to primitive `int`, comparing them with `==` tests numeric equality:

```java
List<Integer> row = List.of(128, 64, 32);
int coordinateValue = row.get(0);
int rowMax = Collections.max(row);
boolean primitiveComparison = coordinateValue == rowMax;
System.out.println(primitiveComparison); // true
```

### Pitfall: Boxed Object Reference Comparison

A subtle pitfall occurs if you keep the values as boxed `Integer` objects and compare them with `==`:

```java
Integer boxedCoordinate = Integer.valueOf(128);
Integer boxedRowMax = Integer.valueOf(128);
boolean boxedReferenceComparison = boxedCoordinate == boxedRowMax;
System.out.println(boxedReferenceComparison); // false
```

### Why the Outcomes Differ

1. **Primitive Comparison (`true`)**: The `==` operator on primitive `int` values compares numerical magnitudes. Since `128 == 128`, the expression evaluates to `true`.
2. **Boxed Object Comparison (`false`)**: The `==` operator on object references compares heap identities (whether both references point to the exact same object in memory).
   Under the Java Language Specification (JLS §5.1.7), Java caches `Integer` instances only between `-128` and `127` inclusive.
   For numbers within that range, autoboxing reuses cached objects, so `==` may deceptively appear to work.
   However, for numbers outside that range (such as `128`), Java creates distinct `Integer` objects on the heap, causing `==` to evaluate to `false` even though both represent the number `128`.

To avoid this pitfall when comparing matrix values, either unbox elements to primitive `int` (as shown in the reference `getRowMax`) or use `Objects.equals(a, b)` / `a.equals(b)` when working with boxed `Integer` instances.
