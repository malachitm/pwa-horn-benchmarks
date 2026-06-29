#!/usr/bin/env python3

from pathlib import Path
import re

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from pygments.styles import get_style_by_name


TIMEOUT_SECONDS = 300.0
ROOT_DIR = Path(__file__).resolve().parents[1]

SPACER_NAMES = {"Z3", "Spacer"}
GOLEM_DAR_NAMES = {"Golem", "Golem-DAR"}
ALLOWED_TOOLS = {"Phaserr", "Spacer", "Golem-DAR"}
TOOL_ORDER = ["Phaserr", "Spacer", "Golem-DAR"]
TOOL_PALETTE = {
    "Phaserr": "#000080",
    "Spacer": "#696969",
    "Golem-DAR": "#800000",
}


def get_staroffice_colors():
    style = get_style_by_name("staroffice")
    colors = []

    for style_def in style.styles.values():
        match = re.search(r"#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})", style_def)
        if not match:
            continue

        color = match.group(0)
        if len(color) == 4:
            color = "#" + "".join(component * 2 for component in color[1:])

        if color.lower() in {"#000000", "#ffffff", "#f8f8f8", "#f5f5f5"}:
            continue

        if color not in colors:
            colors.append(color)

    return style, colors


def configure_plot_style():
    style, staroffice_colors = get_staroffice_colors()
    plt.rcParams.update(
        {
            "text.usetex": False,
            "font.family": "serif",
            "font.serif": ["Times New Roman"],
            "font.size": 12,
            "axes.titlesize": 14,
            "axes.labelsize": 12,
            "legend.fontsize": 10,
            "figure.figsize": (8, 5),
            "text.color": "black",
            "axes.labelcolor": "black",
            "xtick.color": "black",
            "ytick.color": "black",
            "axes.edgecolor": "black",
            "legend.labelcolor": "black",
            "axes.prop_cycle": plt.cycler("color", staroffice_colors),
            "axes.facecolor": style.background_color or "white",
            "grid.color": "#dddddd",
        }
    )
    return staroffice_colors


def normalize_tool_name(tool):
    tool_name = str(tool)
    if tool_name in SPACER_NAMES:
        return "Spacer"
    if tool_name in GOLEM_DAR_NAMES:
        return "Golem-DAR"
    return tool_name


def get_time_seconds(row):
    try:
        return float(row.get("Time_Seconds", float("nan")))
    except Exception:
        return float("nan")


def has_result_column(row):
    result = row.get("Result")
    return pd.notna(result)


def is_solved(row):
    tool = normalize_tool_name(row.get("Tool", ""))
    time_seconds = get_time_seconds(row)

    if has_result_column(row):
        result_text = str(row.get("Result", "")).lower()
        if tool == "Phaserr":
            return "success" in result_text
        if tool in {"Spacer", "Golem-DAR"}:
            return "sat" in result_text and "unsat" not in result_text

    return pd.notna(time_seconds) and time_seconds <= TIMEOUT_SECONDS


def discover_csv_files(dataset_name, preferred_dir, preferred_patterns, fallback_patterns=None):
    files = []
    for pattern in preferred_patterns:
        files.extend(sorted(preferred_dir.glob(pattern)))

    if files:
        return files

    fallback_patterns = fallback_patterns or []
    for pattern in fallback_patterns:
        files.extend(sorted(ROOT_DIR.glob(pattern)))

    if files:
        print(
            f"No raw {dataset_name} CSV files found in {preferred_dir}. "
            f"Using fallback matches: {', '.join(str(path.relative_to(ROOT_DIR)) for path in files)}"
        )

    return files


def load_dataset(dataset_name, csv_files):
    frames = []
    for csv_file in csv_files:
        frame = pd.read_csv(csv_file)
        frame["Dataset"] = dataset_name
        frame["Source_File"] = csv_file.name
        frame["Instance_ID"] = dataset_name + "::" + frame["Filename"].astype(str)
        frames.append(frame)

    if not frames:
        raise ValueError(f"No CSV files were loaded for dataset {dataset_name}.")

    dataset_df = pd.concat(frames, ignore_index=True)
    dataset_df["Tool"] = dataset_df["Tool"].apply(normalize_tool_name)
    dataset_df = dataset_df[dataset_df["Tool"].isin(ALLOWED_TOOLS)].copy()
    dataset_df["is_solved"] = dataset_df.apply(is_solved, axis=1)
    dataset_df["Time_Seconds"] = pd.to_numeric(dataset_df["Time_Seconds"], errors="coerce")
    return dataset_df


def build_cactus_data(df):
    solved_df = df[df["is_solved"]].copy()
    solved_df = solved_df.dropna(subset=["Time_Seconds"])

    cactus_frames = []
    grouped = solved_df.groupby(["Tool"], sort=True)

    for tool_name, tool_df in grouped:
        ranked = tool_df.sort_values(by="Time_Seconds").copy()
        ranked["Solved_Count"] = range(1, len(ranked) + 1)
        cactus_frames.append(ranked)

    if not cactus_frames:
        raise ValueError("No solved rows were found for the requested datasets.")

    return pd.concat(cactus_frames, ignore_index=True)


def main():
    b04_dir = ROOT_DIR / "b04_results"
    b07_dir = ROOT_DIR / "b07_results"

    b04_files = discover_csv_files(
        dataset_name="b04",
        preferred_dir=b04_dir,
        preferred_patterns=["b04_phaserr.csv", "b04_other_*.csv"],
    )
    b07_files = discover_csv_files(
        dataset_name="b07",
        preferred_dir=b07_dir,
        preferred_patterns=["b07*.csv"],
        fallback_patterns=["**/b07*.csv"],
    )

    if not b04_files:
        raise FileNotFoundError(f"No b04 CSV files found under {b04_dir}.")
    if not b07_files:
        raise FileNotFoundError(
            f"No b07 CSV files found under {b07_dir} or anywhere below {ROOT_DIR}."
        )

    combined_df = pd.concat(
        [
            load_dataset("b04", b04_files),
            load_dataset("b07", b07_files),
        ],
        ignore_index=True,
    )
    plot_data = build_cactus_data(combined_df)

    configure_plot_style()

    plot_data["Tool"] = pd.Categorical(plot_data["Tool"], categories=TOOL_ORDER, ordered=True)
    dashes = {tool: (1, 0) for tool in TOOL_ORDER}

    _, ax = plt.subplots()
    sns.lineplot(
        data=plot_data,
        x="Solved_Count",
        y="Time_Seconds",
        hue="Tool",
        style="Tool",
        hue_order=TOOL_ORDER,
        style_order=TOOL_ORDER,
        palette=TOOL_PALETTE,
        markers=True,
        dashes=dashes,
        markevery=0.1,
        linewidth=1.8,
        ax=ax,
    )

    ax.set_yscale("log")
    ax.set_xlabel("Number of Benchmarks Solved")
    ax.set_ylabel("Time (s) [Log Scale]")
    #ax.set_title("Cactus Plot for Combined b04 and b07")
    ax.grid(True, which="both", ls="-", alpha=0.2)
    ax.legend(title="Tool", loc="lower right", frameon=True)

    output_path = ROOT_DIR / "analysis" / "cactus_b04_b07.pdf"
    plt.tight_layout()
    plt.savefig(output_path, format="pdf", bbox_inches="tight")

    print("Loaded b04 files:")
    for csv_file in b04_files:
        print(f"  - {csv_file.relative_to(ROOT_DIR)}")

    print("Loaded b07 files:")
    for csv_file in b07_files:
        print(f"  - {csv_file.relative_to(ROOT_DIR)}")

    summary = (
        plot_data.groupby(["Tool"])["Instance_ID"]
        .nunique()
        .reset_index(name="Solved")
        .sort_values(["Tool"])
    )
    print("\nSolved benchmark counts used in the plot:")
    print(summary.to_string(index=False))
    print(f"\nSaved cactus plot to {output_path}")


if __name__ == "__main__":
    main()