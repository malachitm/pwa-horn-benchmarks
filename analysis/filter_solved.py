#!/usr/bin/env python3
"""Filter a CSV of benchmark results to only the solved rows.

Usage:
  python3 filter_solved.py --input input.csv --output solved.csv

If --output is omitted, the script writes to `<input>_solved.csv`.
"""
from pathlib import Path
import argparse
import pandas as pd
import sys


def is_success(row):
    try:
        res = str(row['Result']).lower()
    except Exception:
        return False
    tool = str(row.get('Tool', ''))
    if tool == 'Phaserr':
        return 'success' in res
    elif tool in ['Spacer', 'Golem']:
        return 'sat' in res and 'unsat' not in res
    return False


def filter_file(input_path: Path, output_path: Path) -> int:
    df = pd.read_csv(input_path)
    # Apply the same logic as in make_data.py
    solved_mask = df.apply(is_success, axis=1)
    solved_df = df[solved_mask].copy()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    solved_df.to_csv(output_path, index=False)
    return len(solved_df)


def main(argv=None):
    parser = argparse.ArgumentParser(description='Filter CSV to solved rows')
    parser.add_argument('--input', '-i', required=True, help='Input CSV file')
    parser.add_argument('--output', '-o', required=False, help='Output CSV file (optional)')
    args = parser.parse_args(argv)

    inp = Path(args.input)
    if not inp.exists():
        print(f"Input file does not exist: {inp}")
        return 2

    if args.output:
        out = Path(args.output)
    else:
        out = inp.with_name(inp.stem + '_solved.csv')

    count = filter_file(inp, out)
    print(f"Wrote {count} solved rows to: {out}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
