# Pangram contract examples

The specification says the sentence must contain each letter `a` through `z`, without regard to case. These existing cases show how punctuation-like characters and digits relate to that rule:

| Case | Input | Expected | Why |
| --- | --- | --- | --- |
| `with underscores` | `the_quick_brown_fox_jumps_over_the_lazy_dog` | `true` | The letters still cover `a` through `z`; underscores do not replace letters. |
| `with numbers` | `the 1 quick brown fox jumps over the 2 lazy dogs` | `true` | The sentence contains all 26 letters; the digits add no letters. |
| `missing letters replaced by numbers` | `7h3 qu1ck brown fox jumps ov3r 7h3 lazy dog` | `false` | The input is missing `e`, `i`, and `t`; digits are not those letters. |

The exercise specifies English-letter coverage and case-insensitivity. It does not define a contract for null input or Unicode characters outside the English alphabet, so this guidance makes no additional promise about them.
