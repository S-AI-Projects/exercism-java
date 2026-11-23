# Alphametics canonical-case notes

Run the reference-backed exercise tests from an isolated copy with:

```sh
python3 work/R58-T031/check.py
```

The case metadata is maintained in `exercises/practice/alphametics/.meta/tests.toml`; Configlet generates the Java test source from that metadata. The generated test file is `exercises/practice/alphametics/src/test/java/AlphameticsTest.java`. Do not edit generated tests by hand. The working reference is `exercises/practice/alphametics/.meta/src/reference/java/Alphametics.java`; the learner source remains `src/main/java/Alphametics.java`.

| UUID | Java test | Rationale | Metadata status |
| --- | --- | --- | --- |
| `e0c08b07-9028-4d5f-91e1-d178fead8e1a` | `testThreeLetters` | `I + BB == ILL` has the mapping `I=1`, `B=9`, `L=0` (`1 + 99 = 100`). | Included |
| `a504ee41-cb92-4ec2-9f11-c37e95ab3f25` | `testUniqueValue` | `A == B` cannot be satisfied when distinct letters must map to distinct digits. | Included |
| `4e3b81d2-be7b-4c5c-9a80-cd72bc6d465a` | `testLeadingZero` | In `ACA + DD == BD`, the units column forces `A=0`; `A` is a leading letter, so the puzzle is unsolvable. | Included |

The full metadata currently contains 10 cases: 10 included and 0 excluded. These three entries remain included; their Java assertions already cover the stated constraints, so no test inclusion was changed.
