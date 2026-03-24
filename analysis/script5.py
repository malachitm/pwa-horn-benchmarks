import pandas as pd
import numpy as np

# --- 1. Load Data ---
df = pd.read_csv('satisfiable_benchmarks2.csv')

# --- 2. Robust Success Filtering ---
def is_success(row):
    res = str(row['Result']).lower()
    tool = row['Tool']
    if tool == 'Phaserr':
        return 'success' in res
    elif tool in ['Z3', 'Golem']:
        return 'sat' in res and 'unsat' not in res
    return False

df['is_solved'] = df.apply(is_success, axis=1)

# --- 3. Categorize by the difference between Param 1 and Param 2 ---
# We use absolute difference so order doesn't matter (e.g. 50-0 vs 0-50)
df['Param_Diff'] = np.abs(df['Param_1'] - df['Param_2'])

def get_category(diff):
    if diff == 0:
        return 'd0'
    elif 0 < diff <= 50:
        return 'd50'
    elif 50 < diff <= 100:
        return 'd100'
    elif diff >= 1000:
        return 'd1000+'
    else:
        return 'other' # Just in case there's an unexpected gap in the data

df['Category'] = df['Param_Diff'].apply(get_category)

# --- 4. Calculate Stats per Category ---
categories = ['d0', 'd50', 'd100', 'd1000+']
tools = ['Phaserr', 'Z3', 'Golem']

# Find how many total UNIQUE filenames exist in each category
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
        avg_time = tool_df['Time_Seconds'].mean() if solved_count > 0 else 0
        
        results.append({
            'Category': cat,
            'Total_Benchmarks': total_in_cat,
            'Tool': tool,
            'Solved': solved_count,
            'Percentage_Solved': f"{pct_solved:.2f}%",
            'Avg_Time_(s)': f"{avg_time:.4f}"
        })

# --- 5. Generate Summarized Totals ---
for tool in tools:
    tool_df = df[(df['Tool'] == tool) & (df['is_solved'] == True)]
    
    solved_count = tool_df['Filename'].nunique()
    pct_solved = (solved_count / total_all_problems) * 100 if total_all_problems > 0 else 0
    avg_time = tool_df['Time_Seconds'].mean() if solved_count > 0 else 0
    
    results.append({
        'Category': 'TOTAL SUMMARY',
        'Total_Benchmarks': total_all_problems,
        'Tool': tool,
        'Solved': solved_count,
        'Percentage_Solved': f"{pct_solved:.2f}%",
        'Avg_Time_(s)': f"{avg_time:.4f}"
    })

# --- 6. Display and Export ---
final_df = pd.DataFrame(results)

print(final_df.to_string(index=False))

# Export to CSV for easy sharing or Excel formatting
final_df.to_csv('tool_category_performance.csv', index=False)
print("\nResults successfully saved to 'tool_category_performance.csv'.")