# Choosing a crypto-square approach

The reference normalizes the text, splits it into row strings, then reads each column across those rows. This makes the rectangle visible in the code and makes the padding rule easy to follow, at the cost of storing the row substrings.

An alternative is to keep the normalized text as one string and calculate each column's character index directly. For `Chill out.`, normalization gives `chillout`, which fills the rows `chi`, `llo`, and `ut `. Reading column positions produces `clu hlt io `. The direct-index approach avoids allocating row strings, but the index and out-of-range padding logic are less visually obvious.

Both approaches must use the same rectangle dimensions and preserve trailing spaces in short final columns. The comparison checker exercises both implementations against the same examples without placing an experimental solution in the learner source.
