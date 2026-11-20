# Knapsack Exercise Maintenance: Computational Cost Analysis

## Overview

This document provides a comprehensive cost analysis of the reference implementation for the `knapsack` practice exercise (`exercises/practice/knapsack/.meta/src/reference/java/Knapsack.java`) as required by Task R58-T005.

The exercise models the classic 0/1 knapsack problem: given a carrying capacity (`maximumWeight`, $W$) and a list of item records (`List<Item> items`, $N$), select a subset of items to maximize cumulative value without exceeding capacity.

---

## Input Size Definition

In terms of the `knapsack` exercise domain, input size cannot be characterized by a single arbitrary scalar or loop counter. Rather, it is defined by two fundamental domain parameters:
1. **Item Record Count ($N$)**: The number of distinct item candidates presented in `List<Item> items` ($N = \text{items.size()}$). Each record contains strictly positive fields `weight` and `value`.
2. **Carrying Capacity Limit ($W$)**: The non-negative integer capacity bound `maximumWeight` ($W \ge 0$).

### State Space and Memory Footprint
The reference algorithm employs bottom-up dynamic programming. It allocates a 2D array grid:
$$\text{Dimensions} = (N + 1) \times (W + 1)$$
- **Rows**: $N + 1$, corresponding to subproblems considering subsets of the first $i$ items ($0 \le i \le N$).
- **Columns**: $W + 1$, corresponding to subproblems with integer residual capacity $w$ ($0 \le w \le W$).
- **Total DP Table Cells**: $(N + 1)(W + 1)$ primitive integer elements.
- **Space Complexity**: $\Theta(N \cdot W)$ heap space (specifically, $1$ outer array of length $N+1$ holding pointers to $(N+1)$ primitive `int[]` arrays of length $W+1$).

---

## Algorithmic Cost & Operation Breakdown

The maintained reference implementation in `Knapsack.java` executes two sequential double-nested loops:

```java
// Loop 1: Zero-initialization
for (int item = 0; item <= items.size(); item++) {
    for (int weight = 0; weight <= maximumWeight; weight++) {
        knapsack[item][weight] = 0; // Return 0 if not filled
    }
}

// Loop 2: DP recurrence computation
for (int item = 0; item <= items.size(); item++) {
    for (int weight = 0; weight <= maximumWeight; weight++) {
        if (item == 0 || weight == 0) {
            knapsack[item][weight] = 0;    
        } else if (items.get(item - 1).weight > weight) {
            knapsack[item][weight] = knapsack[item - 1][weight];
        } else {
            int itemValue  = items.get(item - 1).value;
            int itemWeight = items.get(item - 1).weight;
            knapsack[item][weight] = 
                Math.max(
                    itemValue + knapsack[item - 1][weight - itemWeight],
                    knapsack[item - 1][weight]
                );
        }
    }
}
```

### Exact Operation and Branch Structure
1. **Loop 1 (Explicit Zero-Fill)**:
   - Iterations: $(N + 1)(W + 1)$.
   - Operations: $(N + 1)(W + 1)$ array writes setting elements to `0`. (Note: while Java primitive arrays are zero-initialized by the JVM upon allocation, the reference explicitly performs this pass).

2. **Loop 2 (DP Recurrence Evaluation)**:
   - Iterations: $(N + 1)(W + 1)$.
   - Evaluates three distinct execution branches for each cell $(i, w)$:
     - **Branch 1 (Base Case / Boundary)**: `item == 0 || weight == 0`.
       - Taken exactly $(W + 1) + N = N + W + 1$ times.
       - Action: 1 write `knapsack[item][weight] = 0`.
     - **Branch 2 (Item Too Heavy)**: `items.get(item - 1).weight > weight`.
       - Taken when the $i$-th item cannot fit in current sub-capacity $w$.
       - Action: 1 `items.get(i-1)` call, 1 array read `knapsack[i-1][w]`, 1 array write.
     - **Branch 3 (Item Fits / Optimal Choice)**: `items.get(item - 1).weight <= weight`.
       - Taken when the $i$-th item can be considered for inclusion.
       - Action: 3 `items.get(i-1)` accessor calls, 2 array reads (`knapsack[i-1][w - itemWeight]` and `knapsack[i-1][w]`), 1 addition, 1 `Math.max()` call, and 1 array write.

- **Total Iterations across both loops**: $2 \times (N + 1)(W + 1)$.
- **Time Complexity**: $\Theta(N \cdot W)$ elementary operations.

---

## Three Valid Domain Input Sizes

Rather than synthesizing an artificial large-input benchmark outside the exercise scope, three valid input sizes are selected directly from the canonical test suite (`exercises/practice/knapsack/.meta/tests.toml` and `KnapsackTest.java`):

1. **Small**: `"example knapsack"` (`testExampleKnapsack`)
   - $N = 4$ item records: `(5, 10)`, `(4, 40)`, `(6, 30)`, `(4, 50)`
   - Capacity $W = 10$
   - Expected Maximum Value: `90`
2. **Medium**: `"8 items"` (`testEightItems`)
   - $N = 8$ item records: `(25, 350)`, `(35, 400)`, `(45, 450)`, `(5, 20)`, `(25, 70)`, `(3, 8)`, `(2, 5)`, `(2, 5)`
   - Capacity $W = 104$
   - Expected Maximum Value: `900`
3. **Large**: `"15 items"` (`testFifteenItems`)
   - $N = 15$ item records: `(70, 135)`, `(73, 139)`, `(77, 149)`, `(80, 150)`, `(82, 156)`, `(87, 163)`, `(90, 173)`, `(94, 184)`, `(98, 192)`, `(106, 201)`, `(110, 210)`, `(113, 214)`, `(115, 221)`, `(118, 229)`, `(120, 240)`
   - Capacity $W = 750$
   - Expected Maximum Value: `1458`

---

## Operation & Branch Count Table

| Metric | Small (`example knapsack`) | Medium (`8 items`) | Large (`15 items`) | General Bound |
|---|---|---|---|---|
| **Item Records ($N$)** | 4 | 8 | 15 | $N$ |
| **Capacity ($W$)** | 10 | 104 | 750 | $W$ |
| **DP Grid Dimensions** | $5 \times 11$ | $9 \times 105$ | $16 \times 751$ | $(N+1) \times (W+1)$ |
| **Total DP Table Cells** | **55** | **945** | **12,016** | $(N+1)(W+1)$ |
| **Zero-Init Loop Iterations** | 55 | 945 | 12,016 | $(N+1)(W+1)$ |
| **Compute Loop Iterations** | 55 | 945 | 12,016 | $(N+1)(W+1)$ |
| **Total Loop Iterations** | **110** | **1,890** | **24,032** | $2(N+1)(W+1)$ |
| **Branch 1: Boundary Cells** | 15 | 113 | 766 | $N + W + 1$ |
| **Branch 2: Item Too Heavy** | 15 | 134 | 1,418 | Data-dependent |
| **Branch 3: Item Fits (`Math.max`)** | 25 | 698 | 9,832 | $N \cdot W - (\text{Too Heavy})$ |
| **`items.get()` Calls** | 90 | 2,228 | 30,914 | $N \cdot W + 2 \times (\text{Branch 3})$ |
| **`Math.max()` Calls** | 25 | 698 | 9,832 | Branch 3 count |
| **Array Reads** | 65 | 1,530 | 21,082 | $(\text{Branch 2}) + 2 \times (\text{Branch 3})$ |
| **Array Writes** | 110 | 1,890 | 24,032 | $2(N+1)(W+1)$ |

---

## Empirical Timing Measurements

### Methodology
- **Correctness Assertion**: Prior to timing, all three inputs are executed and verified against canonical values (`90`, `900`, `1458`). An assertion failure immediately terminates the runner with a non-zero exit code.
- **Warmup**: 5,000 warm-up runs execute across all sizes to trigger JIT compilation (C2 compiler Tier 4) and stabilize garbage collection state.
- **Repetitions**: 7 independent repetitions are executed per input size under constant environmental conditions.
- **Measurement**: High-resolution timestamps via `System.nanoTime()`. The median of the 7 repetitions is reported to eliminate OS scheduling noise.

### Measurement Results

| Size | Canonical Case | Grid Cells | Measured Repetitions ($\text{ns}$) | Median Time |
|---|---|---|---|---|
| **Small** | `example knapsack` ($N=4, W=10$) | 55 | `[542, 250, 250, 250, 250, 209, 208]` | **250 ns** ($0.250\ \mu\text{s}$) |
| **Medium** | `8 items` ($N=8, W=104$) | 945 | `[1292, 1333, 1292, 1250, 1250, 1250, 1250]` | **1,250 ns** ($1.250\ \mu\text{s}$) |
| **Large** | `15 items` ($N=15, W=750$) | 12,016 | `[13791, 13750, 13833, 13875, 13875, 13958, 13875]` | **13,875 ns** ($13.875\ \mu\text{s}$) |

### Empirical Scaling Analysis
- Increasing state space from Medium (945 cells) to Large (12,016 cells) represents a **$12.71\times$ increase in table cells**.
- The measured median runtime scales from $1.25\ \mu\text{s}$ to $13.875\ \mu\text{s}$, representing an **$11.10\times$ increase in execution time**.
- This near-linear scaling between table size and elapsed time closely matches the theoretical $\Theta(N \cdot W)$ time complexity.

---

## Distinguishing Algorithm Work from Startup & Compilation Overhead

A critical aspect of performance evaluation in managed environments like the JVM and Gradle is distinguishing pure algorithmic execution time from build orchestration, compilation, and process startup overhead.

| Execution Phase | Measured Duration | Scale Relative to Algorithm |
|---|---|---|
| **Gradle Test Build (`./gradlew test --no-daemon`)** | $\approx 2,705\ \text{ms}$ ($2.7\ \text{s}$) | $\approx 195,000\times$ larger than Large algorithm run |
| **`javac` Compilation (Item, Knapsack, Benchmark)** | $\approx 227\ \text{ms}$ | $\approx 16,300\times$ larger than Large algorithm run |
| **JVM Process Initialization & Reflection** | $\approx 122\ \text{ms}$ | $\approx 8,800\times$ larger than Large algorithm run |
| **Algorithm Execution: Large ($N=15, W=750$)** | **$0.0139\ \text{ms}$ ($13.88\ \mu\text{s}$)** | **$1.0\times$ (Algorithm Work)** |
| **Algorithm Execution: Medium ($N=8, W=104$)** | **$0.00125\ \text{ms}$ ($1.25\ \mu\text{s}$)** | **$0.09\times$** |
| **Algorithm Execution: Small ($N=4, W=10$)** | **$0.00025\ \text{ms}$ ($0.25\ \mu\text{s}$)** | **$0.018\times$** |

### Findings
1. Pure algorithm work across all domain inputs requires between **$0.25\ \mu\text{s}$ and $13.88\ \mu\text{s}$**.
2. Algorithm execution accounts for approximately **$0.00051\%$** of total Gradle build time.
3. Attempting to benchmark algorithm efficiency by wrapping `gradlew` or timing process invocations externally measures JVM bootstrap, class loading, bytecode verification, and test framework reflection—not the cost of the knapsack algorithm. Measuring pure algorithm cost requires in-process, warmed micro-benchmarking with nanosecond precision.

---

## Verification & Integrity

The complete verification harness is executed via:
```bash
python3 work/R58-T005/check.py
```
or via the course check forwarder:
```bash
python3 tools/course_checks/r58-t005.py
```

### Verification Criteria Confirmed:
1. All 7 canonical test cases execute and pass against the maintained reference implementation in an isolated scratch environment.
2. The working tree learner starter stub (`exercises/practice/knapsack/src/main/java/Knapsack.java`) remains unsolved (`UnsupportedOperationException`) and byte-for-byte unchanged.
3. Correctness is verified prior to timing.
4. Measurements adhere to constant environment conditions, $>5$ repetitions, and reported medians.
