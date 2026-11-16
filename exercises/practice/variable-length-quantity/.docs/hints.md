# Debugging variable-length quantity encoding

VLQ stores **seven payload bits per byte**. The high bit is a continuation marker: it is set on every byte except the final byte. When a value needs more than seven bits, the encoder must move the next group of payload bits into the preceding byte without losing or overlapping bits.

A useful boundary is `0x80`, the smallest value that cannot fit in one seven-bit payload:

| Input value | Expected encoded bytes | Why |
| --- | --- | --- |
| `0x7f` | `0x7f` | The value fits in one payload byte, so its continuation bit is clear |
| `0x80` | `0x81 0x00` | One payload bit remains after the first seven-bit group, so the first byte continues and the final byte ends the value |

**Debugging hint:** if your output for `0x80` starts with `0x82`, check the size of the bit group you move between bytes. VLQ groups are seven bits wide, not six or eight. Also keep the continuation marker separate from the seven payload bits.

The contract restricts inputs to unsigned 32-bit values. This hint concerns encoding values within that stated range; it does not introduce behavior for negative or larger values.
