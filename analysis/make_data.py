import pandas as pd
import numpy as np
import glob

# --- 1. Load Data ---
csv_files = glob.glob('b0*.csv')

# Read each CSV file into a dataframe and store them in a list
dataframes = [pd.read_csv(file) for file in csv_files]

# Combine (concatenate) all dataframes into a single one vertically
df = pd.concat(dataframes, ignore_index=True)

# --- 2. Robust Success Filtering ---
def is_success(row):
    try:
        t = float(row.get('Time_Seconds', np.nan))
    except Exception:
        return False
    return t <= 300.0

df['is_solved'] = df.apply(is_success, axis=1)

# --- 3. Categorize by the difference between Param 1 and Param 2 ---
def get_category(diff):
    return "interval"

# Assign a fallback or uncomment your calculation:
df['Category'] = "interval"

# --- 4. Calculate Stats per Category ---
categories = ['interval']
tools = ['Phaserr', 'Spacer', 'Golem']

cat_totals = df.groupby('Category')['Filename'].nunique().to_dict()
total_all_problems = df['Filename'].nunique()

results = []

for cat in categories:
    cat_df = df[df['Category'] == cat]
    total_in_cat = cat_totals.get(cat, 0)
    
    for tool in tools:
        # Filter down to the specific tool and successful solves
        tool_df = cat_df[(cat_df['Tool'] == tool) & (cat_df['is_solved'] == True)]
        
        solved_count = tool_df['Filename'].nunique()
        pct_solved = (solved_count / total_in_cat) * 100 if total_in_cat > 0 else 0
        
        # Calculate Average AND Median
        avg_time = tool_df['Time_Seconds'].mean() if solved_count > 0 else 0
        median_time = tool_df['Time_Seconds'].median() if solved_count > 0 else 0
        
        results.append({
            'Category': cat,
            'Total_Benchmarks': total_in_cat,
            'Tool': tool,
            'Solved': solved_count,
            'Percentage_Solved': f"{pct_solved:.2f}%",
            'Avg_Time_(s)': f"{avg_time:.4f}",
            'Median_Time_(s)': f"{median_time:.4f}"
        })

# --- 5. Generate Summarized Totals ---
for tool in tools:
    tool_df = df[(df['Tool'] == tool) & (df['is_solved'] == True)]
    
    solved_count = tool_df['Filename'].nunique()
    pct_solved = (solved_count / total_all_problems) * 100 if total_all_problems > 0 else 0
    
    avg_time = tool_df['Time_Seconds'].mean() if solved_count > 0 else 0
    median_time = tool_df['Time_Seconds'].median() if solved_count > 0 else 0
    
    results.append({
        'Category': 'TOTAL SUMMARY',
        'Total_Benchmarks': total_all_problems,
        'Tool': tool,
        'Solved': solved_count,
        'Percentage_Solved': f"{pct_solved:.2f}%",
        'Avg_Time_(s)': f"{avg_time:.4f}",
        'Median_Time_(s)': f"{median_time:.4f}"
    })

# --- Unique solves between Golem and Spacer (ignore Phaserr) ---
# Filenames solved by each tool (only count rows marked as solved)
golem_files = set(df[(df['Tool'] == 'Golem') & (df['is_solved'] == True)]['Filename'].unique())
spacer_files = set(df[(df['Tool'] == 'Spacer') & (df['is_solved'] == True)]['Filename'].unique())

unique_golem = golem_files - spacer_files
unique_spacer = spacer_files - golem_files

ug_count = len(unique_golem)
us_count = len(unique_spacer)

pct_ug = (ug_count / total_all_problems) * 100 if total_all_problems > 0 else 0
pct_us = (us_count / total_all_problems) * 100 if total_all_problems > 0 else 0

results.append({
    'Category': 'UNIQUE (Golem vs Spacer)',
    'Total_Benchmarks': total_all_problems,
    'Tool': 'Golem (unique)',
    'Solved': ug_count,
    'Percentage_Solved': f"{pct_ug:.2f}%",
    'Avg_Time_(s)': '',
    'Median_Time_(s)': ''
})

results.append({
    'Category': 'UNIQUE (Golem vs Spacer)',
    'Total_Benchmarks': total_all_problems,
    'Tool': 'Spacer (unique)',
    'Solved': us_count,
    'Percentage_Solved': f"{pct_us:.2f}%",
    'Avg_Time_(s)': '',
    'Median_Time_(s)': ''
})

# --- 6. Display and Export ---
final_df = pd.DataFrame(results)

print(final_df.to_string(index=False))

# Export to CSV for easy sharing or Excel formatting
final_df.to_csv('total_statistics.csv', index=False)
print("\nResults successfully saved to 'tool_category_performance_with_median.csv'.")