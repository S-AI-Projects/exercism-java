# Hints

## Java: checking digits in an `int[]`

The reference validates that every digit is in range by streaming the primitive
array and asking for its minimum and maximum. `Arrays.stream(int[])` produces an
`IntStream`; its `min()` method returns an `OptionalInt`, so `getAsInt()` gives
you an `int` without boxing it into an `Integer`.

```java
import java.util.Arrays;

class DigitMinimumExample {
    public static void main(String[] args) {
        int[] digits = {1, 0, 1};
        int smallestDigit = Arrays.stream(digits).min().getAsInt();
        System.out.println(smallestDigit); // 0

        int[] noDigits = {};
        if (noDigits.length == 0) {
            System.out.println("no digits to check");
        } else {
            System.out.println(Arrays.stream(noDigits).min().getAsInt());
        }
    }
}
```

Output:

```text
0
no digits to check
```

The early return for an empty array in `validateInputs` matters: calling
`getAsInt()` on the empty result of `min()` throws `NoSuchElementException`.
For this exercise, an empty digit sequence is valid and represents zero, so
there is no minimum digit to inspect. This is also why the reference handles
the empty case before checking for negative or too-large digits. See the Java
references for [`Arrays.stream(int[])`](https://docs.oracle.com/javase/8/docs/api/java/util/Arrays.html#stream-int:A-)
and [`OptionalInt.getAsInt()`](https://docs.oracle.com/javase/8/docs/api/java/util/OptionalInt.html#getAsInt--).
