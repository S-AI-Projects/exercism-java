# Hints

## Approach Selection: Epoch Timestamps vs. Discrete Duration Accumulation

When implementing a stopwatch capable of recording laps and pausing time, you need a representation for tracking the elapsed time of the active lap, completed laps, and overall total duration.

There are two primary architectural representations to model time tracking:

### 1. Continuous Wall-Clock / Epoch Offset Model
- **Mechanism**: The stopwatch maintains a simulated global monotonic clock (`mockTime` or system timestamp in milliseconds) and records an epoch marker whenever the active segment begins (`currentLapStart = mockTime`).
- **State Handling**: Time elapsed during the current segment is computed lazily upon query or state change using delta arithmetic: $(t_{\text{current}} - t_{\text{start}}) + \text{accumulated}$. Pausing saves the accrued time into an `accumulated` offset, and completed laps are pushed to a collection.
- **Trade-offs**:
  - *Advantage*: Matches real hardware timers and real-world system clocks (`System.currentTimeMillis()` / `System.nanoTime()`), where time continuously elapses in the background without needing explicit tick notifications.
  - *Overhead*: Requires tracking multiple timestamp state variables (global time, segment start, accumulated pause offset, completed lap totals). Every query to `currentLap()` or `total()` performs arithmetic and state-conditional branching (`switch (state)`).

### 2. Discrete Duration Accumulation Model
- **Mechanism**: Rather than tracking absolute timestamps, the stopwatch maintains direct duration counters (e.g., active lap seconds and total elapsed seconds).
- **State Handling**: Whenever `advanceTime(timeString)` is called, the stopwatch checks its current state. If `RUNNING`, it directly accumulates the converted elapsed duration into the active lap counter. If `STOPPED` or `READY`, advancing external time has no effect on internal counters.
- **Trade-offs**:
  - *Advantage*: Significantly simpler control flow and state representation. State transitions (`start()`, `stop()`) merely set a status flag without recording or subtracting epoch timestamps. Querying `currentLap()` requires zero arithmetic or conditional branches—the duration counter is already exact.
  - *Overhead*: Storing completed laps as unformatted numeric durations (`List<Integer>`) requires on-demand string formatting when `previousLaps()` is requested. Additionally, this approach relies on discrete tick events (`advanceTime`) and cannot passively read continuous system wall clocks.

---

## Worked Example: Tracing Stopwatch Laps and State Transitions

Consider a runner executing an interval workout:

1. **Initialization (`READY` state)**:
   - Initial state: `"ready"`, current lap: `"00:00:00"`, total: `"00:00:00"`, previous laps: `[]`.

2. **First Interval (`start()` $\to$ `advanceTime("00:00:25")`)**:
   - `start()` sets state to `"running"`.
   - `advanceTime("00:00:25")` adds $25\text{s}$ ($0 \times 3600 + 0 \times 60 + 25 = 25\text{s}$).
   - `currentLap()` evaluates to `"00:00:25"`, `total()` evaluates to `"00:00:25"`.

3. **Recording a Lap (`lap()` $\to$ `advanceTime("00:00:40")`)**:
   - `lap()` commits the active duration ($25\text{s}$) to previous laps and resets the active lap counter to $0\text{s}$.
   - Previous laps now contains: `["00:00:25"]`.
   - `advanceTime("00:00:40")` adds $40\text{s}$ to the new active lap.
   - `currentLap()` evaluates to `"00:00:40"`.
   - `total()` evaluates to $25\text{s} + 40\text{s} = 65\text{s} \implies$ `"00:01:05"`.

4. **Pausing (`stop()` $\to$ `advanceTime("00:00:15")` $\to$ `start()`)**:
   - `stop()` transitions state to `"stopped"`.
   - `advanceTime("00:00:15")` occurs while stopped: the stopwatch does **not** accrue elapsed time.
   - `currentLap()` remains `"00:00:40"`, and `total()` remains `"00:01:05"`.
   - `start()` transitions state back to `"running"`.

5. **Completing the Segment (`advanceTime("00:00:20")`)**:
   - Adding $20\text{s}$ brings current lap to $40\text{s} + 20\text{s} = 60\text{s} \implies$ `"00:01:00"`.
   - `total()` evaluates to $25\text{s} + 60\text{s} = 85\text{s} \implies$ `"00:01:25"`.
   - Previous laps remains untouched: `["00:00:25"]`.

---

## Key Takeaway
Decide whether your application benefits more from **passive timestamp delta calculation** (best when bound to real continuous hardware clocks) or **active discrete event accumulation** (best for discrete simulation steps, unit testing, and simpler memory layouts).
