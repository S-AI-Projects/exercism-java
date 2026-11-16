# Simple Cipher — Canonical Test Decisions

## Overview

This document records the rationale for the three canonical test cases investigated for the Simple Cipher exercise.

The exercise implements the Vigenère cipher. Its specification requires lowercase alphabetic keys, key-based character shifts, key wrapping and reversible encoding and decoding.

**Decision summary:** All three investigated canonical cases remain included. No exclusions are proposed.

## UUID-to-test mapping
| Canonical UUID | Java test method | Decision |
|---|---|---|
| `b8bdfbe1-bea3-41bb-a999-b41403f2b15d` | `randomKeyCipherCanEncode()` | Include |
| `3dff7f36-75db-46b4-ab70-644b3f38b81c` | `randomKeyCipherCanDecode()` | Include |
| `8143c684-6df6-46ba-bd1f-dea8fcb5d265` | `randomKeyCipherIsReversible()` | Include |
## Individual rationales

### 1. Can encode

**UUID:** `b8bdfbe1-bea3-41bb-a999-b41403f2b15d`

**Java test:** `randomKeyCipherCanEncode()`

The test uses ten `a` characters as plaintext. Since `a` represents a shift of zero, encoding these characters produces the corresponding first ten characters of the random key.

The Java assertion compares the encoded output with `randomKeyCipher.getKey().substring(0, 10)`.

**Decision:** Include. This verifies that random-key generation and encoding work together correctly.

### 2. Can decode

**UUID:** `3dff7f36-75db-46b4-ab70-644b3f38b81c`

**Java test:** `randomKeyCipherCanDecode()`

The test uses the first ten characters of the generated key as ciphertext. Decoding each character using the corresponding key character should produce `aaaaaaaaaa`.

**Decision:** Include. This verifies decoding with a generated random key. The Java test is currently disabled, but its intended behaviour is consistent with the exercise specification.

### 3. Is reversible

**UUID:** `8143c684-6df6-46ba-bd1f-dea8fcb5d265`

**Java test:** `randomKeyCipherIsReversible()`

The test encodes `abcdefghij` and then decodes the result using the same random-key cipher instance.

The expected result is the original plaintext.

The message contains ten characters, while the reference implementation generates a key of 100 characters. Therefore, the test does not require key wrapping.

**Decision:** Include. Reversibility is a fundamental property of the cipher and is explicitly consistent with the exercise's encoding and decoding requirements.

## Reference implementation observations

The reference implementation generates a 100-character random key and validates supplied keys using lowercase alphabetic characters.

Its `encode()` method extends the key when the plaintext is longer than the key.

However, `decode()` directly indexes the original key without extending it. This creates a potential limitation for decoding messages longer than the key.

This implementation limitation does not invalidate the three investigated cases because their messages are shorter than the generated random key.

## Final decision

- Investigated canonical cases: 3
- Included: 3
- Excluded: 0

All three cases remain included. No canonical inclusion values are changed.
