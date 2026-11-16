# Connect reference: scoped readability refactor

## Change

The refactor renames `boardHorizontalSize` and `boardVerticalSize` to `boardWidth` and `boardHeight`. These names describe the dimensions represented by the values: the number of columns and rows. It also names the two degenerate-board predicates by the actual winning direction: O connects top-to-bottom and X connects left-to-right.

The constructor's loop variables now use `rowIndex` and `columnIndex`, which makes their roles explicit while scanning the board. The connectivity algorithm, `Board` and `UnionFind` collaborators, public constructor, return type, enum values, and ordering of winner checks remain unchanged.

## Important invariant

If a player's target edge collapses to a single cell, that cell must contain that player's stone. The 1x1 tests make this edge case visible. O's top/bottom connection is degenerate when the board width is one; X's left/right connection is degenerate when the board height is one. The renamed predicates make this orientation rule explicit.

## Verification

Run:

```bash
python3 work/R58-T014/check.py
```

The checker runs the original snapshot and the refactored reference in separate temporary exercise copies with the same enabled JUnit suite. It compares test counts and requires both runs to pass. It also verifies that learner starter files are unchanged. The original snapshot is kept under `work/R58-T014/original/` solely to make the before/after comparison reproducible.
