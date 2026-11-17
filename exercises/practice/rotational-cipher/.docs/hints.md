# Choosing a rotational-cipher implementation

There are two useful ways to represent the same rotation.

## Character-code arithmetic (the maintained reference)

The reference shifts a character's code point by the key, then adjusts it when it crosses the end of that character's alphabet. This avoids searching for the character in an alphabet string. It is compact and performs a constant amount of work per input character.

## Alphabet lookup (an alternative)

A second approach stores the lowercase and uppercase alphabets as strings. For each letter, find its index with `indexOf`, add the normalized key, and use modulo 26 to wrap around. Characters that are not letters are copied unchanged.

Worked example: with key 5, `o` is at index 14 in the lowercase alphabet. Moving five positions gives index 19, which is `t`; therefore `omg` becomes `trl`. The same lookup is performed in the uppercase alphabet for capital letters.

The lookup approach makes the wrap-around rule visible and avoids separate start/end character arithmetic. Its trade-off is that `indexOf` searches up to 26 alphabet positions for each letter. Because the alphabet size is fixed, this remains O(n) in the input length, but it has a larger constant factor than direct character arithmetic. Both approaches need an output buffer proportional to the input length.

The punctuation and digit cases matter: the cipher rotates only Latin letters and preserves spaces, digits and punctuation exactly. The alternative implementation used for comparison is retained as experimental evidence under `work/R58-T016/`; it is not a replacement learner solution.
