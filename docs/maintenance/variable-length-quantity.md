# Variable-length-quantity: mutation and regression evidence

## Contract under examination

The exercise encodes each unsigned 32-bit integer as groups of seven payload bits. The most-significant bit of each output byte indicates continuation: it is set for every non-final byte and clear for the final byte.

## Deliberate scratch mutation

The maintained reference in `exercises/practice/variable-length-quantity/.meta/src/reference/java/VariableLengthQuantity.java` advances to the next payload group with a seven-bit right shift. The mutation used by the focused checker changes that shift from seven to six bits in `encodeSingleNumber`. This is a semantic mutation: it changes the grouping boundary, not merely formatting.

## Smallest diagnostic case

| Input | Correct output | Mutant output | Rejecting test |
| --- | --- | --- | --- |
| `0x80` | `[0x81, 0x0]` | `[0x82, 0x0]` | `testSmallestDoubleByte` (`smallest double byte`) |

The input `0x80` is the smallest value requiring two VLQ bytes. Its expected output is defined by the exercise's seven-bit grouping rule. The test's canonical case ID is `77b07086-bd3f-4882-8476-8dcafee79b1c`.

## Reproduction

From the repository root, run:

```bash
python3 work/R58-T013/check.py
```

The checker runs the unmodified reference first, then applies the one-line mutation only in a temporary copy and runs the named regression test there. It never edits the learner starter source or the maintained reference in the working tree. A successful mutation experiment means the original run passes and the mutant run fails specifically at `testSmallestDoubleByte`; it does not imply that the maintained implementation is defective.
