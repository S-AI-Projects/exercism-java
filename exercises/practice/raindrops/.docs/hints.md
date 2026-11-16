# Java note: primitive integers and remainder

The maintained `RaindropConverter` receives a primitive Java `int`. It tests divisibility with the remainder operator `%`:

```java
int number = 15;
boolean divisibleByThree = number % 3 == 0;
System.out.println(divisibleByThree); // true
```

The remainder is zero exactly when the number is evenly divisible by the divisor. The same rule is used for 5 and 7, and the sounds are appended in the required order: Pling, Plang, then Plong.

A common pitfall is using integer division instead of remainder:

```java
int number = 15;
System.out.println(number / 3 == 0); // false
```

Integer division answers how many whole groups fit, not whether a remainder is left. For 15 divided by 3, the quotient is 5, so comparing it with zero does not test divisibility.

This exercise's reference uses a primitive `int`, `%`, and string concatenation. It does not mutate a collection, use boxed numeric values, or define an exception contract for this operation. For the language rule, see the [Java Language Specification: remainder operator](https://docs.oracle.com/javase/specs/jls/se21/html/jls-15.html#jls-15.17.3).
