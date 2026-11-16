#!/usr/bin/env python3
"""Validate an exercise config.json files map and negative path fixtures."""
from __future__ import annotations
import copy,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
EXERCISE=ROOT/"exercises/practice/largest-series-product"

def validate_files(config, exercise_root):
    root=Path(exercise_root).resolve()
    errors=[]
    files=config.get("files")
    if not isinstance(files,dict):
        return ["files must be an object"]
    for role, entries in files.items():
        if not isinstance(entries,list):
            errors.append(f"{role}: expected a list")
            continue
        for entry in entries:
            if not isinstance(entry,str) or not entry:
                errors.append(f"{role}: path must be a non-empty string")
                continue
            relative=Path(entry)
            if relative.is_absolute() or ".." in relative.parts:
                errors.append(f"{role}: path escapes exercise: {entry}")
                continue
            candidate=(root/relative).resolve()
            try:
                candidate.relative_to(root)
            except ValueError:
                errors.append(f"{role}: path escapes exercise: {entry}")
                continue
            if not candidate.is_file():
                errors.append(f"{role}: missing file: {entry}")
    return errors

def expect_rejected(label, fixture, root, expected_fragment):
    errors=validate_files(fixture,root)
    if not any(expected_fragment in error for error in errors):
        raise AssertionError(f"{label} fixture was not rejected for {expected_fragment!r}: {errors}")
    print(f"PASS: {label} fixture rejected: {errors[0]}")

def main():
    config=json.loads((EXERCISE/".meta/config.json").read_text())
    errors=validate_files(config,EXERCISE)
    if errors: raise AssertionError("Real metadata invalid: "+ "; ".join(errors))
    print("PASS: all real config.json file roles resolve inside the exercise.")
    missing_reference=copy.deepcopy(config)
    missing_reference["files"]["example"][0]=".meta/src/reference/java/MissingReference.java"
    expect_rejected("missing reference",missing_reference,EXERCISE,"missing file")
    missing_test=copy.deepcopy(config)
    missing_test["files"]["test"][0]="src/test/java/MissingTest.java"
    expect_rejected("missing test",missing_test,EXERCISE,"missing file")
    outside=copy.deepcopy(config)
    outside["files"]["editor"]=["../../README.md"]
    expect_rejected("outside-exercise traversal",outside,EXERCISE,"escapes exercise")

if __name__=="__main__":
    main()
