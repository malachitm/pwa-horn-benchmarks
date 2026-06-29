#!/usr/bin/env python3
"""Keep only Phaserr rows whose runtime is below a threshold.

Usage:
  python3 filter_phaserr_under_time.py file1.csv file2.csv --max-time 300

If no input files are provided, the script defaults to the two CSV files from
the current Phaserr comparison workflow.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_INPUTS = [
    ROOT_DIR / "b04_results" / "b04_phaserr.csv",
    ROOT_DIR / "b04_results" / "b07_results.csv",
]


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT_DIR))
    except ValueError:
        return str(path)


def default_output_path(input_path: Path, max_time: float) -> Path:
    suffix = f"_phaserr_under_{max_time:g}s"
    sanitized_suffix = suffix.replace(".", "p")
    return input_path.with_name(input_path.stem + sanitized_suffix + ".csv")


def row_matches(row: dict[str, str], max_time: float) -> bool:
    tool_name = str(row.get("Tool", "")).strip()
    if tool_name != "Phaserr":
        return False

    try:
        time_seconds = float(str(row.get("Time_Seconds", "")).strip())
    except ValueError:
        return False

    return time_seconds < max_time


def filter_file(input_path: Path, output_path: Path, max_time: float) -> int:
    with input_path.open(newline="") as input_handle:
        reader = csv.DictReader(input_handle)
        fieldnames = reader.fieldnames or []
        required_columns = {"Tool", "Time_Seconds"}
        missing_columns = sorted(required_columns - set(fieldnames))
        if missing_columns:
            raise ValueError(
                f"{display_path(input_path)} is missing required columns: {', '.join(missing_columns)}"
            )

        filtered_rows = [row for row in reader if row_matches(row, max_time)]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="") as output_handle:
        writer = csv.DictWriter(output_handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(filtered_rows)

    return len(filtered_rows)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Filter CSV files down to Phaserr rows with runtime below a threshold"
    )
    parser.add_argument(
        "inputs",
        nargs="*",
        help="CSV files to filter. Defaults to b04_phaserr.csv and b07_results.csv.",
    )
    parser.add_argument(
        "--max-time",
        type=float,
        default=300.0,
        help="Exclusive runtime threshold in seconds (default: 300)",
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

    for input_path in input_paths:
        output_path = default_output_path(input_path, args.max_time)
        count = filter_file(input_path, output_path, args.max_time)
        print(
            f"Wrote {count} rows from {display_path(input_path)} to {display_path(output_path)}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())