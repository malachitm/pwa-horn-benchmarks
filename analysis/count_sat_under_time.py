#!/usr/bin/env python3
"""Count satisfiable rows whose runtime is below a target threshold.

Usage:
  python3 count_sat_under_time.py file.csv --max-time 20

If no input files are provided, the script defaults to b04_phaserr.csv.
For raw solver CSVs, satisfiable rows are identified from the Result column.
For cleaned Phaserr CSVs that omit Result, rows with numeric runtime data are
treated as solved rows.
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_INPUTS = [
    ROOT_DIR / "b04_results" / "b04_phaserr.csv",
]


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT_DIR))
    except ValueError:
        return str(path)


def is_satisfiable(row: dict[str, str], fieldnames: set[str]) -> bool:
    tool_name = str(row.get("Tool", "")).strip()

    if "Result" in fieldnames:
        result_text = str(row.get("Result", "")).lower()
        if tool_name == "Phaserr":
            return "success" in result_text
        if tool_name in {"Spacer", "Golem", "Golem-DAR", "Z3"}:
            return "sat" in result_text and "unsat" not in result_text
        return "sat" in result_text and "unsat" not in result_text

    if tool_name == "Phaserr":
        return True

    return False


def count_matching_rows(path: Path, max_time: float) -> dict[str, object]:
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = set(reader.fieldnames or [])
        required_columns = {"Time_Seconds", "Tool"}
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
                time_seconds = float(str(row.get("Time_Seconds", "")).strip())
            except ValueError:
                continue

            if time_seconds >= max_time or not is_satisfiable(row, fieldnames):
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
        description="Count satisfiable rows whose runtime is below a threshold"
    )
    parser.add_argument(
        "inputs",
        nargs="*",
        help="CSV files to analyze. Defaults to b04_phaserr.csv.",
    )
    parser.add_argument(
        "--max-time",
        type=float,
        default=20.0,
        help="Exclusive runtime threshold in seconds (default: 20)",
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
        stats = count_matching_rows(path, args.max_time)
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
            f"Time_Seconds < {args.max_time:g}; {len(stats['filenames'])} distinct benchmark files"
            f"{tool_summary}"
        )

    print(f"Total satisfiable rows with Time_Seconds < {args.max_time:g}: {total_rows}")
    print(
        "Total distinct benchmark files with satisfiable rows under the time threshold: "
        f"{len(total_filenames)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())