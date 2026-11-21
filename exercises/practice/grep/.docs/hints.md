# Hints

## Reading the matching and output rules

These examples use the fixed-string contract in the exercise. Files are
searched in the order supplied, and matching lines stay in their original
order. When more than one file is searched, a matching line includes its file
name. `-n` adds the 1-based line number after that name. `-l` changes the
output to file names only, so it takes precedence over printing matching lines
and line numbers.

| Test case | Inputs | Required output | Why |
| --- | --- | --- | --- |
| `multipleFilesOneMatchMultipleFlags` | Pattern `WITH LOSS OF EDEN, TILL ONE GREATER MAN`; flags `-n`, `-i`, `-x`; files `iliad.txt`, `midsummer-night.txt`, `paradise-lost.txt` | `paradise-lost.txt:4:With loss of Eden, till one greater Man` | `-i` ignores case, `-x` requires the whole line to equal the pattern, and `-n` adds line 4. Multiple-file output prefixes the filename. |
| `multipleFilesSeveralMatchesFileFlagTakesPrecedenceOverLineNumberFlag` | Pattern `who`; flags `-n`, `-l`; same three files | `iliad.txt` then `paradise-lost.txt` on separate lines | Both files contain a match. `-l` emits one filename per matching file, so matching text and `-n` line numbers are omitted. File order follows the supplied list. |

In Java, `grep` returns a single `String`: separate output entries are joined
with `\n`. The tests compare that string exactly, including the order and
prefixes shown above.

The contract describes searching for fixed strings. It does not require
regular-expression interpretation. It also does not define what to do with an
unknown flag, a missing or unreadable file, or null arguments. The reference
currently treats an I/O failure as an empty file; do not assume that behavior
is a required error rule for learner solutions.
