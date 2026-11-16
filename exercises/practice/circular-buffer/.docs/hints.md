# Circular-buffer contract walkthroughs

The buffer is a FIFO queue with a fixed capacity. The key distinction is whether the buffer is full when `overwrite` is called.

| Test case | Starting state and operations | Required result | Contract reason |
| --- | --- | --- | --- |
| `overwrite acts like write on non-full buffer` | Capacity 2; `write(1)`, then `overwrite(2)` | Reads return 1, then 2 | If there is free capacity, overwrite appends the new value and preserves existing unread values |
| `overwrite replaces the oldest item on full buffer` | Capacity 2; `write(1)`, `write(2)`, then `overwrite(3)` | Reads return 2, then 3 | When full, overwrite removes the oldest unread item before appending the new value |
| `overwrite replaces the oldest item remaining in buffer following a read` | Capacity 3; write 1, 2, 3; read 1; write 4; overwrite 5 | Reads return 3, 4, then 5 | The already-read 1 is no longer in the queue. The next oldest unread value is 2, so that is the value discarded by overwrite |
| `initial clear does not affect wrapping around` | Capacity 2; clear an empty buffer; write 1, 2; overwrite 3, 4 | Reads return 3, then 4; the next read reports empty | Clearing an empty buffer leaves it ready for ordinary writes and subsequent overwrite behavior |

Two related error contracts are explicit in the tests: reading an empty buffer throws `BufferIOException("Tried to read from empty buffer")`, and writing to a full buffer throws `BufferIOException("Tried to write to full buffer")`.

The exercise does not specify a required behavior for zero or negative capacity. Do not add an exception rule, coercion, or ordering promise for those inputs based on this exercise alone.
