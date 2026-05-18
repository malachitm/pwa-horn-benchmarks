import pandas as pd
import json
import re
import argparse
import sys

def process_results(input_csv, output_csv):
    """
    Reads a benchmark results CSV, extracts the JSON data from the end of the 
    'Result' column, creates three new columns, and writes to a new CSV.
    """
    # Read the CSV file
    try:
        df = pd.read_csv(input_csv)
    except Exception as e:
        print(f"Error reading {input_csv}: {e}")
        sys.exit(1)

    if 'Result' not in df.columns:
        print(f"Error: 'Result' column not found in the input CSV.")
        sys.exit(1)

    polar_runtimes = []
    average_times = []
    iterations = []

    for index, row in df.iterrows():
        result_str = str(row['Result'])
        
        # Regex to find the JSON string at the end of the Result column
        # Looks for the outermost JSON dictionary that contains "polar_time"
        match = re.search(r'(\{"polar_time".*\})\s*$', result_str, re.DOTALL)
        
        if match:
            json_str = match.group(1)
            try:
                data = json.loads(json_str)
                polar_runtimes.append(data.get("polar_time"))
                synth_data = data.get("synth_time_seconds", {})
                average_times.append(synth_data.get("mean"))
                iterations.append(synth_data.get("samples"))
            except json.JSONDecodeError:
                polar_runtimes.append(None)
                average_times.append(None)
                iterations.append(None)
        else:
            polar_runtimes.append(None)
            average_times.append(None)
            iterations.append(None)

    # Insert the new columns at the position where 'Result' used to be
    col_idx = df.columns.get_loc('Result')
    df.insert(col_idx, "Polar Runtime", polar_runtimes)
    df.insert(col_idx + 1, "Average Time per Iteration", average_times)
    df.insert(col_idx + 2, "# Iterations", iterations)

    # Drop the old 'Result' column
    df.drop(columns=['Result'], inplace=True)

    # Write the cleaned data to the output CSV
    try:
        df.to_csv(output_csv, index=False)
        print(f"Successfully wrote cleaned data to {output_csv}")
    except Exception as e:
        print(f"Error writing to {output_csv}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean benchmark results CSV")
    parser.add_argument("-i", "--input", default="benchmark_results_20260512_012742.csv", help="Input CSV file")
    parser.add_argument("-o", "--output", default="benchmark_results_cleaned.csv", help="Output CSV file")
    
    args = parser.parse_args()
    process_results(args.input, args.output)
