#!/usr/bin/env python3
"""Compare iteration runtime across Param_1/Param_2 within matched Param_3+ groups.

The script groups rows by Tool and Param_3 through Param_8, then compares the
"Average Time per Iteration" values across the Param_1/Param_2 variants inside
each matched group.

Outputs:
  1. A per-group CSV with one row per matched Param_3+ group.
  2. A per-variant summary CSV.
  3. A pairwise comparison CSV across Param_1/Param_2 variants.

Usage:
  python3 compare_iteration_runtime_by_param12.py
  python3 compare_iteration_runtime_by_param12.py --input path/to/file.csv
"""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from itertools import combinations
from pathlib import Path
from statistics import mean, median


ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT_DIR / "b04_results" / "b04_phaserr.csv"
GROUP_COLUMNS = ["Param_3", "Param_4", "Param_5", "Param_6", "Param_7", "Param_8"]
VARIANT_COLUMNS = ["Param_1", "Param_2"]
METRIC_COLUMN = "Average Time per Iteration"
FLOAT_TOLERANCE = 1e-12


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT_DIR))
    except ValueError:
        return str(path)


def parse_float(value: str, column_name: str, row_number: int) -> float:
    try:
        return float(str(value).strip())
    except ValueError as exc:
        raise ValueError(f"Row {row_number}: invalid {column_name} value {value!r}") from exc


def format_number(value: float) -> str:
    return f"{value:g}".replace("-", "neg").replace(".", "p")


def variant_label(variant: tuple[float, float]) -> str:
    param_1, param_2 = variant
    return f"P1_{format_number(param_1)}__P2_{format_number(param_2)}"


def variant_display(variant: tuple[float, float]) -> str:
    param_1, param_2 = variant
    return f"(Param_1={param_1:g}, Param_2={param_2:g})"


def default_output_path(input_path: Path, suffix: str) -> Path:
    return input_path.with_name(input_path.stem + suffix)


def percent_change(value: float, baseline: float) -> float:
    if abs(baseline) <= FLOAT_TOLERANCE:
        return 0.0
    return ((value - baseline) / baseline) * 100.0


def summarize_variant_rows(
    per_variant_rows: dict[tuple[float, float], list[dict[str, object]]]
) -> tuple[
    dict[tuple[float, float], float],
    dict[tuple[float, float], str],
    dict[tuple[float, float], int],
]:
    metric_by_variant: dict[tuple[float, float], float] = {}
    filenames_by_variant: dict[tuple[float, float], str] = {}
    count_by_variant: dict[tuple[float, float], int] = {}

    for variant, rows in per_variant_rows.items():
        metrics = [float(entry["metric"]) for entry in rows]
        metric_by_variant[variant] = mean(metrics)
        filenames_by_variant[variant] = ";".join(
            entry["filename"] for entry in rows if str(entry["filename"]).strip()
        )
        count_by_variant[variant] = len(rows)

    return metric_by_variant, filenames_by_variant, count_by_variant


def build_group_detail_row(
    group_index: int,
    group_key: tuple[object, ...],
    variants: list[tuple[float, float]],
    metric_by_variant: dict[tuple[float, float], float],
    filenames_by_variant: dict[tuple[float, float], str],
    count_by_variant: dict[tuple[float, float], int],
    group_mean: float,
    fastest_variant: tuple[float, float],
    fastest_value: float,
    slowest_variant: tuple[float, float],
    slowest_value: float,
) -> dict[str, object]:
    tool_name = str(group_key[0])
    param_values = group_key[1:]
    detail_row: dict[str, object] = {
        "Group_ID": group_index,
        "Tool": tool_name,
        "Matched_Variant_Count": len(metric_by_variant),
        "Group_Mean_Avg_Iteration_Runtime": group_mean,
        "Fastest_Param_1": fastest_variant[0],
        "Fastest_Param_2": fastest_variant[1],
        "Fastest_Avg_Iteration_Runtime": fastest_value,
        "Slowest_Param_1": slowest_variant[0],
        "Slowest_Param_2": slowest_variant[1],
        "Slowest_Avg_Iteration_Runtime": slowest_value,
        "Runtime_Range": slowest_value - fastest_value,
        "Slowdown_Percentage_Slowest_vs_Fastest": percent_change(slowest_value, fastest_value),
    }

    for column_name, column_value in zip(GROUP_COLUMNS, param_values):
        detail_row[column_name] = column_value

    for variant in variants:
        label = variant_label(variant)
        metric_value = metric_by_variant.get(variant)
        detail_row[f"Filename__{label}"] = filenames_by_variant.get(variant, "")
        detail_row[f"RowCount__{label}"] = count_by_variant.get(variant, 0)
        detail_row[f"AvgIter__{label}"] = metric_value if metric_value is not None else ""
        detail_row[f"DeltaFromGroupMean__{label}"] = (
            metric_value - group_mean if metric_value is not None else ""
        )
        detail_row[f"DeltaFromFastest__{label}"] = (
            metric_value - fastest_value if metric_value is not None else ""
        )
        detail_row[f"PctDeltaFromFastest__{label}"] = (
            percent_change(metric_value, fastest_value) if metric_value is not None else ""
        )
        detail_row[f"PctDeltaFromGroupMean__{label}"] = (
            percent_change(metric_value, group_mean) if metric_value is not None else ""
        )

    return detail_row


def update_variant_aggregates(
    variants: list[tuple[float, float]],
    metric_by_variant: dict[tuple[float, float], float],
    group_mean: float,
    fastest_variant: tuple[float, float],
    fastest_value: float,
    variant_values: dict[tuple[float, float], list[float]],
    variant_delta_from_group_mean: dict[tuple[float, float], list[float]],
    variant_delta_from_fastest: dict[tuple[float, float], list[float]],
    variant_pct_delta_from_group_mean: dict[tuple[float, float], list[float]],
    variant_pct_delta_from_fastest: dict[tuple[float, float], list[float]],
    variant_fastest_count: dict[tuple[float, float], int],
) -> None:
    for variant in variants:
        metric_value = metric_by_variant.get(variant)
        if metric_value is None:
            continue

        variant_values[variant].append(metric_value)
        variant_delta_from_group_mean[variant].append(metric_value - group_mean)
        variant_delta_from_fastest[variant].append(metric_value - fastest_value)
        variant_pct_delta_from_group_mean[variant].append(percent_change(metric_value, group_mean))
        variant_pct_delta_from_fastest[variant].append(percent_change(metric_value, fastest_value))
        if variant == fastest_variant:
            variant_fastest_count[variant] += 1


def update_pairwise_differences(
    variants: list[tuple[float, float]],
    metric_by_variant: dict[tuple[float, float], float],
    pairwise_differences: dict[
        tuple[tuple[float, float], tuple[float, float]], list[tuple[float, float]]
    ],
) -> None:
    for variant_a, variant_b in combinations(variants, 2):
        if variant_a not in metric_by_variant or variant_b not in metric_by_variant:
            continue
        metric_a = metric_by_variant[variant_a]
        metric_b = metric_by_variant[variant_b]
        diff = metric_b - metric_a
        pct_diff = percent_change(metric_b, metric_a)
        pairwise_differences[(variant_a, variant_b)].append((diff, pct_diff))


def build_variant_summary_rows(
    variants: list[tuple[float, float]],
    detail_rows: list[dict[str, object]],
    variant_values: dict[tuple[float, float], list[float]],
    variant_delta_from_group_mean: dict[tuple[float, float], list[float]],
    variant_delta_from_fastest: dict[tuple[float, float], list[float]],
    variant_pct_delta_from_group_mean: dict[tuple[float, float], list[float]],
    variant_pct_delta_from_fastest: dict[tuple[float, float], list[float]],
    variant_fastest_count: dict[tuple[float, float], int],
) -> list[dict[str, object]]:
    variant_summary_rows: list[dict[str, object]] = []
    total_groups = len(detail_rows)

    for variant in variants:
        values = variant_values.get(variant, [])
        if not values:
            continue

        delta_group = variant_delta_from_group_mean[variant]
        delta_fastest = variant_delta_from_fastest[variant]
        pct_delta_group = variant_pct_delta_from_group_mean[variant]
        pct_delta_fastest = variant_pct_delta_from_fastest[variant]
        variant_summary_rows.append(
            {
                "Param_1": variant[0],
                "Param_2": variant[1],
                "Variant": variant_display(variant),
                "Groups_Present": len(values),
                "Mean_Avg_Iteration_Runtime": mean(values),
                "Median_Avg_Iteration_Runtime": median(values),
                "Mean_Delta_From_Group_Mean": mean(delta_group),
                "Median_Delta_From_Group_Mean": median(delta_group),
                "Mean_Delta_From_Fastest": mean(delta_fastest),
                "Median_Delta_From_Fastest": median(delta_fastest),
                "Mean_Pct_Delta_From_Group_Mean": mean(pct_delta_group),
                "Median_Pct_Delta_From_Group_Mean": median(pct_delta_group),
                "Mean_Pct_Delta_From_Fastest": mean(pct_delta_fastest),
                "Median_Pct_Delta_From_Fastest": median(pct_delta_fastest),
                "Fastest_In_Group_Count": variant_fastest_count.get(variant, 0),
                "Fastest_In_Group_Percentage": (
                    variant_fastest_count.get(variant, 0) / total_groups if total_groups else 0.0
                ),
            }
        )

    return variant_summary_rows


def count_pairwise_outcomes(diffs: list[float]) -> tuple[int, int, int]:
    variant_b_faster = sum(1 for diff in diffs if diff < -FLOAT_TOLERANCE)
    variant_a_faster = sum(1 for diff in diffs if diff > FLOAT_TOLERANCE)
    tie_count = len(diffs) - variant_b_faster - variant_a_faster
    return variant_b_faster, variant_a_faster, tie_count


def build_pairwise_summary_rows(
    pairwise_differences: dict[
        tuple[tuple[float, float], tuple[float, float]], list[tuple[float, float]]
    ]
) -> list[dict[str, object]]:
    pairwise_summary_rows: list[dict[str, object]] = []

    for (variant_a, variant_b), comparisons in sorted(
        pairwise_differences.items(), key=lambda item: (item[0][0], item[0][1])
    ):
        diffs = [diff for diff, _ in comparisons]
        pct_diffs = [pct_diff for _, pct_diff in comparisons]
        variant_b_faster, variant_a_faster, tie_count = count_pairwise_outcomes(diffs)
        pairwise_summary_rows.append(
            {
                "Variant_A_Param_1": variant_a[0],
                "Variant_A_Param_2": variant_a[1],
                "Variant_B_Param_1": variant_b[0],
                "Variant_B_Param_2": variant_b[1],
                "Variant_A": variant_display(variant_a),
                "Variant_B": variant_display(variant_b),
                "Compared_Groups": len(diffs),
                "Mean_Diff_B_minus_A": mean(diffs),
                "Median_Diff_B_minus_A": median(diffs),
                "Min_Diff_B_minus_A": min(diffs),
                "Max_Diff_B_minus_A": max(diffs),
                "Mean_Pct_Diff_B_vs_A": mean(pct_diffs),
                "Median_Pct_Diff_B_vs_A": median(pct_diffs),
                "Min_Pct_Diff_B_vs_A": min(pct_diffs),
                "Max_Pct_Diff_B_vs_A": max(pct_diffs),
                "Variant_B_Faster_Count": variant_b_faster,
                "Variant_A_Faster_Count": variant_a_faster,
                "Tie_Count": tie_count,
            }
        )

    return pairwise_summary_rows


def summarize_single_group(
    group_index: int,
    group_key: tuple[object, ...],
    variants: list[tuple[float, float]],
    per_variant_rows: dict[tuple[float, float], list[dict[str, object]]],
) -> tuple[dict[str, object], dict[tuple[float, float], float], float, tuple[float, float], float]:
    metric_by_variant, filenames_by_variant, count_by_variant = summarize_variant_rows(per_variant_rows)
    group_mean = mean(metric_by_variant.values())
    fastest_variant, fastest_value = min(metric_by_variant.items(), key=lambda item: item[1])
    slowest_variant, slowest_value = max(metric_by_variant.items(), key=lambda item: item[1])
    detail_row = build_group_detail_row(
        group_index,
        group_key,
        variants,
        metric_by_variant,
        filenames_by_variant,
        count_by_variant,
        group_mean,
        fastest_variant,
        fastest_value,
        slowest_variant,
        slowest_value,
    )
    return detail_row, metric_by_variant, group_mean, fastest_variant, fastest_value


def load_grouped_rows(input_path: Path) -> tuple[dict[tuple[object, ...], dict[tuple[float, float], list[dict[str, object]]]], list[tuple[float, float]]]:
    grouped: dict[tuple[object, ...], dict[tuple[float, float], list[dict[str, object]]]] = defaultdict(
        lambda: defaultdict(list)
    )
    variants: set[tuple[float, float]] = set()

    with input_path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = set(reader.fieldnames or [])
        required_columns = set(GROUP_COLUMNS + VARIANT_COLUMNS + [METRIC_COLUMN])
        missing_columns = sorted(required_columns - fieldnames)
        if missing_columns:
            raise ValueError(
                f"{display_path(input_path)} is missing required columns: {', '.join(missing_columns)}"
            )

        for row_number, row in enumerate(reader, start=2):
            tool_name = str(row.get("Tool", "")).strip()
            group_values = tuple(parse_float(row[column], column, row_number) for column in GROUP_COLUMNS)
            variant = tuple(parse_float(row[column], column, row_number) for column in VARIANT_COLUMNS)
            metric_value = parse_float(row[METRIC_COLUMN], METRIC_COLUMN, row_number)

            group_key = (tool_name, *group_values)
            grouped[group_key][variant].append(
                {
                    "filename": str(row.get("Filename", "")).strip(),
                    "metric": metric_value,
                    "time_seconds": row.get("Time_Seconds", ""),
                }
            )
            variants.add(variant)

    return grouped, sorted(variants)


def summarize_groups(
    grouped: dict[tuple[object, ...], dict[tuple[float, float], list[dict[str, object]]]],
    variants: list[tuple[float, float]],
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    detail_rows: list[dict[str, object]] = []
    variant_values: dict[tuple[float, float], list[float]] = defaultdict(list)
    variant_delta_from_group_mean: dict[tuple[float, float], list[float]] = defaultdict(list)
    variant_delta_from_fastest: dict[tuple[float, float], list[float]] = defaultdict(list)
    variant_pct_delta_from_group_mean: dict[tuple[float, float], list[float]] = defaultdict(list)
    variant_pct_delta_from_fastest: dict[tuple[float, float], list[float]] = defaultdict(list)
    variant_fastest_count: dict[tuple[float, float], int] = defaultdict(int)
    pairwise_differences: dict[
        tuple[tuple[float, float], tuple[float, float]], list[tuple[float, float]]
    ] = defaultdict(list)

    for group_index, group_key in enumerate(sorted(grouped.keys()), start=1):
        detail_row, metric_by_variant, group_mean, fastest_variant, fastest_value = summarize_single_group(
            group_index,
            group_key,
            variants,
            grouped[group_key],
        )
        detail_rows.append(detail_row)

        update_variant_aggregates(
            variants,
            metric_by_variant,
            group_mean,
            fastest_variant,
            fastest_value,
            variant_values,
            variant_delta_from_group_mean,
            variant_delta_from_fastest,
            variant_pct_delta_from_group_mean,
            variant_pct_delta_from_fastest,
            variant_fastest_count,
        )
        update_pairwise_differences(variants, metric_by_variant, pairwise_differences)

    variant_summary_rows = build_variant_summary_rows(
        variants,
        detail_rows,
        variant_values,
        variant_delta_from_group_mean,
        variant_delta_from_fastest,
        variant_pct_delta_from_group_mean,
        variant_pct_delta_from_fastest,
        variant_fastest_count,
    )
    pairwise_summary_rows = build_pairwise_summary_rows(pairwise_differences)

    return detail_rows, variant_summary_rows, pairwise_summary_rows


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames: list[str] = []
    for row in rows:
        for key in row.keys():
            if key not in fieldnames:
                fieldnames.append(key)

    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare Average Time per Iteration across Param_1/Param_2 within matched Param_3+ groups"
    )
    parser.add_argument(
        "--input",
        default=str(DEFAULT_INPUT),
        help="Input CSV file (default: b04_phaserr.csv)",
    )
    parser.add_argument(
        "--detail-output",
        help="Optional output CSV for the per-group matched detail report",
    )
    parser.add_argument(
        "--variant-summary-output",
        help="Optional output CSV for the per-variant summary report",
    )
    parser.add_argument(
        "--pairwise-output",
        help="Optional output CSV for the pairwise variant comparison report",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Input file does not exist: {input_path}")
        return 2

    detail_output = Path(args.detail_output) if args.detail_output else default_output_path(
        input_path, "_param12_iteration_groups.csv"
    )
    variant_summary_output = (
        Path(args.variant_summary_output)
        if args.variant_summary_output
        else default_output_path(input_path, "_param12_iteration_variant_summary.csv")
    )
    pairwise_output = Path(args.pairwise_output) if args.pairwise_output else default_output_path(
        input_path, "_param12_iteration_pairwise.csv"
    )

    grouped, variants = load_grouped_rows(input_path)
    detail_rows, variant_summary_rows, pairwise_summary_rows = summarize_groups(grouped, variants)

    write_csv(detail_output, detail_rows)
    write_csv(variant_summary_output, variant_summary_rows)
    write_csv(pairwise_output, pairwise_summary_rows)

    print(f"Input: {display_path(input_path)}")
    print(f"Matched Param_3+ groups: {len(detail_rows)}")
    print(f"Param_1/Param_2 variants discovered: {', '.join(variant_display(v) for v in variants)}")
    print("Per-variant average iteration runtime summary:")
    for row in variant_summary_rows:
        print(
            "  "
            f"{row['Variant']}: mean={row['Mean_Avg_Iteration_Runtime']:.6f}, "
            f"mean pct delta from group mean={row['Mean_Pct_Delta_From_Group_Mean']:.2f}%, "
            f"fastest in {row['Fastest_In_Group_Count']} groups"
        )
    print("Pairwise mean percentage differences (Variant_B vs Variant_A baseline):")
    for row in pairwise_summary_rows:
        print(
            "  "
            f"{row['Variant_B']} - {row['Variant_A']}: "
            f"mean pct diff={row['Mean_Pct_Diff_B_vs_A']:.2f}% across {row['Compared_Groups']} groups"
        )
    print(f"Wrote per-group report to: {detail_output}")
    print(f"Wrote per-variant summary to: {variant_summary_output}")
    print(f"Wrote pairwise summary to: {pairwise_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())