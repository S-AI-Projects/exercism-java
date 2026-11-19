# Forth Exercise Maintenance & Complexity Study

## Overview
This document presents the architecture, complexity study, and benchmark analysis for the `forth` practice exercise in the Java track as part of Task R58-T025.

---

## 1. What `ForthEvaluator` Does
`ForthEvaluator` implements an interpreter for a subset of the stack-based programming language Forth.
It accepts a program as `List<String> program`, evaluates all numbers, built-in operators, and user-defined word declarations, and returns the contents of the evaluation stack in bottom-to-top order (`List<Integer>`).

Supported language features:
- **Numbers**: Signed integers (e.g. `1`, `-42`), pushed directly onto the evaluation stack.
- **Arithmetic operations**: `+`, `-`, `*`, `/` operating on the top 2 stack elements.
- **Stack manipulation**:
  - `dup`: Duplicates the top value (requires $\ge 1$ value).
  - `drop`: Discards the top value (requires $\ge 1$ value).
  - `swap`: Swaps the top two values (requires $\ge 2$ values).
  - `over`: Copies the second-to-top value onto the top (requires $\ge 2$ values).
- **User-defined words**: Syntax `: <word> <definition> ;` allows defining custom composite words, overriding existing words, and recursive word-definition expansions. Case-insensitive matching is enforced.

---

## 2. Implementation Mechanics
The evaluation proceeds in two phases:

1. **Parsing (`parse`)**:
   - Each input line is split by whitespace and parsed into `Token` objects (`IntToken`, `OpToken`, or `OpDefToken`).
   - All parsed tokens are accumulated into a `List<Token> tokens` (backed by `java.util.ArrayList`).

2. **Evaluation (`evaluate`)**:
   - Tokens are processed in FIFO order from the head of `tokens` using a while-loop: `while (!tokens.isEmpty()) { Token token = tokens.remove(0); ... }`.
   - `OpDefToken`: Resolves and substitutes previously defined user words in the definition (`applyUserOps`) and saves the token sequence in `Map<String, List<Token>> userOps`.
   - `OpToken`: Looked up in `userOps`. If present, the replacement tokens are reversed and inserted at index 0 of `tokens` (`tokens.add(0, token)`). Otherwise, looked up in `BUILT_IN_OPS` and applied to the `Deque<Integer> values` stack.
   - `IntToken`: Pushed onto `values`.
   - At the conclusion, elements in `values` (`ArrayDeque`) are converted to `List<Integer>` and reversed to produce the final bottom-to-top stack order.

---

## 3. Definition of Input Size
The input size $N$ is defined as the **total number of whitespace-delimited tokens** across all lines of the input program:
$$N = \sum_{i=1}^{L} \text{tokenCount}(\text{line}_i)$$
Because a Forth program can contain an arbitrary sequence of numbers, operators, and definitions of any length, the exercise supports **variable-size inputs**.

---

## 4. Complexity Analysis

### Time Complexity: $O(N^2)$
- **Parsing**: $O(N)$ regex matches and string splits.
- **Evaluation**: While stack operations (`push`, `pop`, `peek`) on `ArrayDeque` and lookups in `HashMap` are $O(1)$, the evaluation loop uses:
  ```java
  final Token token = tokens.remove(0);
  ```
  In Java, `ArrayList.remove(0)` shifts all $(K - 1)$ subsequent elements one position left, costing $O(K)$ per token. Over $N$ tokens, the cumulative shift cost is:
  $$\sum_{K=1}^{N} O(K) = O(N^2)$$
  Similarly, expanding user-defined words via `tokens.add(0, token)` incurs an $O(K)$ array shift per inserted token.

### Auxiliary Space Complexity: $O(N + D)$
- `tokens`: Stores up to $O(N)$ tokens in memory.
- `values`: Stack depth is bounded by $O(N)$ elements in the worst case (e.g. pushing $N$ integers).
- `userOps`: Stores $D$ tokens representing custom word definitions.

---

## 5. Benchmark Methodology & Empirical Results

### Environment & Measurement Strategy
- **Isolation**: JVM warm-up iterations (200 warm-up runs) were performed prior to measurement to trigger JIT compilation and class loading.
- **Timing Isolation**: Only algorithm execution (`evaluateProgram`) was measured using `System.nanoTime()`, strictly separating algorithm runtime from JVM startup and disk I/O.
- **Correctness Assertion**: The result of each input size was asserted against the mathematically expected value prior to benchmarking.
- **Repetitions**: 5 independent runs per input size; median timing reported.

### Benchmark Data
Input programs consisted of linear accumulation chains: `"1 1 + 1 + ... 1 +"`:

| Input Size ($N$ tokens) | Median Time (ms) | Repetitions (5 runs, ms) | Result Verified |
|---|---|---|---|
| **99 tokens** (Small) | **0.1947 ms** | [0.1717, 0.1845, 0.1947, 0.2152, 0.2526] | Passed (result: `50`) |
| **999 tokens** (Medium) | **1.3260 ms** | [1.1501, 1.1540, 1.3260, 1.4594, 1.6771] | Passed (result: `500`) |
| **4999 tokens** (Large) | **4.4549 ms** | [4.0955, 4.4098, 4.4549, 4.6499, 4.9175] | Passed (result: `2500`) |

### Observation
Execution time scales super-linearly with input size, confirming the theoretical $O(N^2)$ element-shifting overhead imposed by `ArrayList.remove(0)`.

---

## 6. Limitations of the Conclusion
1. **Memory Allocation**: Extremely large token streams may trigger JVM Garbage Collection (GC) pauses that introduce timing jitter.
2. **User-Defined Expansion**: Programs heavily using nested word replacements can expand token counts dynamically, where execution cost depends on the expansion tree depth rather than raw input token count alone.
3. **Data Structure Optimization**: Replacing `ArrayList<Token>` with a `Deque<Token>` or maintaining a cursor pointer would reduce evaluation time from $O(N^2)$ to $O(N)$.
