import os
import subprocess
import time
import csv
import glob
import argparse
import sys
from datetime import datetime

# ================= CONFIGURATION =================
# Define your tools here.
# Certificate path is injected per-run, so do NOT include it here.
TOOLS = {
    #"Phaserr":   ["../build/tools/deep/freqhorn", "--phaserr"]
    "Spacer": ["z3"],
    "Golem": ["golem", "--engine", "dar"]
    #"cvc5": ["cvc5", "--incremental"],
    #"MathSAT": ["mathsat"]
    #"GSpacer": ["gspacer"]
}

OUTPUT_CSV = "benchmark_results_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".csv"
TIMEOUT_SECONDS = 60
CERT_DIR = "./certificate"
# =================================================

def run_single_tool(tool_command_list, filepath, run_index=0):
    """Run the tool and return output and duration."""
    os.makedirs(CERT_DIR, exist_ok=True)
    #cert_path = os.path.join(CERT_DIR, f"c{run_index}.smt2")
    full_command = tool_command_list + [filepath]
    start_time = time.time()
    try:
        result = subprocess.run(
            full_command, 
            capture_output=True, 
            text=True, 
            timeout=TIMEOUT_SECONDS
        )
        output = result.stdout.strip()
        if result.stderr:
            output += f" [STDERR: {result.stderr.strip()}]"
        # Clean newlines for CSV safety
        output = output.replace('\n', ' ').replace('\r', '')
    except subprocess.TimeoutExpired:
        output = "TIMEOUT"
    except Exception as e:
        output = f"ERROR: {str(e)}"
        
    duration = time.time() - start_time
    return output, duration

def extract_params(filename):
    """
    Parses 'p_0.00_10.00_5.00.smt2' into a dictionary of parameters.
    """
    name_no_ext = os.path.splitext(filename)[0]
    parts = name_no_ext.split('_')
    
    # We skip the first part (parts[0]) assuming it is the prefix "p"
    raw_params = parts[1:]
    
    param_dict = {}
    for i, val in enumerate(raw_params):
        param_dict[f'Param_{i+1}'] = val
        
    return param_dict

def load_filter_set(csv_path):
    """Read a CSV and return the set of unique filenames from its 'Filename' column."""
    filenames = set()
    with open(csv_path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            filenames.add(row['Filename'])
    return filenames

def main():
    # --- Argument Parsing ---
    parser = argparse.ArgumentParser(description="Run benchmarks on SMT2 files in a specific folder.")
    parser.add_argument("--folder", help="Path to the folder containing .smt2 files")
    parser.add_argument("--filter-csv", metavar="CSV",
                        help="Only run benchmarks whose Filename appears in this CSV")
    
    args = parser.parse_args()
    
    smt_dir = args.folder

    # Validate directory
    if not os.path.isdir(smt_dir):
        print(f"Error: The directory '{smt_dir}' does not exist.")
        sys.exit(1)

    # Gather files
    files = glob.glob(os.path.join(smt_dir, "*.smt2"))
    files.sort()

    if not files:
        print(f"No .smt2 files found in '{smt_dir}'.")
        return

    # Optionally filter to only filenames present in a CSV
    if args.filter_csv:
        if not os.path.isfile(args.filter_csv):
            print(f"Error: Filter CSV '{args.filter_csv}' does not exist.")
            sys.exit(1)
        allowed = load_filter_set(args.filter_csv)
        files = [f for f in files if os.path.basename(f) in allowed]
        files.sort()
        if not files:
            print(f"No matching .smt2 files after filtering with '{args.filter_csv}'.")
            return
        print(f"Filtered to {len(files)} files using '{args.filter_csv}'.")

    # --- Dynamic Header Generation ---
    first_file_params = extract_params(os.path.basename(files[0]))
    param_headers = list(first_file_params.keys())
    
    fieldnames = ['Filename'] + param_headers + ['Tool', 'Result', 'Time_Seconds']

    print(f"Found {len(files)} files in '{smt_dir}'.")
    print(f"Detected {len(param_headers)} parameters per file.")
    
    # Determine output path (save CSV inside the benchmark folder or current dir)
    # Here we save it in the current directory where the script is run
    print(f"Writing results to {OUTPUT_CSV}...")

    with open(OUTPUT_CSV, mode='w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for idx, filepath in enumerate(files):
            filename = os.path.basename(filepath)
            
            # 1. Extract parameters
            params = extract_params(filename)
            
            print(f"Processing {idx}/{len(files)}: {filename}...")

            # 2. Run tools
            for tool_name, tool_cmd in TOOLS.items():
                output, duration = run_single_tool(tool_cmd, filepath, run_index=idx)

                # 3. Write row
                row_data = {
                    'Filename': filename,
                    'Tool': tool_name,
                    'Result': output,
                    'Time_Seconds': f"{duration:.4f}"
                }
                row_data.update(params)

                writer.writerow(row_data)

    print("Done.")

if __name__ == "__main__":
    main()