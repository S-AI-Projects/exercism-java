# Bowling Exercise Maintenance

## Overview

This document records the mutation analysis for the `bowling` practice exercise
as part of Task R58-T023. It identifies a deliberate code mutant, the existing
test case that rejects it, and the expected correct behaviour.

---

## Mutant Description

**File mutated**: `.meta/src/reference/java/Frame.java`  
**Original line**:
```java
private static int nextNextRoll(Frame next, Frame nextNext) {
    return next.isStrike() ? nextNext.first : next.second;
}
```
**Mutant line** (one condition changed):
```java
private static int nextNextRoll(Frame next, Frame nextNext) {
    return next.isStrike() ? next.first : next.second;
    // BUG: when next is a strike, the second strike bonus roll should come from
    // nextNext.first (the first roll of the frame after the strike), not next.first
    // (the strike itself, which equals 10).
}
```

**What the mutant does**: When computing the two-roll bonus for a strike and the
immediately following frame is *also* a strike, the mutant uses the second strike's
value (`next.first = 10`) again instead of the first roll of the *third* frame
(`nextNext.first`). This inflates the score for each pair of consecutive strikes.

---

## Rejecting Test Case

| Item | Value |
|---|---|
| **UUID** | `1635e82b-14ec-4cd1-bce4-4ea14bd13a49` |
| **Description** | `consecutive strikes each get the two roll bonus` |
| **Java method** | `consecutiveStrikesEachGetTheTwoRollBonus()` |
| **Input rolls** | `[10, 10, 10, 5, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]` |
| **Expected score** | `81` |
| **Mutant score** | `91` (over-counts: frame 1 bonus becomes 10+10 instead of 10+10, frame 2 bonus becomes 10+10 instead of 10+5) |

**Detailed scoring (correct)**:
- Frame 1 (strike): 10 + 10 (frame 2 first) + 10 (frame 3 first) = **30**
- Frame 2 (strike): 10 + 10 (frame 3 first) + 5 (frame 4 first) = **25**
- Frame 3 (strike): 10 + 5 + 3 = **18**
- Frame 4: 5 + 3 = **8**
- Frames 5–10: 0

Total = 30 + 25 + 18 + 8 = **81**

**Mutant scoring (wrong)**:
- Frame 1 (strike): 10 + 10 (frame 2 first) + 10 (frame 2 first again, bug!) = **30** (coincidentally same here)
- Frame 2 (strike): 10 + 10 (frame 3 first) + 10 (frame 3 first again, bug!) = **30** (should be 25)
- Frame 3 (strike): 10 + 5 + 3 = **18**
- Frame 4: 5 + 3 = **8**

Mutant total = 30 + 30 + 18 + 8 = **86** (differs by +5 from correct)

> [!NOTE]
> The smallest input that distinguishes correct from mutant behaviour is any game
> containing at least two consecutive strikes followed by a non-strike frame.
> Minimum: `[10, 10, 5, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]`
> Correct = 10+10+5 + 10+5+3 + 5+3 = 25+18+8 = **51**
> Mutant  = 10+10+10 + 10+5+3 + 5+3 = 30+18+8 = **56**

---

## Named Cases (Anchored for Task R58-T023)

| UUID | Description | Java Method |
|---|---|---|
| `75269642-2b34-4b72-95a4-9be28ab16902` | a strike earns ten points in a frame with a single roll | `aStrikeEarnsTenPointsInFrameWithASingleRoll()` |
| `037f978c-5d01-4e49-bdeb-9e20a2e6f9a6` | points scored in the two rolls after a strike are counted twice as a bonus | `pointsScoredInTheTwoRollsAfterAStrikeAreCountedTwiceAsABonus()` |
| `1635e82b-14ec-4cd1-bce4-4ea14bd13a49` | consecutive strikes each get the two roll bonus | `consecutiveStrikesEachGetTheTwoRollBonus()` |

---

## Reproduction

```bash
python3 work/R58-T023/check.py
```
