# Nucleotide Count file roles

`exercises/practice/nucleotide-count/.meta/config.json` maps each Exercism file
role to a path relative to the exercise directory. The runner reads the
`files.solution`, `files.test`, and `files.example` entries from that object;
it does not need to guess file locations from filenames.

| Role | Config path | Purpose |
| --- | --- | --- |
| `solution` | `src/main/java/NucleotideCounter.java` | Learner starter file; remains unsolved in this task. |
| `test` | `src/test/java/NucleotideCounterTest.java` | Java track test source used by Gradle. |
| `example` | `.meta/src/reference/java/NucleotideCounter.java` | Maintained Java reference copied into a temporary test project as the solution. |
| `invalidator` | `build.gradle` | Build-file change marker used by track tooling. |
| `editor` | Not declared | This exercise has no editor file entry. If one is added, it must also be an existing path under this exercise. |

The canonical test case definitions live in `.meta/tests.toml`. The Java test
source is the track-facing test artifact generated from those definitions; the
two files serve different roles and should not be confused. The reference
implementation is not copied over the learner file in the working tree.

Validate the metadata and its missing-reference, missing-test, and path
traversal fixtures with:

```sh
python3 tools/course_checks/r58-t028.py
```

Run the reference exercise tests, path validation, and the test-count assertion
with:

```sh
python3 work/R58-T028/check.py
```
