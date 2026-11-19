# Hints

## Approach Selection: Distance vs. Squared Distance

When determining which concentric ring a dart lands in, you need to check whether the dart's coordinates $(x, y)$ fall within a circle of radius $r$ centered at the origin $(0, 0)$.

There are two primary approaches to represent and evaluate this geometric condition:

### 1. Direct Euclidean Distance (`Math.sqrt`)
- **Formula**: $d = \sqrt{x^2 + y^2}$.
- **Comparison**: Compare the calculated distance $d$ directly against the circle radii ($r = 1$, $r = 5$, $r = 10$).
- **Trade-off**: While this directly mirrors the problem statement, calling `Math.sqrt()` and `Math.pow()` involves floating-point square root instructions which are computationally heavier and can introduce minor rounding nuances near boundary values.

### 2. Squared Distance ($d^2 \le r^2$)
- **Formula**: $d^2 = x \cdot x + y \cdot y$.
- **Comparison**: Compare $d^2$ against pre-squared radii ($1^2 = 1$, $5^2 = 25$, $10^2 = 100$).
- **Trade-off**: Mathematically, $\sqrt{x^2 + y^2} \le r \iff x^2 + y^2 \le r^2$ for non-negative values. This eliminates the square root operation entirely, using only basic multiplication and addition. It is faster, avoids square-root precision loss, and simplifies control flow by allowing single-sided monotonic checks from the inside out (inner $\le 1$, middle $\le 25$, outer $\le 100$).

### Worked Example: Dart at $(-3.5, 3.5)$
Consider a dart thrown at coordinates $(-3.5, 3.5)$:
1. Calculate squared distance:
   $$d^2 = (-3.5)^2 + (3.5)^2 = 12.25 + 12.25 = 24.5$$
2. Compare against threshold boundaries:
   - Is $24.5 \le 1$ (inner circle)? No ($24.5 > 1$).
   - Is $24.5 \le 25$ (middle circle)? Yes ($24.5 \le 25$).
3. The dart lands within the middle circle, scoring **5 points**.
