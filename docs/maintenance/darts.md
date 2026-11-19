# Darts Exercise Maintenance & Approach Comparison

## Overview
This document compares two implementation approaches for the `darts` practice exercise in the Java track as part of Task R58-T026.

---

## 1. Problem Contract & Rules
The task requires calculating points scored by a dart landing at Cartesian coordinates $(x, y)$:
- Inside or on inner circle ($r = 1$): **10 points**
- Inside or on middle circle ($r = 5$): **5 points**
- Inside or on outer circle ($r = 10$): **1 point**
- Outside target ($r > 10$): **0 points**

---

## 2. Compared Approaches

### Approach 1: Maintained Reference (Euclidean Distance via `Math.sqrt`)
Located in `.meta/src/reference/java/Darts.java`:
```java
int score(double x, double y) {
    if (RADIUS_CIRCLE_MIDDLE < distanceDartToOrigin(x, y)
            && distanceDartToOrigin(x, y) <= RADIUS_CIRCLE_OUTER) {
        return 1;
    } else if (RADIUS_CIRCLE_INNER < distanceDartToOrigin(x, y)
            && distanceDartToOrigin(x, y) <= RADIUS_CIRCLE_MIDDLE) {
        return 5;
    } else if (distanceDartToOrigin(x, y) <= RADIUS_CIRCLE_INNER) {
        return 10;
    }
    return 0;
}
private double distanceDartToOrigin(double x, double y) {
    return Math.sqrt(Math.pow(x, 2) + Math.pow(y, 2));
}
```

### Approach 2: Alternative (Squared Radius & Monotonic Early-Exit)
Implemented experimentally in `work/R58-T026/AlternativeDarts.java`:
```java
int score(double x, double y) {
    double distanceSquared = x * x + y * y;
    if (distanceSquared <= 1.0) {
        return 10;
    } else if (distanceSquared <= 25.0) {
        return 5;
    } else if (distanceSquared <= 100.0) {
        return 1;
    }
    return 0;
}
```

---

## 3. Comparison & Trade-off Analysis

| Feature | Reference Approach (`Math.sqrt`) | Alternative Approach (Squared Distance) |
|---|---|---|
| **Mathematical Concept** | Direct distance comparison: $d \le r$ | Squared distance comparison: $x^2 + y^2 \le r^2$ |
| **Computational Overhead** | High (calls `Math.sqrt` and `Math.pow`, repeatedly recomputed in multiple conditions) | Minimal (2 multiplications, 1 addition, 3 scalar comparisons) |
| **Control Flow** | Outer-to-inner with compound double-sided range checks (`5 < d && d <= 10`) | Inner-to-outer with simple single-sided monotonic thresholds (`<= 1`, `<= 25`, `<= 100`) |
| **Numerical Stability** | Subject to square-root floating-point rounding precision near thresholds | Exact multiplication without square-root rounding distortion |
| **Memory Usage** | $O(1)$ auxiliary stack space | $O(1)$ auxiliary stack space |

---

## 4. Test Verification Across Approaches
Both implementations were tested against the full suite of 13 tests, confirming 100% agreement:
- `missedTarget()`: $(-9, 9) \implies 0$
- `onTheOuterCircle()`: $(0, 10) \implies 1$
- `onTheMiddleCircle()`: $(-5, 0) \implies 5$
- `onTheInnerCircle()`: $(0, -1) \implies 10$
- `exactlyOnCentre()`: $(0, 0) \implies 10$
- `nearTheCentre()`: $(-0.1, -0.1) \implies 10$
- `justWithinTheInnerCircle()`: $(0.7, 0.7) \implies 10$
- `justOutsideTheInnerCircle()`: $(0.8, -0.8) \implies 5$
- `justWithinTheMiddleCircle()`: $(-3.5, 3.5) \implies 5$
- `justOutsideTheMiddleCircle()`: $(-3.6, -3.6) \implies 1$
- `justWithinTheOuterCircle()`: $(-7.0, 7.0) \implies 1$
- `justOutsideTheOuterCircle()`: $(7.1, -7.1) \implies 0$
- `asymmetricPositionBetweenTheInnerAndMiddleCircles()`: $(0.5, -4) \implies 5$

---

## 5. Verification Command
```bash
python3 work/R58-T026/check.py
```
