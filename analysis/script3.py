import pandas as pd
import numpy as np

# Load Data
df = pd.read_csv('satisfiable_benchmarks2.csv')

# --- 1. Robust Success Filtering Logic ---
def is_success(row):
    res = str(row['Result']).lower()
    tool = row['Tool']
    if tool == 'Phaserr':
        return 'success' in res
    elif tool in ['Z3', 'Golem']:
        return 'sat' in res and 'unsat' not in res
    return False

df['is_solved'] = df.apply(is_success, axis=1)

# Only work with successfully solved benchmarks
solved_df = df[df['is_solved'] == True].copy()

# --- 2. Calculate Benchmark Min-Times & Phaserr's Times ---

# Get minimum time per filename across all tools (This is the VBS time)
vbs_times = solved_df.groupby('Filename')['Time_Seconds'].min().reset_index()
vbs_times.rename(columns={'Time_Seconds': 'Min_Time'}, inplace=True)

# Get specific times for Phaserr
phaserr_df = solved_df[solved_df['Tool'] == 'Phaserr'][['Filename', 'Time_Seconds']]
phaserr_df.rename(columns={'Time_Seconds': 'Phaserr_Time'}, inplace=True)

# Merge the VBS times and the Phaserr times side-by-side
merged = pd.merge(vbs_times, phaserr_df, on='Filename', how='left')

# If Phaserr completely failed or timed out, its time should be treated as Infinity
merged['Phaserr_Time'] = merged['Phaserr_Time'].fillna(np.inf)

# --- 3. Apply the Conditions ---
# Condition A: Minimum time is > 2 seconds (so NO tool solved it in <= 2 seconds)
condition1 = merged['Min_Time'] > 1.9

# Condition B: Another tool solved it faster than Phaserr (Min_Time is lower)
condition2 = merged['Min_Time'] < merged['Phaserr_Time']

# Extract the rows that meet both conditions
results = merged[condition1 & condition2].copy()

# --- 4. Identify the "Winning" Tool for Context ---
def get_fastest_tool(filename):
    tools = solved_df[solved_df['Filename'] == filename]
    # Identify the row with the lowest time for this specific file
    fastest_row = tools.loc[tools['Time_Seconds'].idxmin()]
    return fastest_row['Tool']

results['Fastest_Tool'] = results['Filename'].apply(get_fastest_tool)

# Display results
print(f"Found {len(results)} benchmarks matching the criteria.\n")
if len(results) > 0:
    print(results.to_string(index=False))