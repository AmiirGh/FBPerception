from Setup import importlib
import Setup
importlib.reload(Setup)

from Setup import *

df = pd.read_csv(METADATA_DIR)

def capitalize_strings(value):
    if isinstance(value, str):
        words = value.split()
        capitalized_words = [word.capitalize() for word in words]
        return ' '.join(capitalized_words)
    return value

df = df.applymap(capitalize_strings)

bar_columns = [
    "Superior sense",
    "Handness",
    "Ticklishness",
    "Glasses",
    "Diplopia",
    "Hearing impairment",
    "Experience of motion sickness",
    "Experience in using VR",
    "Gender",
]

short_labels = [
    "Superior\nsense",
    "Handness",
    "Ticklishness",
    "Glasses",
    "Diplopia",
    "Hearing\nimpairment",
    "Motion\nsickness",
    "VR usage\nexperience",
    "Gender",
]

label_mapping = {
    "Male": "M", "Female": "F",
    "Right": "R", "Left": "L",
    "Yes": "Y", "No": "N",
    "Visual": "V", "Auditory": "A", "Haptic": "H",
}

# --- Define Colors ---
# Two distinct blues for the binary bars
binary_blues = ['#4C72B0', '#A6BADD']

# Set 2 from seaborn mapped specifically to A, H, and V
set2_palette = sns.color_palette("Set2")
sup_sense_colors = {
    'A': set2_palette[0],  # 1st color of Set 2
    'H': set2_palette[1],  # 2nd color of Set 2
    'V': set2_palette[2]  # 3rd color of Set 2
}

# --- Plotting Setup ---
fig, ax = plt.subplots(1, 1, figsize=(FIG_HEIGHT * ASPECT_RATIO, FIG_HEIGHT * 1.1))

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_linewidth(AXIS_LINEWIDTH)
ax.spines['left'].set_linewidth(AXIS_LINEWIDTH)

positions = np.arange(len(bar_columns))
bar_height = 0.6

all_data = []
for col in bar_columns:
    if col in df.columns:
        counts = df[col].value_counts()
        categories = counts.index.astype(str)
        values = counts.values
        total = sum(values)
        percentages = [v / total * 100 for v in values]
        short_categories = [label_mapping.get(cat, cat[:1]) for cat in categories]
        all_data.append({
            'col_name': col,  # Added column name here to reference in the plotting loop
            'categories': short_categories,
            'values': values,
            'percentages': percentages,
            'total': total
        })

# --- Plotting Loop ---
for i, data in enumerate(all_data):
    left = 0
    col_name = data['col_name']

    for j, (cat, val, pct) in enumerate(zip(data['categories'], data['values'], data['percentages'])):

        # Determine the correct color based on the bar type
        if col_name == "Superior sense":
            current_color = sup_sense_colors.get(cat, '#CCCCCC')  # Fallback color just in case
        else:
            current_color = binary_blues[j % 2]  # Alternates between the two blues

        # Plot bar (linewidth=0 removes the border)
        bar = ax.barh(i, val, height=bar_height, left=left,
                      color=current_color, linewidth=0)

        # Text placement
        if val > 2:
            ax.text(left + val / 2, i - 0.05, f'{cat}',
                    ha='center', va='center', fontsize=FONTSIZE - 3)
        else:
            ax.text(left + val + 0.5, i - 0.05, f'{cat}',
                    ha='left', va='center', fontsize=FONTSIZE - 3)
        left += val

# --- Formatting ---
ax.set_yticks(positions)
ax.set_yticklabels(short_labels, fontsize=FONTSIZE)
ax.grid(axis='x', alpha=GRID_ALPHA, linestyle=GRID_LINESTYLE)
ax.set_axisbelow(True)
ax.set_xlabel("Count", fontsize=FONTSIZE)

max_total = max([data['total'] for data in all_data])
ax.set_xlim(0, max_total + max_total * 0.15)
ax.set_xticks([0, 10, 20, 30, 40, 50, 54, 60])
plt.tight_layout()
plt.savefig('barplot_info.pdf', format='pdf', bbox_inches='tight')
plt.show()