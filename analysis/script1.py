import pandas as pd

df = pd.read_csv('satisfiable_benchmarks2.csv')

SPACER_NAMES = {'Z3', 'Spacer'}
GOLEM_DAR_NAMES = {'Golem', 'Golem-DAR'}

def is_success(row):
    res = str(row['Result']).lower()
    tool = row['Tool']
    if tool == 'Phaserr':
        return 'success' in res
    elif tool in SPACER_NAMES:
        return 'sat' in res and 'unsat' not in res
    elif tool in GOLEM_DAR_NAMES:
        return 'sat' in res and 'unsat' not in res
    return False

df['is_solved'] = df.apply(is_success, axis=1)

solved_df = df[df['is_solved'] == True]

phaserr_solved = set(solved_df[solved_df['Tool'] == 'Phaserr']['Filename'])
spacer_solved = set(solved_df[solved_df['Tool'].isin(SPACER_NAMES)]['Filename'])
golem_dar_solved = set(solved_df[solved_df['Tool'].isin(GOLEM_DAR_NAMES)]['Filename'])

vbs_solved = phaserr_solved.union(spacer_solved).union(golem_dar_solved)

print(f"Unique Phaserr solved: {len(phaserr_solved)}")
print(f"Unique Spacer solved: {len(spacer_solved)}")
print(f"Unique Golem-DAR solved: {len(golem_dar_solved)}")
print(f"Total Unique Solved (VBS): {len(vbs_solved)}")

diff = vbs_solved - phaserr_solved
print(f"Number of instances solved by others but NOT Phaserr: {len(diff)}")

import matplotlib.pyplot as plt
import numpy as np

# Let's plot the cactus plot to see what it actually looks like.
phaserr_times = np.sort(solved_df[solved_df['Tool'] == 'Phaserr']['Time_Seconds'].values)
spacer_times = np.sort(solved_df[solved_df['Tool'].isin(SPACER_NAMES)]['Time_Seconds'].values)
golem_dar_times = np.sort(solved_df[solved_df['Tool'].isin(GOLEM_DAR_NAMES)]['Time_Seconds'].values)

# VBS
vbs_times = np.sort(solved_df.groupby('Filename')['Time_Seconds'].min().values)

plt.figure(figsize=(10, 6))
plt.plot(range(1, len(phaserr_times) + 1), phaserr_times, label='Phaserr', marker='.')
plt.plot(range(1, len(spacer_times) + 1), spacer_times, label='Spacer', marker='.')
plt.plot(range(1, len(golem_dar_times) + 1), golem_dar_times, label='Golem-DAR', marker='.')
plt.plot(range(1, len(vbs_times) + 1), vbs_times, label='VBS', marker='+', linestyle='--')

plt.yscale('log')
plt.xlabel('Number of Benchmarks Solved')
plt.ylabel('Time (s) [Log Scale]')
plt.legend()
plt.grid(True, which="both", ls="--")
plt.savefig('cactus_reconstructed..pdf', format='pdf')
print("Plot saved.")