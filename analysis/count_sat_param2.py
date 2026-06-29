#!/usr/bin/env python3
"""Count satisfiable rows whose Param_2 matches a target value.

Usage:
  python3 count_sat_param2.py file1.csv file2.csv --param2 4000

If no input files are provided, the script defaults to the two b04 "other"
CSV files in the repository.
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_INPUTS = [
    ROOT_DIR / "b04_results" / "b04_other_1.csv",
    ROOT_DIR / "b04_results" / "b04_other_2.csv",
]


def is_success(row: dict[str, str]) -> bool:
    result_text = str(row.get("Result", "")).lower()
    tool_name = str(row.get("Tool", "")).strip()

    if tool_name == "Phaserr":
        return "success" in result_text
    if tool_name in {"Spacer", "Golem"}:
        return "sat" in result_text and "unsat" not in result_text
    return False


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT_DIR))
    except ValueError:
        return str(path)


def count_matching_rows(path: Path, target_param2: float, tolerance: float) -> dict[str, object]:
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = set(reader.fieldnames or [])
        required_columns = {"Param_2", "Result", "Tool"}
        missing_columns = sorted(required_columns - fieldnames)
        if missing_columns:
            raise ValueError(
                f"{display_path(path)} is missing required columns: {', '.join(missing_columns)}"
            )

        row_count = 0
        filenames: set[str] = set()
        per_tool_counter: Counter[str] = Counter()

        for row in reader:
            try:
                param_2 = float(str(row.get("Param_2", "")).strip())
            except ValueError:
                continue

            if abs(param_2 - target_param2) > tolerance or not is_success(row):
                continue

            row_count += 1
            filename = str(row.get("Filename", "")).strip()
            if filename:
                filenames.add(filename)

            tool_name = str(row.get("Tool", "")).strip()
            if tool_name:
                per_tool_counter[tool_name] += 1

    per_tool = {
        tool: int(count) for tool, count in sorted(per_tool_counter.items())
    }

    return {
        "row_count": row_count,
        "filenames": filenames,
        "per_tool": per_tool,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Count satisfiable rows whose Param_2 equals a target value"
    )
    parser.add_argument(
        "inputs",
        nargs="*",
        help="CSV files to analyze. Defaults to b04_other_1.csv and b04_other_2.csv.",
    )
    parser.add_argument(
        "--param2",
        type=float,
        default=4000.0,
        help="Target Param_2 value to match (default: 4000)",
    )
    parser.add_argument(
        "--tolerance",
        type=float,
        default=1e-9,
        help="Allowed absolute error when comparing Param_2 values",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    input_paths = [Path(path) for path in args.inputs] or list(DEFAULT_INPUTS)

    missing_files = [path for path in input_paths if not path.exists()]
    if missing_files:
        for path in missing_files:
            print(f"Input file does not exist: {path}")
        return 2

    total_rows = 0
    total_filenames: set[str] = set()

    for path in input_paths:
        stats = count_matching_rows(path, args.param2, args.tolerance)
        total_rows += int(stats["row_count"])
        total_filenames.update(stats["filenames"])

        tool_summary = ""
        per_tool = stats["per_tool"]
        if per_tool:
            tool_summary = " | by tool: " + ", ".join(
                f"{tool}={count}" for tool, count in per_tool.items()
            )

        print(
            f"{display_path(path)}: {stats['row_count']} satisfiable rows with "
            f"Param_2={args.param2:g}; {len(stats['filenames'])} distinct benchmark files"
            f"{tool_summary}"
        )

    print(
        f"Total satisfiable rows with Param_2={args.param2:g}: {total_rows}"
    )
    print(
        "Total distinct benchmark files with satisfiable rows and matching Param_2: "
        f"{len(total_filenames)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())