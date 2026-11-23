#!/usr/bin/env python3
"""Run the isolated minesweeper reference, mutant, and zero-test checks."""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from common import record_versions, run_reference_tests  # noqa: E402

TASK = "R58-T039"
EVIDENCE = ROOT / "work" / TASK
FAILING_TEST = "testInputBoardWithNoRowsAndNoColumns"


def break_empty_board(source: Path) -> None:
    text = source.read_text(encoding="utf-8")
    original = """        return result;
    }

    private String getRowWithNumbers"""
    replacement = """        return List.of("broken");
    }

    private String getRowWithNumbers"""
    if text.count(original) != 1:
        raise RuntimeError("Could not identify the single withNumbers return in the scratch reference")
    source.write_text(text.replace(original, replacement), encoding="utf-8")


def main() -> int:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    record_versions(EVIDENCE)
    reference = run_reference_tests("minesweeper", EVIDENCE / "reference")
    mutant = run_reference_tests(
        "minesweeper", EVIDENCE / "mutant", mutation=break_empty_board, expected_failure=FAILING_TEST
    )
    try:
        run_reference_tests(
            "minesweeper",
            EVIDENCE / "zero-selection",
            test_arguments=("--tests", "NoSuchMinesweeperCase"),
        )
    except RuntimeError as error:
        if "Reference test run failed" not in str(error):
            raise
    else:
        raise RuntimeError("The checker accepted a zero-test selection")
    zero_result = json.loads((EVIDENCE / "zero-selection/reference-test-results.json").read_text())
    if zero_result["tests"] != 0 or zero_result["exit_code"] == 0:
        raise RuntimeError(f"Unexpected zero-test run result: {zero_result}")
    if not all(
        item["learner_hashes_unchanged"]
        for item in (reference, mutant, zero_result)
    ):
        raise RuntimeError("Learner files changed during a runner scenario")
    (EVIDENCE / "runner-summary.json").write_text(
        json.dumps(
            {
                "reference_tests": reference["tests"],
                "reference_failures": reference["failures"],
                "mutant_failed_cases": mutant["failed_cases"],
                "zero_selection_tests": zero_result["tests"],
                "zero_selection_exit_code": zero_result["exit_code"],
                "learner_hashes_unchanged_in_all_scenarios": True,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(
        f"{TASK}: reference suite: {reference['tests']} cases discovered, "
        f"{reference['failures']} failures, {reference['skipped']} skipped; "
        "mutant fails; zero-test run rejected; learner files unchanged"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
