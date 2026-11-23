# Java-specific hint: compare boxed values

The Java reference searches a `List<Integer>` and compares the target with the middle element using `Integer.compareTo`. A list lookup returns an `Integer` object; `compareTo` compares the numeric values and returns zero when they are equal. Do not replace this with `==`, which compares object identity for two `Integer` references and can appear to work for small cached values.

This standalone example mirrors the reference's boxed comparison:

```java
import java.util.List;

class BinarySearchBoxingDemo {
    public static void main(String[] args) {
        Integer target = Integer.valueOf(10);
        Integer middle = List.of(4, 10, 21).get(1);
        System.out.println(target.compareTo(middle) == 0);
        System.out.println((int) middle);
    }
}
```

Expected output:

```text
true
10
```

The cast makes the unboxing step explicit. The reference compares boxed values with `compareTo` while narrowing the search bounds; it does not modify the list. See the Java [`Integer.compareTo`](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/Integer.html#compareTo(java.lang.Integer)) documentation.
