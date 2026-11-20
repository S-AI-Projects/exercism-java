# Zebra Puzzle: Constraint Satisfaction and Solution Guidance

## Overview

The Zebra Puzzle is a classic constraint satisfaction problem (CSP) where five houses in a row must be assigned unique attributes across five categories:
- **House Position**: 1 (first/leftmost), 2, 3 (middle), 4, 5 (rightmost)
- **House Color**: Red, Green, Ivory, Yellow, Blue
- **Inhabitant Nationality**: Englishman, Spaniard, Ukrainian, Japanese, Norwegian
- **Beverage**: Coffee, Tea, Milk, Orange juice, Water
- **Pet**: Dog, Snails, Fox, Horse, Zebra
- **Hobby**: Dancing, Painter, Reading, Football, Chess

The exercise contract requires answering two specific questions via parameterless methods:
1. `getWaterDrinker()`: Returns the nationality of the resident who drinks water (`"Norwegian"`).
2. `getZebraOwner()`: Returns the nationality of the resident who owns the zebra (`"Japanese"`).

---

## Step-by-Step Constraint Deduction

The 15 statements in the specification uniquely determine the attribute of every house through deductive elimination:

### 1. Positional Anchors
- **Statement 10**: The Norwegian lives in the first house $\implies \text{House 1} = \text{Norwegian}$.
- **Statement 15**: The Norwegian lives next to the blue house $\implies \text{House 2} = \text{Blue}$ (the only neighbor of House 1).
- **Statement 9**: The person in the middle house drinks milk $\implies \text{House 3} = \text{Milk}$.

### 2. House Colors and Hobbies
- **Statement 6**: The green house is immediately to the right of the ivory house.
  The adjacent pair $(\text{Ivory}, \text{Green})$ can only be $(3, 4)$ or $(4, 5)$ because House 2 is Blue.
- **Statement 4**: The person in the green house drinks coffee.
  Since House 3 drinks Milk, Green cannot be House 3.
- **Statement 2**: The Englishman lives in the red house.
  House 1 is Norwegian and House 2 is Blue, so Red must be House 3 or House 5.
  - If $(\text{Ivory}, \text{Green}) = (3, 4)$, Red must be House 5 and Yellow must be House 1.
  - If $(\text{Ivory}, \text{Green}) = (4, 5)$, Red must be House 3 and Yellow must be House 1.
  - In both scenarios, **House 1 is Yellow**.
- **Statement 8**: The person in the yellow house is a painter $\implies \text{House 1} = \text{Painter}$.
- **Statement 12**: The painter's house is next to the house with the horse $\implies \text{House 2} = \text{Horse}$.

### 3. Beverages and Water Drinker
- **Statement 5**: The Ukrainian drinks tea.
  Ukrainian cannot be House 1 (Norwegian), House 3 (Milk), or the Green house (Coffee).
  Thus, $\text{House 2} = \text{Ukrainian}$ and drinks **Tea**.
- **Statement 13**: The person who plays football drinks orange juice.
  Football/Orange juice cannot be House 1 (Painter), House 2 (Tea), House 3 (Milk), or Green (Coffee).
  Thus, Orange juice must be in the remaining house: **House 4** ($\text{House 4} = \text{Orange juice}$, $\text{Football}$).
- **Water Deduction**:
  The five beverages are Coffee, Tea, Milk, Orange juice, and Water.
  - House 5 (Green) = Coffee
  - House 2 (Blue) = Tea
  - House 3 = Milk
  - House 4 = Orange juice
  - This leaves only **House 1** for **Water**.
  - Since House 1 is the Norwegian, **the Norwegian drinks water**.
  - This fixes the colors: $\text{House 4} = \text{Ivory}$, $\text{House 5} = \text{Green}$, and $\text{House 3} = \text{Red}$ ($\text{Englishman}$).

### 4. Pets, Nationalities, and Zebra Owner
- **Statement 14**: The Japanese person plays chess.
  Remaining nationalities are Japanese and Spaniard for Houses 4 and 5.
  House 4 already has the hobby Football. Thus, **House 5 = Japanese** (plays **Chess**).
- **Statement 3**: The Spaniard owns the dog $\implies \text{House 4} = \text{Spaniard}$ (owns **Dog**).
- **Hobbies**:
  Remaining hobbies are Dancing and Reading for Houses 2 and 3.
  - **Statement 7**: The snail owner likes to go dancing $\implies \text{House 3} = \text{Dancing}$ (owns **Snails**).
  - This leaves $\text{House 2} = \text{Reading}$.
- **Statement 11**: The person who enjoys reading lives next to the person with the fox.
  House 2 enjoys Reading, so Fox must be next to House 2.
  House 3 already has Snails, so $\text{House 1} = \text{Fox}$.
- **Zebra Deduction**:
  The five pets are Fox (House 1), Horse (House 2), Snails (House 3), Dog (House 4), and Zebra.
  The only house without an assigned pet is **House 5**.
  Therefore, **House 5 owns the Zebra**.
  Since the Japanese person lives in House 5, **the Japanese person owns the zebra**.

---

## Full House Assignment Matrix

| House | 1 (First) | 2 | 3 (Middle) | 4 | 5 (Fifth) |
|---|---|---|---|---|---|
| **Color** | Yellow | Blue | Red | Ivory | Green |
| **Nationality** | Norwegian | Ukrainian | Englishman | Spaniard | Japanese |
| **Beverage** | **Water** | Tea | Milk | Orange juice | Coffee |
| **Pet** | Fox | Horse | Snails | Dog | **Zebra** |
| **Hobby** | Painter | Reading | Dancing | Football | Chess |

---

## Decision Table

The decision table maps each test case and method call to its required outcome based strictly on the exercise specification:

| Test Case | Method Invocation | Input Condition & Constraints Applied | Required Outcome | Contract Deduction |
|---|---|---|---|---|
| `resident who drinks water` | `new ZebraPuzzle().getWaterDrinker()` | Statements 1, 4, 5, 8, 9, 10, 13, 15: Norwegian in House 1, Blue in House 2, Milk in House 3; Green drinks Coffee, Ukrainian drinks Tea, Football drinks Orange juice. All other beverages eliminated for House 1. | `"Norwegian"` | Only the Norwegian residing in House 1 can drink water without violating any beverage, color, or hobby constraint. |
| `resident who owns zebra` | `new ZebraPuzzle().getZebraOwner()` | Statements 1–15: Full constraint propagation fixes House 5 as Green/Coffee/Japanese/Chess. Pets for Houses 1–4 are Fox, Horse, Snails, Dog. All other pets eliminated for House 5. | `"Japanese"` | The Japanese resident in House 5 is the sole inhabitant who can own the zebra under the complete constraint set. |

---

## Separating Specified Behavior from Inputs Outside the Exercise Contract

### Explicit Statement on Unspecified Behavior

The exercise specification defines a focused query contract. Learners and maintainers must clearly separate specified behavior from inputs outside the exercise contract and behavior that is intentionally left unspecified:

1. **Parameterless Queries**: Both `getWaterDrinker()` and `getZebraOwner()` take no parameters. The constructor takes no arguments.
2. **Intermediate and Out-of-Contract Queries**:
   - The contract does **not** specify methods to query other attributes (such as `getFoxOwner()`, `getCoffeeDrinker()`, or `getHouseColor(int)`).
   - Implementations must not add or require extraneous query methods in the public contract.
3. **No Dynamic or Parametric Configuration**:
   - The class does not accept runtime statement lists, variable house counts ($N \ne 5$), or custom constraint models.
   - The puzzle rules are static and fixed by the problem description.
4. **Error & Exception Contracts**:
   - Neither `getWaterDrinker()` nor `getZebraOwner()` specifies or throws checked or unchecked exceptions during standard execution.
   - Do not add artificial exception rules, argument-checking guards, or error codes for out-of-contract calls.
5. **String Formatting & Typing**:
   - Expected outputs are exact case-sensitive strings: `"Norwegian"` and `"Japanese"`.
   - No lowercase coercion, trimming, localized spelling, or enum types are required or permitted by the test assertions.
6. **Invocation Ordering & Idempotence**:
   - The query methods are idempotent and state-independent. Calling `getZebraOwner()` before `getWaterDrinker()`, calling either method repeatedly, or calling only one method must yield identical results without side effects.
7. **Implementation Strategy**:
   - The specification leaves the underlying solving mechanism unspecified. Backtracking search, constraint propagation, permutation filtering, or precomputed result return are all valid provided the public interface contract is strictly satisfied.
