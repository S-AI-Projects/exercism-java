# Task R58-T002 Verification Evidence

## Exercise: `exercises/practice/isogram`

This directory records the verification check and execution evidence for Task R58-T002.

### Execution Command

Run from the repository root:

```bash
python3 work/R58-T002/check.py
```

### Verification Pipeline

The check script performs the following end-to-end checks:
1. **Metadata & Path Resolution**: Reads `exercises/practice/isogram/.meta/config.json` to resolve paths for solution, test, and reference example files.
2. **Canonical Data Verification**: Parses `exercises/practice/isogram/.meta/tests.toml` and confirms all 14 canonical test cases are present.
3. **Cross-Check Test Methods**: Confirms that JUnit 5 `@DisplayName` annotations in `src/test/java/IsogramCheckerTest.java` match 1:1 with descriptions in `.meta/tests.toml`.
4. **Round-Trip Consistency**: Generates two independent copies in scratch directories and verifies they produce byte-identical tests after timestamp normalization.
5. **Learner Stub Integrity**: Confirms `src/main/java/IsogramChecker.java` remains unsolved and throws `UnsupportedOperationException`.
6. **Isolated Test Execution**: Copies the exercise (including dotfiles) to a temporary directory, copies the reference implementation into `src/main/java`, unskips `@Disabled` test markers in the copy only, and executes `./gradlew test`.
7. **Anchor Cases & Test Counts**:
   - `testEmptyString()`: UUID `a0e97d2d-669e-47c7-8134-518a1e2c4555` -> PASSED
   - `testLowercaseIsogram()`: UUID `9a001b50-f194-4143-bc29-2af5ec1ef652` -> PASSED
   - `testNotIsogram()`: UUID `8ddb0ca3-276e-4f8b-89da-d95d5bae78a4` -> PASSED
   - All other 11 enabled cases -> PASSED
   - Total executed: 14, Failures: 0, Errors: 0, Skipped: 0.
8. **Negative Validations**: Confirms that deliberate mutant solutions and zero-test selections are correctly rejected with non-zero exits.
9. **Working Tree Safety**: Confirms the working tree learner files remain completely unmodified.

Evidence outputs are written to `work/R58-T002/results.json` and `work/R58-T002/latest-result.json`.
