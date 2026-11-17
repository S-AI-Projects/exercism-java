# OCR numbers: test metadata and maintained JUnit source

## What is generated, and what is maintained

There are two related but distinct layers:

1. `exercises/practice/ocr-numbers/.meta/tests.toml` is the track's canonical test metadata. Its UUIDs and descriptions are synchronized from Exercism problem specifications by Configlet.
2. `exercises/practice/ocr-numbers/src/test/java/OpticalCharacterReaderTest.java` is the Java track's maintained JUnit adapter. It contains the concrete Java inputs, assertions, method names and AssertJ expectations. The repository has no per-exercise Jinja/Jinja2 template for this Java test class. Configlet does not render this Java source from `tests.toml`.

Therefore, the reproducible relationship is a **case mapping**, not a template-rendering pipeline. A maintainer updates the canonical metadata through Configlet, then maintains the Java JUnit test source so its `@DisplayName` and assertions represent the intended cases. Do not invent or hand-edit a nonexistent generated-test template.

## Reproduction commands

From the track repository root:

```bash
bin/fetch-configlet
bin/configlet sync --exercise ocr-numbers --tests
```

The second command checks the test metadata against the canonical problem specifications. To apply a deliberate metadata synchronization after reviewing the proposed changes, the Configlet update form is:

```bash
bin/configlet sync --exercise ocr-numbers --tests --update --yes
```

That update targets `.meta/tests.toml`; it does not generate `OpticalCharacterReaderTest.java`. The Java test source remains maintained by the Java track.

## Case-to-output map

| Canonical UUID | TOML description | JUnit method / display name | Input and expected result |
| --- | --- | --- | --- |
| `5ee54e1a-b554-4bf3-a056-9a7976c3f7e8` | Recognizes 0 | `testReaderRecognizesSingle0` / Recognizes 0 | 3x4 zero glyph returns `0` |
| `027ada25-17fd-4d78-aee6-35a19623639d` | Recognizes 1 | `testReaderRecognizesSingle1` / Recognizes 1 | 3x4 one glyph returns `1` |
| `3cce2dbd-01d9-4f94-8fae-419a822e89bb` | Unreadable but correctly sized inputs return ? | `testReaderReturnsQuestionMarkForUnreadableButCorrectlySizedInput` / Unreadable but correctly sized inputs return ? | Valid 3x4 dimensions with an unrecognized glyph returns `?` |

Other JUnit cases in the file cover malformed dimensions, multi-digit recognition, multiple OCR rows, and mixed readable/unreadable digits. The focused check validates the three anchor mappings and confirms that two fresh exercise copies contain byte-identical maintained JUnit source. That comparison is deliberately described as a source-reproducibility check, not as template generation.
