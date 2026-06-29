#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_INPUTS = [
    ROOT_DIR / "b04_results" / "b04_phaserr.csv",
    ROOT_DIR / "b04_results" / "b04_other_1.csv",
    ROOT_DIR / "b04_results" / "b04_other_2.csv",
    ROOT_DIR / "b04_results" / "b07_results.csv",
]
OUTPUT_PATH = ROOT_DIR / "analysis" / "phaserr_stat_correlation.csv"
PHASERR_DATASET_OUTPUT_PATH = ROOT_DIR / "analysis" / "phaserr_stat_correlation_by_dataset.csv"
PHASERR_DATASET_LATEX_OUTPUT_PATH = ROOT_DIR / "analysis" / "phaserr_stat_correlation_by_dataset.tex"
TARGET_COLUMN = "Time_Seconds"
ALLOWED_TOOLS = {"Phaserr", "Golem-DAR", "Spacer"}
RESULT_JSON_PATTERN = re.compile(r'(\{"polar_time".*\})\s*$')
PHASERR_DATASET_ORDER = ["b04", "b07"]
PHASERR_DATASET_LABELS = {"b04": "PC-Intv-A", "b07": "PC-Intv-B"}
PHASERR_TABLE_METRICS = ["# Iterations", "Polar Runtime"]

KNOWN_METRIC_ALIASES = {
    "Interval Width": ["Interval Width"],
    "Polar Runtime": ["Polar Runtime", "polar_time"],
    "Average Time per Iteration": [
        "Average Time per Iteration",
        "synth_time_seconds.mean",
        "mean",
    ],
    "# Iterations": ["# Iterations", "synth_time_seconds.samples", "samples"],
}


def normalize_tool_name(tool: object) -> str:
    tool_name = str(tool).strip()
    if tool_name == "Golem":
        return "Golem-DAR"
    if tool_name == "Z3":
        return "Spacer"
    return tool_name


def is_success(row: pd.Series) -> bool:
    tool_name = normalize_tool_name(row.get("Tool", ""))
    time_seconds = pd.to_numeric(pd.Series([row.get(TARGET_COLUMN)]), errors="coerce").iloc[0]

    if pd.isna(time_seconds) or float(time_seconds) > 300.0:
        return False

    result_value = row.get("Result")
    if pd.notna(result_value):
        result_text = str(result_value).lower()
        if tool_name == "Phaserr":
            return "success" in result_text
        if tool_name in {"Spacer", "Golem-DAR"}:
            return "sat" in result_text and "unsat" not in result_text

    return True


def flatten_numeric_json(data: object, prefix: str = "") -> dict[str, float]:
    flattened: dict[str, float] = {}
    if isinstance(data, dict):
        for key, value in data.items():
            next_prefix = f"{prefix}.{key}" if prefix else str(key)
            flattened.update(flatten_numeric_json(value, next_prefix))
    elif isinstance(data, (int, float)) and not isinstance(data, bool):
        flattened[prefix] = float(data)
    return flattened


def extract_result_metrics(frame: pd.DataFrame) -> pd.DataFrame:
    if "Result" not in frame.columns:
        return frame

    extracted_rows = []
    for result in frame["Result"].fillna(""):
        match = RESULT_JSON_PATTERN.search(str(result))
        if not match:
            extracted_rows.append({})
            continue

        try:
            extracted_rows.append(flatten_numeric_json(json.loads(match.group(1))))
        except json.JSONDecodeError:
            extracted_rows.append({})

    extracted_df = pd.DataFrame(extracted_rows)
    if extracted_df.empty:
        return frame

    extracted_df = extracted_df.add_prefix("Result.")
    combined = pd.concat([frame.reset_index(drop=True), extracted_df.reset_index(drop=True)], axis=1)

    alias_fill_sources = {
        "Polar Runtime": ["Result.polar_time"],
        "Average Time per Iteration": ["Result.synth_time_seconds.mean"],
        "# Iterations": ["Result.synth_time_seconds.samples"],
    }
    for canonical_name, candidate_columns in alias_fill_sources.items():
        if canonical_name not in combined.columns:
            combined[canonical_name] = pd.NA
        for candidate in candidate_columns:
            if candidate in combined.columns:
                combined[canonical_name] = combined[canonical_name].fillna(combined[candidate])

    return combined


def load_phaserr_rows(csv_path: Path) -> pd.DataFrame:
    frame = pd.read_csv(csv_path)
    if "Tool" in frame.columns:
        frame["Tool"] = frame["Tool"].apply(normalize_tool_name)
        frame = frame[frame["Tool"].isin(ALLOWED_TOOLS)].copy()
    else:
        frame = frame.copy()

    frame["Source_File"] = csv_path.name
    frame["Source_Path"] = str(csv_path.relative_to(ROOT_DIR))
    frame["Dataset"] = "b07" if "b07" in csv_path.name else "b04"
    frame = extract_result_metrics(frame)
    frame["Is_Success"] = frame.apply(is_success, axis=1)
    if "Param_1" in frame.columns and "Param_2" in frame.columns:
        param_1 = pd.to_numeric(frame["Param_1"], errors="coerce")
        param_2 = pd.to_numeric(frame["Param_2"], errors="coerce")
        frame["Interval Width"] = param_2 - param_1
    return frame


def get_candidate_metric_columns(frame: pd.DataFrame) -> list[str]:
    excluded_columns = {
        "Filename",
        "Tool",
        "Result",
        "Is_Success",
        "Source_File",
        "Source_Path",
        TARGET_COLUMN,
    }
    excluded_prefixes = ("Param_",)

    numeric_columns = []
    for column in frame.columns:
        if column in excluded_columns:
            continue
        if column.startswith(excluded_prefixes):
            continue

        series = pd.to_numeric(frame[column], errors="coerce")
        if series.notna().any():
            numeric_columns.append(column)

    return numeric_columns


def resolve_known_metrics(available_columns: list[str]) -> tuple[dict[str, str], list[str]]:
    resolved: dict[str, str] = {}
    missing: list[str] = []

    available_set = set(available_columns)
    for canonical_name, aliases in KNOWN_METRIC_ALIASES.items():
        match = next((alias for alias in aliases if alias in available_set), None)
        if match is None:
            missing.append(canonical_name)
        else:
            resolved[canonical_name] = match

    return resolved, missing


def summarize_metric(
    frame: pd.DataFrame, tool_name: str, metric_column: str, display_name: str
) -> dict[str, object]:
    metric_frame = frame
    if "Is_Success" in frame.columns:
        metric_frame = frame[frame["Is_Success"]].copy()

    working = metric_frame[[metric_column, TARGET_COLUMN]].copy()
    working[metric_column] = pd.to_numeric(working[metric_column], errors="coerce")
    working[TARGET_COLUMN] = pd.to_numeric(working[TARGET_COLUMN], errors="coerce")
    working = working.dropna(subset=[metric_column, TARGET_COLUMN])

    values = working[metric_column]
    correlation = values.corr(working[TARGET_COLUMN]) if len(working) >= 2 else pd.NA

    return {
        "Tool": tool_name,
        "Metric": display_name,
        "Source_Column": metric_column,
        "Count": int(len(working)),
        "Runtime_Correlation": correlation,
        "Min": values.min() if not values.empty else pd.NA,
        "Max": values.max() if not values.empty else pd.NA,
        "Variance": values.var(ddof=1) if len(values) >= 2 else pd.NA,
    }


def summarize_metric_table(frame: pd.DataFrame, metric_column: str, display_name: str) -> dict[str, object]:
    row: dict[str, object] = {"Metric": display_name}

    for dataset_name in PHASERR_DATASET_ORDER:
        dataset_frame = frame[frame["Dataset"] == dataset_name].copy()
        if display_name == "Interval Width" and "Is_Success" in dataset_frame.columns:
            dataset_frame = dataset_frame[dataset_frame["Is_Success"]].copy()

        working = dataset_frame[[metric_column, TARGET_COLUMN]].copy()
        working[metric_column] = pd.to_numeric(working[metric_column], errors="coerce")
        working[TARGET_COLUMN] = pd.to_numeric(working[TARGET_COLUMN], errors="coerce")
        working = working.dropna(subset=[metric_column, TARGET_COLUMN])

        values = working[metric_column]
        correlation = values.corr(working[TARGET_COLUMN]) if len(working) >= 2 else pd.NA

        prefix = f"{dataset_name}_"
        row[prefix + "Count"] = int(len(working))
        row[prefix + "Correlation"] = correlation
        row[prefix + "Min"] = values.min() if not values.empty else pd.NA
        row[prefix + "Max"] = values.max() if not values.empty else pd.NA
        row[prefix + "Variance"] = values.var(ddof=1) if len(values) >= 2 else pd.NA

    return row


def summarize_dataset_metric(frame: pd.DataFrame, metric_column: str, display_name: str) -> dict[str, object]:
    metric_frame = frame
    if "Is_Success" in frame.columns:
        metric_frame = frame[frame["Is_Success"]].copy()

    working = metric_frame[[metric_column, TARGET_COLUMN]].copy()
    working[metric_column] = pd.to_numeric(working[metric_column], errors="coerce")
    working[TARGET_COLUMN] = pd.to_numeric(working[TARGET_COLUMN], errors="coerce")
    working = working.dropna(subset=[metric_column, TARGET_COLUMN])

    values = working[metric_column]
    correlation = values.corr(working[TARGET_COLUMN]) if len(working) >= 2 else pd.NA

    return {
        "#": int(len(working)),
        "rho_t": correlation,
        "Min": values.min() if not values.empty else pd.NA,
        "Max": values.max() if not values.empty else pd.NA,
        "sigma^2": values.var(ddof=1) if len(values) >= 2 else pd.NA,
    }


def format_latex_number(value: object) -> str:
    if pd.isna(value):
        return "--"

    if isinstance(value, (int,)):
        return str(value)

    numeric_value = float(value)
    if numeric_value.is_integer():
        return str(int(numeric_value))
    if abs(numeric_value) >= 1000:
        return f"{numeric_value:.2f}"
    if abs(numeric_value) >= 1:
        return f"{numeric_value:.3f}"
    return f"{numeric_value:.4f}"


def build_phaserr_dataset_latex_table(report: pd.DataFrame) -> str:
    lines = [
        r"\begin{table}[t]",
        r"    \centering",
        r"    \caption{Phaserr Correlation Statistics By Dataset}",
        r"    \begin{tabular}{llccccc}",
        r"        \toprule",
        r"        \textbf{Category} & \textbf{Metric} & \textbf{\#} & $\rho_t$ & \textbf{Min} & \textbf{Max} & $\sigma^2$ \\",
        r"        \midrule",
    ]

    for _, row in report.iterrows():
        category = row["Category"] if pd.notna(row["Category"]) else ""
        metric = str(row["Metric"]).replace("#", r"\#")
        count = format_latex_number(row["#"])
        rho_t = format_latex_number(row["rho_t"])
        min_value = format_latex_number(row["Min"])
        max_value = format_latex_number(row["Max"])
        sigma_sq = format_latex_number(row["sigma^2"])
        lines.append(
            f"        {category} & {metric} & {count} & {rho_t} & {min_value} & {max_value} & {sigma_sq} \\\\")

    lines.extend(
        [
            r"        \bottomrule",
            r"    \end{tabular}",
            r"    \label{tab:phaserr-correlation-by-dataset}",
            r"\end{table}",
        ]
    )
    return "\n".join(lines)


def build_report(input_paths: list[Path]) -> tuple[pd.DataFrame, dict[str, list[str]], int]:
    frames = [load_phaserr_rows(path) for path in input_paths]
    combined = pd.concat(frames, ignore_index=True)
    combined[TARGET_COLUMN] = pd.to_numeric(combined[TARGET_COLUMN], errors="coerce")

    report_rows = []
    missing_metrics_by_tool: dict[str, list[str]] = {}

    for tool_name in sorted(ALLOWED_TOOLS):
        tool_frame = combined[combined["Tool"] == tool_name].copy()
        candidate_columns = get_candidate_metric_columns(tool_frame)
        resolved_known_metrics, missing_metrics = resolve_known_metrics(candidate_columns)
        missing_metrics_by_tool[tool_name] = missing_metrics

        seen_columns = set()
        for display_name, column_name in resolved_known_metrics.items():
            report_rows.append(summarize_metric(tool_frame, tool_name, column_name, display_name))
            seen_columns.add(column_name)

        for column_name in candidate_columns:
            if column_name in seen_columns:
                continue
            report_rows.append(summarize_metric(tool_frame, tool_name, column_name, column_name))

    report = pd.DataFrame(report_rows)
    if not report.empty:
        report = report.sort_values(["Tool", "Metric"]).reset_index(drop=True)

    return report, missing_metrics_by_tool, len(combined)


def build_phaserr_dataset_report(input_paths: list[Path]) -> tuple[pd.DataFrame, list[str], int]:
    frames = [load_phaserr_rows(path) for path in input_paths]
    combined = pd.concat(frames, ignore_index=True)
    combined = combined[combined["Tool"] == "Phaserr"].copy()
    combined[TARGET_COLUMN] = pd.to_numeric(combined[TARGET_COLUMN], errors="coerce")

    candidate_columns = get_candidate_metric_columns(combined)
    resolved_known_metrics, missing_metrics = resolve_known_metrics(candidate_columns)

    report_rows = []
    filtered_missing_metrics = [
        metric_name for metric_name in missing_metrics if metric_name in PHASERR_TABLE_METRICS
    ]

    for dataset_name in PHASERR_DATASET_ORDER:
        dataset_frame = combined[combined["Dataset"] == dataset_name].copy()
        dataset_label = PHASERR_DATASET_LABELS.get(dataset_name, dataset_name)
        for metric_index, display_name in enumerate(PHASERR_TABLE_METRICS):
            column_name = resolved_known_metrics.get(display_name)
            row = {
                "Category": dataset_label if metric_index == 0 else "",
                "Metric": display_name,
            }
            if column_name is None:
                row.update({"#": pd.NA, "rho_t": pd.NA, "Min": pd.NA, "Max": pd.NA, "sigma^2": pd.NA})
            else:
                row.update(summarize_dataset_metric(dataset_frame, column_name, display_name))
            report_rows.append(row)

    report = pd.DataFrame(report_rows)
    if not report.empty:
        report = report[["Category", "Metric", "#", "rho_t", "Min", "Max", "sigma^2"]]

    return report, filtered_missing_metrics, len(combined)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarize how Phaserr benchmark statistics correlate with runtime."
    )
    parser.add_argument(
        "--input",
        nargs="+",
        type=Path,
        default=DEFAULT_INPUTS,
        help="CSV files to analyze. Defaults to the combined b04/b07 cactus dataset inputs.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT_PATH,
        help="Where to write the summary CSV.",
    )
    parser.add_argument(
        "--phaserr-dataset-output",
        type=Path,
        default=PHASERR_DATASET_OUTPUT_PATH,
        help="Where to write the b04/b07-separated Phaserr summary CSV.",
    )
    parser.add_argument(
        "--phaserr-dataset-latex-output",
        type=Path,
        default=PHASERR_DATASET_LATEX_OUTPUT_PATH,
        help="Where to write the b04/b07-separated Phaserr LaTeX table.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_paths = [path if path.is_absolute() else (ROOT_DIR / path).resolve() for path in args.input]

    missing_paths = [path for path in input_paths if not path.exists()]
    if missing_paths:
        for path in missing_paths:
            print(f"Missing input file: {path}")
        return 2

    report, missing_metrics_by_tool, row_count = build_report(input_paths)
    output_path = args.output if args.output.is_absolute() else (ROOT_DIR / args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    report.to_csv(output_path, index=False)

    phaserr_report, phaserr_missing_metrics, phaserr_row_count = build_phaserr_dataset_report(input_paths)
    phaserr_output_path = (
        args.phaserr_dataset_output
        if args.phaserr_dataset_output.is_absolute()
        else (ROOT_DIR / args.phaserr_dataset_output).resolve()
    )
    phaserr_output_path.parent.mkdir(parents=True, exist_ok=True)
    phaserr_report.to_csv(phaserr_output_path, index=False)

    phaserr_latex_output_path = (
        args.phaserr_dataset_latex_output
        if args.phaserr_dataset_latex_output.is_absolute()
        else (ROOT_DIR / args.phaserr_dataset_latex_output).resolve()
    )
    phaserr_latex_output_path.parent.mkdir(parents=True, exist_ok=True)
    phaserr_latex_output_path.write_text(build_phaserr_dataset_latex_table(phaserr_report) + "\n")

    print("Analyzed rows across selected tools:", row_count)
    print("Input files:")
    for path in input_paths:
        print(f"  - {path.relative_to(ROOT_DIR)}")

    if report.empty:
        print("\nNo numeric benchmark-stat columns were available for correlation analysis.")
    else:
        print("\nMetric summary:")
        print(report.to_string(index=False))

    missing_tools = {tool: metrics for tool, metrics in missing_metrics_by_tool.items() if metrics}
    if missing_tools:
        print("\nRequested metrics not found in these inputs:")
        for tool_name, metric_names in missing_tools.items():
            print(f"  - {tool_name}: {', '.join(metric_names)}")

    print(f"\nWrote summary to {output_path}")
    print(f"Wrote Phaserr-by-dataset summary to {phaserr_output_path}")
    print(f"Wrote Phaserr-by-dataset LaTeX table to {phaserr_latex_output_path}")

    if not phaserr_report.empty:
        print("\nPhaserr by dataset:")
        print(phaserr_report.to_string(index=False))

    if phaserr_missing_metrics:
        print("\nPhaserr metrics not found in these inputs:")
        for metric_name in phaserr_missing_metrics:
            print(f"  - {metric_name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())