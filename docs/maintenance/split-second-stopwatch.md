# Split-Second Stopwatch Exercise Maintenance & Approach Comparison

## Overview
This document evaluates and compares two distinct implementation techniques for the `split-second-stopwatch` practice exercise in the Java track as part of Task R58-T006.

---

## 1. Problem Contract & State Machine

The stopwatch tracks lap times and total duration across three discrete operational states:
1. **`READY`**: Initial state; no elapsed time.
2. **`RUNNING`**: Active time tracking.
3. **`STOPPED`**: Paused state; retains accumulated time without advancing.

### State Transition & Command Matrix

| Command | Allowed Begin States | End State | Behavioral Invariant | Exception on Invalid State |
|---|---|---|---|---|
| `start()` | `READY`, `STOPPED` | `RUNNING` | Initiates or resumes time tracking | `IllegalStateException("cannot start an already running stopwatch")` |
| `stop()` | `RUNNING` | `STOPPED` | Freezes current lap tracking | `IllegalStateException("cannot stop a stopwatch that is not running")` |
| `lap()` | `RUNNING` | `RUNNING` | Commits current lap to previous laps; resets active lap to `00:00:00` | `IllegalStateException("cannot lap a stopwatch that is not running")` |
| `reset()` | `STOPPED` | `READY` | Resets active lap to `00:00:00` and clears previous laps | `IllegalStateException("cannot reset a stopwatch that is not stopped")` |

Time is formatted strictly as `HH:MM:SS` (two digits per component, zero-padded, hours unconstrained by 24h limits).

---

## 2. Compared Approaches

### Approach 1: Maintained Reference (Wall-Clock Epoch Offset Model)
Located in `.meta/src/reference/java/SplitSecondStopwatch.java`:
```java
public class SplitSecondStopwatch {
    private enum State { READY, RUNNING, STOPPED }

    private State state;
    private long totalCompletedLaps;  // Total time from completed laps in ms
    private long currentLapStart;     // When current lap started in ms
    private long accumulated;         // Accumulated time for current lap when stopped
    private List<String> previousLaps;
    private long mockTime;            // Global monotonic hardware clock in ms
    ...
```
**Mechanism**:
- Tracks a global monotonic timeline (`mockTime` in milliseconds).
- On `start()`, stamps `currentLapStart = mockTime`.
- On `advanceTime()`, increments `mockTime += milliseconds` indiscriminately.
- On `stop()`, accumulates elapsed segment: `accumulated += mockTime - currentLapStart`.
- Evaluates active lap time lazily via `getCurrentLapTime()` with a three-way state switch:
  $$\text{time} = \begin{cases} 0 & \text{state} = \text{READY} \\ \text{accumulated} + (\text{mockTime} - \text{currentLapStart}) & \text{state} = \text{RUNNING} \\ \text{accumulated} & \text{state} = \text{STOPPED} \end{cases}$$
- Laps are formatted eagerly to `String` and stored in `List<String>`.

---

### Approach 2: Alternative (Discrete Duration Accumulation Model)
Implemented in `work/R58-T006/AlternativeSplitSecondStopwatch.java`:
```java
public class SplitSecondStopwatch {
    private enum State { READY, RUNNING, STOPPED }

    private State state;
    private int currentLapSeconds;
    private int totalLapSeconds;
    private final List<Integer> previousLapDurations;
    ...
```
**Mechanism**:
- Discards the global epoch clock and start timestamps entirely.
- In `advanceTime()`, actively gates on state: if and only if `state == State.RUNNING`, it immediately parses and accumulates seconds into `currentLapSeconds`.
- State transitions (`start()`, `stop()`) merely validate and update the `State` enum without recording timestamps or performing epoch subtractions.
- On `lap()`, appends raw integer seconds `currentLapSeconds` into `previousLapDurations`, accumulates `totalLapSeconds`, and zeroes `currentLapSeconds`.
- Read operations (`currentLap()`, `total()`) access integer values directly with zero branching and zero timestamp arithmetic.
- Laps are formatted on-demand upon invoking `previousLaps()`.

---

## 3. Comparison & Trade-off Analysis

| Dimension | Approach 1: Maintained Reference (Epoch Offset) | Approach 2: Alternative (Duration Accumulation) |
|---|---|---|
| **Underlying Representation** | Monotonic epoch milliseconds (`long mockTime`, `currentLapStart`) | Discrete duration counters (`int currentLapSeconds`, `totalLapSeconds`) |
| **Active Lap Calculation** | Lazy: evaluated on demand via $(t_{\text{mock}} - t_{\text{start}}) + \text{accumulated}$ | Eager: directly maintained in `currentLapSeconds` |
| **`advanceTime()` Logic** | Unconditional: always adds to global `mockTime` | Conditional: filters on `state == State.RUNNING` before accumulation |
| **State Transitions** | Heavy bookkeeping: saves timestamps and updates `accumulated` | Lightweight: state flag validation and assignment only |
| **Query Complexity (`currentLap`)**| Branching: executes a 3-way `switch (state)` plus arithmetic | Direct: reads `currentLapSeconds` with zero branching |
| **Previous Laps Storage** | Formatted strings (`List<String>`) | Raw durations (`List<Integer>`) |
| **String Formatting Work** | Eager: formatted once during `lap()` | Lazy: formatted on-demand when `previousLaps()` is requested |
| **Memory Footprint** | Higher: 5 `long` fields + heap `String` objects per lap | Lower: 2 primitive `int` fields + primitive/boxed integer laps |
| **Hardware / OS Mapping** | Directly portable to real OS timers (`System.nanoTime()`) | Ideal for discrete-event loops, tick engines, and unit tests |

### When the Alternative is Clearer
1. **Discrete Simulation Contexts**: In turn-based simulations, discrete tick loops, or mocked test harnesses, storing an artificial running timestamp (`mockTime`) introduces unnecessary indirection. The alternative treats time advancement as direct delta application, which aligns naturally with how callers perceive a stopwatch.
2. **Simplified Invariants**: The reference requires synchronizing four temporal variables (`mockTime`, `currentLapStart`, `accumulated`, `totalCompletedLaps`). A defect in updating `currentLapStart` during restart or lap causes subtle drift bugs. The alternative eliminates three of these variables entirely.
3. **Branch-Free Reads**: Reading `currentLap()` or `total()` in the alternative requires no state inspection or timestamp subtraction.

### Extra Memory and Work in the Alternative
1. **Repeated Formatting Overhead**: If a client calls `previousLaps()` repeatedly without recording new laps, the alternative re-formats every completed lap duration into a new string each time, allocating $O(K)$ temporary String objects (where $K$ is the number of completed laps). In contrast, the reference amortizes this cost to a single string creation per `lap()` call.
2. **Inability to Passively Sample Wall Clocks**: In a real-world stopwatch running against `System.currentTimeMillis()`, the alternative cannot work because real time flows continuously without discrete `advanceTime` calls. The reference epoch offset pattern is strictly necessary for real-time continuous timers.

---

## 4. Test Verification Across Approaches

Both implementations were subjected to the entire 29-test JUnit test suite in isolated temporary environments. Both passed all tests with **100% agreement**:

| Test Method | JUnit `@DisplayName` | Expected Outcome | Reference | Alternative |
|---|---|---|---|---|
| `startInitiatesTimeTrackingForCurrentLap()` | `"start initiates time tracking for current lap"` | `00:00:05` | PASSED | PASSED |
| `lapAddsCurrentLapToPreviousLaps()` | `"lap adds current lap to previous laps"` | Laps: `["00:00:10"]` | PASSED | PASSED |
| `supportsVeryLongLaps()` | `"supports very long laps"` | Total: `14:08:30` | PASSED | PASSED |
| `newStopwatchStartsInReadyState()` | `"new stopwatch starts in ready state"` | State: `"ready"` | PASSED | PASSED |
| `newStopwatchCurrentLapHasNoElapsedTime()` | `"new stopwatch's current lap has no elapsed time"` | `00:00:00` | PASSED | PASSED |
| `newStopwatchTotalHasNoElapsedTime()` | `"new stopwatch's total has no elapsed time"` | `00:00:00` | PASSED | PASSED |
| `newStopwatchDoesNotHavePreviousLaps()` | `"new stopwatch does not have previous laps"` | Empty list | PASSED | PASSED |
| `startFromReadyStateChangesStateToRunning()` | `"start from ready state changes state to running"` | State: `"running"` | PASSED | PASSED |
| `startDoesNotChangePreviousLaps()` | `"start does not change previous laps"` | Empty list | PASSED | PASSED |
| `startInitiatesTimeTrackingForTotal()` | `"start initiates time tracking for total"` | `00:00:23` | PASSED | PASSED |
| `startCannotBeCalledFromRunningState()` | `"start cannot be called from running state"` | Throws `IllegalStateException` | PASSED | PASSED |
| `stopFromRunningStateChangesStateToStopped()` | `"stop from running state changes state to stopped"` | State: `"stopped"` | PASSED | PASSED |
| `stopPausesTimeTrackingForCurrentLap()` | `"stop pauses time tracking for current lap"` | `00:00:05` | PASSED | PASSED |
| `stopPausesTimeTrackingForTotal()` | `"stop pauses time tracking for total"` | `00:00:13` | PASSED | PASSED |
| `stopCannotBeCalledFromReadyState()` | `"stop cannot be called from ready state"` | Throws `IllegalStateException` | PASSED | PASSED |
| `stopCannotBeCalledFromStoppedState()` | `"stop cannot be called from stopped state"` | Throws `IllegalStateException` | PASSED | PASSED |
| `startFromStoppedStateChangesStateToRunning()` | `"start from stopped state changes state to running"` | State: `"running"` | PASSED | PASSED |
| `startFromStoppedStateResumesTimeTrackingForCurrentLap()` | `"start from stopped state resumes time tracking for current lap"` | `00:00:13` | PASSED | PASSED |
| `startFromStoppedStateResumesTimeTrackingForTotal()` | `"start from stopped state resumes time tracking for total"` | `00:00:13` | PASSED | PASSED |
| `lapResetsCurrentLapAndResumesTimeTracking()` | `"lap resets current lap and resumes time tracking"` | `00:00:05` | PASSED | PASSED |
| `lapContinuesTimeTrackingForTotal()` | `"lap continues time tracking for total"` | `00:00:15` | PASSED | PASSED |
| `lapCannotBeCalledFromReadyState()` | `"lap cannot be called from ready state"` | Throws `IllegalStateException` | PASSED | PASSED |
| `lapCannotBeCalledFromStoppedState()` | `"lap cannot be called from stopped state"` | Throws `IllegalStateException` | PASSED | PASSED |
| `stopDoesNotChangePreviousLaps()` | `"stop does not change previous laps"` | Laps: `["00:11:22"]` | PASSED | PASSED |
| `resetFromStoppedStateChangesStateToReady()` | `"reset from stopped state changes state to ready"` | State: `"ready"` | PASSED | PASSED |
| `resetResetsCurrentLap()` | `"reset resets current lap"` | `00:00:00` | PASSED | PASSED |
| `resetClearsPreviousLaps()` | `"reset clears previous laps"` | Empty list | PASSED | PASSED |
| `resetCannotBeCalledFromReadyState()` | `"reset cannot be called from ready state"` | Throws `IllegalStateException` | PASSED | PASSED |
| `resetCannotBeCalledFromRunningState()` | `"reset cannot be called from running state"` | Throws `IllegalStateException` | PASSED | PASSED |

Total: **29/29 tests passed** on both implementations with zero discrepancies.

---

## 5. Verification Commands

Run the automated verification suite:
```bash
python3 work/R58-T006/check.py
```

Or via the course check runner:
```bash
python3 tools/course_checks/r58-t006.py
```
