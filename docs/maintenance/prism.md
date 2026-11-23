# Prism test maintenance

## Sources and commands

Canonical case metadata lives in `exercises/practice/prism/.meta/tests.toml`. `configlet sync --tests` checks or updates that metadata from Exercism's `problem-specifications`; it does not render `PrismTest.java`. There is no per-exercise Jinja template in this repository. The Java assertions in `exercises/practice/prism/src/test/java/PrismTest.java` are the maintained test source, so do not invent or invoke a nonexistent template.

Install Configlet and check the canonical metadata from the repository root:

```sh
./bin/fetch-configlet
./bin/configlet sync --exercise prism --tests
```

Run the Java exercise tests from the prism directory:

```sh
cd exercises/practice/prism
./gradlew test
```

The focused coursework check runs the metadata synchronization in two fresh track copies, compares the resulting canonical metadata and Java test source, and runs the reference tests in an isolated exercise copy:

```sh
python3 work/R58-T032/check.py
```

## Case mapping

| UUID | Canonical description | Java test method | Java source outcome |
| --- | --- | --- | --- |
| `ec65d3b3-f7bf-4015-8156-0609c141c4c4` | `zero prisms` | `testZeroPrisms` | Empty prism input returns an empty sequence. |
| `ec0ca17c-0c5f-44fb-89ba-b76395bdaf1c` | `one prism one hit` | `testOnePrismOneHit` | A ray through prism 1 returns sequence `[1]`. |
| `0db955f2-0a27-4c82-ba67-197bd6202069` | `one prism zero hits` | `testOnePrismHitsZero` | A prism behind the ray is not hit, so the sequence is empty. |

The complete source currently has 14 TOML cases and 14 Java `@DisplayName` cases. The one-prism/one-hit case is disabled in the learner test file until the exercise is implemented; the reference-backed check runs the full test source against the maintained reference.
