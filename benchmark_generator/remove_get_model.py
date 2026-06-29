#!/usr/bin/env python3
"""Create copies of .smt2 files with the final "(get-model)" line removed.

Usage:
  python3 remove_get_model.py --src b04 --dst b04_nogetmodel

The script preserves directory structure under the destination directory.
"""
from pathlib import Path
import argparse
import sys


def process_file(src_path: Path, dst_path: Path) -> bool:
    text = src_path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)

    # Find last non-empty line
    idx = len(lines) - 1
    while idx >= 0 and lines[idx].strip() == "":
        idx -= 1

    removed = False
    if idx >= 0 and lines[idx].strip() == "(get-model)":
        new_lines = lines[:idx]
        removed = True
    else:
        new_lines = lines

    dst_path.parent.mkdir(parents=True, exist_ok=True)
    dst_path.write_text("".join(new_lines), encoding="utf-8")
    return removed


def main(argv=None):
    parser = argparse.ArgumentParser(description="Copy .smt2 files and remove final '(get-model)' line if present")
    parser.add_argument("--src", required=True, help="Source directory containing .smt2 files")
    parser.add_argument("--dst", required=False, help="Destination directory (sibling created if omitted)")
    parser.add_argument("--no-recursive", action="store_true", help="Do not recurse into subdirectories")
    args = parser.parse_args(argv)

    src_root = Path(args.src)
    if not src_root.exists() or not src_root.is_dir():
        print(f"Source directory does not exist: {src_root}")
        return 2

    if args.dst:
        dst_root = Path(args.dst)
    else:
        dst_root = src_root.parent / (src_root.name + "_nogetmodel")

    count = 0
    removed_count = 0

    glob = "**/*.smt2" if not args.no_recursive else "*.smt2"
    for src_path in src_root.glob(glob):
        if not src_path.is_file():
            continue
        rel = src_path.relative_to(src_root)
        dst_path = dst_root / rel
        did_remove = process_file(src_path, dst_path)
        count += 1
        if did_remove:
            removed_count += 1

    print(f"Processed {count} .smt2 files; removed final '(get-model)' from {removed_count} files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
