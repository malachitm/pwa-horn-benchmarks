import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from pygments.styles import get_style_by_name
import re

SPACER_NAMES = {'Z3', 'Spacer'}
GOLEM_DAR_NAMES = {'Golem', 'Golem-DAR'}


def normalize_tool_name(tool):
    if tool in SPACER_NAMES:
        return 'Spacer'
    if tool in GOLEM_DAR_NAMES:
        return 'Golem-DAR'
    return tool

# 1. Dynamically extract the Staroffice color palette
style = get_style_by_name('staroffice')
staroffice_colors = []

# Scrape the hex colors directly from Pygment's token dictionary
for token, style_def in style.styles.items():
    # Matches both #FFFFFF and #FFF format
    match = re.search(r'#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})', style_def)
    if match:
        color = match.group(0)
        # Normalize 3-digit hex to 6-digit hex strings
        if len(color) == 4:
            color = '#' + ''.join([c*2 for c in color[1:]])
            
        # Ignore pure black/white/grays to save them for text and backgrounds
        if color.lower() not in ['#000000', '#ffffff', '#f8f8f8', '#f5f5f5']:
            if color not in staroffice_colors:
                staroffice_colors.append(color)

# 2. Update Matplotlib settings
plt.rcParams.update({
    # --- MANUSCRIPT COMPLIANCE: STRICTLY BLACK TIMES NEW ROMAN FONTS ---
    'font.family': 'serif',
    'font.serif': ['Times New Roman'],
    'text.color': 'black',
    'axes.labelcolor': 'black',
    'xtick.color': 'black',
    'ytick.color': 'black',
    'axes.edgecolor': 'black',
    'legend.labelcolor': 'black',
    
    # --- APPLY STAROFFICE STYLE ONLY TO DATA/BACKGROUND ---
    'axes.prop_cycle': plt.cycler('color', staroffice_colors),
    'axes.facecolor': style.background_color or 'white',
    
    # Subtle grid for readability
    'grid.color': '#dddddd'
})

def get_cactus_data_with_vbs(df):
    df = df.copy()
    df['Tool'] = df['Tool'].apply(normalize_tool_name)

    # --- 1. Robust Success Filtering Logic ---
    def is_success(row):
        res = str(row['Result']).lower()
        tool = row['Tool']
        if tool == 'Phaserr':
            return 'success' in res
        elif tool == 'Spacer' or tool == 'Golem-DAR':
            # Must contain 'sat' but explicitly avoid 'unsat'
            return 'sat' in res and 'unsat' not in res
        return False
        
    df['is_solved'] = df.apply(is_success, axis=1)
    
    # Only work with benchmarks that were actually solved
    solved_df = df[df['is_solved'] == True].copy()
    
    cactus_data = []
    tools = solved_df['Tool'].unique()

    # --- 2. Process Real Tools ---
    for tool in tools:
        tool_data = solved_df[solved_df['Tool'] == tool].copy()
        tool_data = tool_data.sort_values(by='Time_Seconds')
        tool_data['Solved_Count'] = range(1, len(tool_data) + 1)
        cactus_data.append(tool_data)

    # --- 3. Calculate VBS on ONLY solved instances ---
    # Group by Filename and take the MINIMUM time across all tools for successes
    vbs_times = solved_df.groupby('Filename')['Time_Seconds'].min().reset_index()
    
    # Sort VBS times (Fastest -> Slowest) just like a real tool
    vbs_times = vbs_times.sort_values(by='Time_Seconds')
    
    # Add metadata so it looks like a tool
    vbs_times['Tool'] = 'VBS'
    vbs_times['Solved_Count'] = range(1, len(vbs_times) + 1)
    
    # Add to our list
    cactus_data.append(vbs_times)
    
    return pd.concat(cactus_data, ignore_index=True)

# Load Data
df = pd.read_csv('./satisfiable_benchmarks2.csv')
plot_data = get_cactus_data_with_vbs(df)

# --- 4. Plotting with Custom Style ---
fig, ax = plt.subplots(figsize=(7, 5))

real_tools = [t for t in plot_data['Tool'].unique() if t != 'VBS']

# Map each tool to a Staroffice color, looping back to the start if we run out of colors
palette = {t: staroffice_colors[i % len(staroffice_colors)] for i, t in enumerate(real_tools)}

palette['VBS'] = 'black'  # VBS is always black

# Define styles: Real tools get solid lines, VBS gets dashed
dashes = {t: (1, 0) for t in real_tools}  # Solid lines
dashes['VBS'] = (3, 3)    # Dashed line

sns.lineplot(
    data=plot_data,
    x='Solved_Count',
    y='Time_Seconds',
    hue='Tool',
    style='Tool',
    palette=palette,
    dashes=dashes,
    markers=True,  # Markers for everyone
    markevery=0.1, # Optional: Don't clutter the VBS line with too many markers if it solves 1000s
    ax=ax
)

# Standard Formatting
ax.set_yscale('log')
ax.set_xlabel("Number of Benchmarks Solved")
ax.set_ylabel("Time (s) [Log Scale]")
ax.grid(True, which="both", ls="-", alpha=0.2)
ax.legend(loc='lower right')

plt.tight_layout()
plt.savefig("./cactus_vbs_staroffice.pdf", format='pdf')
plt.show()