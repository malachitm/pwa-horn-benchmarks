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

# --- 2. Find the Fastest Tool per Benchmark ---
# Sort all successful solves by time (fastest first)
sorted_df = solved_df.sort_values('Time_Seconds')

# Drop duplicate filenames to keep ONLY the very first (fastest) tool for each benchmark
fastest_df = sorted_df.drop_duplicates('Filename').copy()

# Rename columns for clarity
fastest_df = fastest_df[['Filename', 'Tool', 'Time_Seconds']].rename(
    columns={'Tool': 'Fastest_Tool', 'Time_Seconds': 'Min_Time'}
)

# --- 3. Get Specific Times for Phaserr ---
phaserr_df = solved_df[solved_df['Tool'] == 'Phaserr'][['Filename', 'Time_Seconds']]
phaserr_df = phaserr_df.rename(columns={'Time_Seconds': 'Phaserr_Time'})

# Merge the Fastest Tool info with Phaserr's times
merged = pd.merge(fastest_df, phaserr_df, on='Filename', how='left')

# If Phaserr completely failed/timed out, treat its time as Infinity
merged['Phaserr_Time'] = merged['Phaserr_Time'].fillna(np.inf)

# --- 4. Apply Condition: Phaserr is NOT the absolute fastest ---
results = merged[merged['Fastest_Tool'] != 'Phaserr'].copy()

# Sort by the minimum time just to see the fastest problems at the top
results = results.sort_values('Min_Time')

# Display and save the results
print(f"Found {len(results)} benchmarks where Phaserr was NOT the minimum time.\n")

if len(results) > 0:
    # Print the first 15 as a preview
    print(results.head(15).to_string(index=False))
    
    # Save everything to a CSV file
    results.to_csv('phaserr_not_fastest.csv', index=False)
    print("\nFull list saved to 'phaserr_not_fastest.csv'")