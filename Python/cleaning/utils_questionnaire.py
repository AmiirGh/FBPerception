import matplotlib.pyplot as plt

from utils import *
import textwrap
def plot_final_MNO(df_questionnaire_final):
    col_mapping = {
        'بازخورد صوتی برایم واضح و متمایز بود.': 'audio',
        'بازخورد لرزشی برایم واضح و متمایز بود.': 'haptic',
        'بازخورد تصویری برایم واضح و متمایز بود.': 'visual'
    }

    # 3. Select and rename the columns
    df_feedback = df_questionnaire_final[list(col_mapping.keys())].rename(columns=col_mapping)

    # 4. Melt the dataframe into a long format for Seaborn
    df_melted = df_feedback.melt(var_name='Modality', value_name='Rating')

    # 5. Set up the plot aesthetics
    plt.figure(figsize=(8, 6))
    modality_order = ['audio', 'haptic', 'visual']
    palette = sns.color_palette("Set2")

    # 6. Create the bar plot
    sns.boxplot(
        data=df_melted,
        x='Modality',
        y='Rating',
        order=modality_order,
        palette=palette,
        showmeans=True
        # capsize=0.1  # Adds small caps to the error bars
    )

    # 7. Customize labels and layout
    plt.title('Feedback Clarity and Distinctness by Modality', fontsize=14)
    plt.xlabel('Feedback Modality', fontsize=12)
    plt.ylabel('Rating (1-5)', fontsize=12)
    plt.ylim(0, 5.5)  # Assuming standard 5-point Likert scale

    # 8. Save the figure
    plt.tight_layout()
    plt.show()



def plot_final_DEFGHIJK(df_questionnaire_final):
    labels1 = ['Cognitive Load', 'Physical Load', 'Try to act fast']
    labels2 = ['self ev. - positioning', 'self ev. - dodging', 'self ev. - improving']
    labels3 = ['stress', 'self ev. - adapting']

    # Extract columns based on index (assuming A=0, B=1, etc.)
    # D, E, F -> 3, 4, 5
    df1 = df_questionnaire_final.iloc[:, 3:6].copy()
    df1.columns = labels1

    # G, H, I -> 6, 7, 8
    df2 = df_questionnaire_final.iloc[:, 6:9].copy()
    df2.columns = labels2

    # J, K -> 9, 10
    df3 = df_questionnaire_final.iloc[:, 9:11].copy()
    df3.columns = labels3

    # Set up 3 subplots
    fig, axes = plt.subplots(1, 3, figsize=(15, 6))

    # Plot 1
    sns.barplot(data=df1.melt(), x='variable', y='value', palette="Paired", ax=axes[0])
    axes[0].set_title('Cognitive & Physical Demands')
    axes[0].set_ylabel('Rating')
    axes[0].set_xlabel('')
    axes[0].tick_params(axis='x', rotation=45)

    # Plot 2
    sns.barplot(data=df2.melt(), x='variable', y='value', palette="Paired", ax=axes[1])
    axes[1].set_title('Self Evaluation')
    axes[1].set_ylabel('')
    axes[1].set_xlabel('')
    axes[1].tick_params(axis='x', rotation=45)

    # Plot 3
    sns.barplot(data=df3.melt(), x='variable', y='value', palette="Paired", ax=axes[2])
    axes[2].set_title('Stress & Adaptation')
    axes[2].set_ylabel('')
    axes[2].set_xlabel('')
    axes[2].tick_params(axis='x', rotation=45)

    plt.tight_layout()
    plt.show()


def plot_final_L(df_questionnaire_final):
    # Column L is at index 11
    col_name = df_questionnaire_final.columns[11]

    val_mapping = {
        'تشخیص مکان جسم': 'positioning',
        'اجتناب از برخورد با موانع': 'dodging',
        'هر دو به یک اندازه': 'both'
    }

    mapped_series = df_questionnaire_final[col_name].map(val_mapping)

    plt.figure(figsize=(4, 3))

    sns.countplot(
        x=mapped_series,
        order=['positioning', 'dodging', 'both'],
        palette='Paired',
        width=0.3

    )

    plt.title('Count of Most Challenging Tasks')
    plt.xlabel('Task')
    plt.ylabel('Count')

    # Restrict the y-axis to start at 12 (and go slightly above 20 to fit the top bar)
    plt.ylim(12, 21)

    # Set the exact y-axis ticks requested
    plt.yticks([16, 18, 20])

    plt.tight_layout()
    plt.show()

def plot_final_P(df_questionnaire_final):
    # Column P is at index 15 (A=0, ..., L=11, M=12, N=13, O=14, P=15)
    col_name = df_questionnaire_final.columns[15]

    # Set up the figure size
    plt.figure(figsize=(8, 6))

    # Create the box plot using seaborn
    sns.boxplot(
        y=df_questionnaire_final[col_name],
        color='skyblue',  # You can change the color
        width=0.4         # Adjust the width of the box if needed
    )

    # Add labels and a title
    plt.title(f'Box Plot of {col_name}')
    plt.ylabel('Values')

    # Display the plot cleanly
    plt.tight_layout()
    plt.show()


def plot_final_QRS(df_questionnaire_final):
    # 1. Dynamically grab the column names at indices 16, 17, and 18
    cols_to_plot = df_questionnaire_final.columns[16:19]

    # 2. Map the original column names to your desired labels
    col_mapping = {
        cols_to_plot[0]: 'dual',
        cols_to_plot[1]: 'dodging hard',
        cols_to_plot[2]: 'positioning hard'
    }

    # 3. Select those columns and rename them
    df_selected = df_questionnaire_final[list(col_mapping.keys())].rename(columns=col_mapping)

    # 4. Melt the dataframe into a long format so Seaborn can plot it easily
    df_melted = df_selected.melt(var_name='Condition', value_name='Value')

    # 5. Set up the figure size and color palette
    plt.figure(figsize=(8, 6))
    palette = sns.color_palette("Set2")

    # 6. Create the box plot (keeping the mean markers from your previous preference)
    sns.boxplot(
        data=df_melted,
        x='Condition',
        y='Value',
        palette=palette,
        # showmeans=True,
        meanline=True,
        meanprops={  # UPDATED: Line styling properties instead of marker properties
            "color": "red",  # Makes the mean line red
            "linestyle": "--",  # Makes the mean line dashed (to distinguish from the median)
            "linewidth": 2  # Makes the line thicker
        }
    )

    # 7. Add titles and labels
    plt.title('Comparison of Task Conditions', fontsize=14)
    plt.xlabel('Condition', fontsize=12)
    plt.ylabel('Score / Value', fontsize=12)

    # Note: If this is a Likert scale (e.g., 1-5 or 1-7), uncomment the line below to lock the y-axis
    # plt.ylim(0, 6)

    # 8. Render the plot cleanly
    plt.tight_layout()
    plt.show()


def plot_mid_fatigue_progression(df_questionnaire_mid):
    # Extract the fatigue columns based on their indices (3, 12, 21)
    # and map them to readable English labels
    fatigue_cols = {
        df_questionnaire_mid.columns[3]: 'Part 1',
        df_questionnaire_mid.columns[12]: 'Part 2',
        df_questionnaire_mid.columns[21]: 'Part 3'
    }

    # Subset the dataframe and rename the columns
    df_fatigue = df_questionnaire_mid[list(fatigue_cols.keys())].rename(columns=fatigue_cols)

    # Convert data from wide to long format for Seaborn
    df_melted = df_fatigue.melt(var_name='Experiment Stage', value_name='Fatigue Score')

    # Create the plot
    plt.figure(figsize=(8, 6))

    sns.barplot(
        data=df_melted,
        x='Experiment Stage',
        y='Fatigue Score',
        palette='Paired',
        capsize=0.1
    )

    # Add titles and labels
    plt.title('Progression of Fatigue Over Time', fontsize=14)
    plt.xlabel('Experiment Stage', fontsize=12)
    plt.ylabel('Average Fatigue Score', fontsize=12)

    plt.tight_layout()
    plt.show()


def plot_mid_Dizziness_progression(df_questionnaire_mid):
    # 1. Extract Nausea/Dizziness columns (Indices 4, 13, 22)
    cols = {
        df_questionnaire_mid.columns[4]: 'Part 1',
        df_questionnaire_mid.columns[13]: 'Part 2',
        df_questionnaire_mid.columns[22]: 'Part 3'
    }
    df_sub = df_questionnaire_mid[list(cols.keys())].rename(columns=cols)
    df_melted = df_sub.melt(var_name='Experiment Stage', value_name='Dizziness Score')

    # 2. Plot the Line Chart
    plt.figure(figsize=(8, 6))
    sns.lineplot(
        data=df_melted,
        x='Experiment Stage',
        y='Dizziness Score',
        marker='o',  # Add dots for each stage
        markersize=8,
        err_style='bars',  # Shows standard error as vertical bars
        color='tab:red',  # Reddish tone fits "nausea/dizziness" visually
        linewidth=2
    )

    plt.title('Progression of Nausea/Dizziness Over Time', fontsize=14)
    plt.xlabel('Experiment Stage', fontsize=12)
    plt.ylabel('Average Nausea/Dizziness Score', fontsize=12)
    plt.ylim(0, 5.5)  # Based on standard 1-5 scale; adjust if your max is different

    plt.tight_layout()
    plt.show()


def plot_mid_usefull_fb(df_questionnaire_mid):
    # 1. Extract 'Most Useful Feedback' columns (Indices 5, 14, 23)
    cols = {
        df_questionnaire_mid.columns[5]: 'Part 1',
        df_questionnaire_mid.columns[14]: 'Part 2',
        df_questionnaire_mid.columns[23]: 'Part 3'
    }
    df_sub = df_questionnaire_mid[list(cols.keys())].rename(columns=cols)

    # 2. Translate the values from Persian to English
    for col in df_sub.columns:
        # Ensure it's a string
        df_sub[col] = df_sub[col].astype(str)

        # Strip any accidental whitespace first
        df_sub[col] = df_sub[col].str.replace(' ', '')

        # Replace the modalities
        df_sub[col] = df_sub[col].str.replace('لرزشی', 'haptic')
        df_sub[col] = df_sub[col].str.replace('صوتی', 'audio')
        df_sub[col] = df_sub[col].str.replace('تصویری', 'visual')

        # Replace the Persian comma with an English comma and a space for readability
        df_sub[col] = df_sub[col].str.replace('،', ', ')

    # 3. Melt the dataframe
    df_melted = df_sub.melt(var_name='Experiment Stage', value_name='Feedback Type')

    # 4. Group and count occurrences for the stacked bar
    counts = df_melted.groupby(['Experiment Stage', 'Feedback Type']).size().unstack(fill_value=0)

    # 5. Plot the Stacked Bar Chart
    counts.plot(
        kind='bar',
        stacked=True,
        figsize=(10, 6),
        colormap='Paired'
    )

    plt.title('Shift in "Most Useful Feedback" Preference', fontsize=14)
    plt.xlabel('Experiment Stage', fontsize=12)
    plt.ylabel('Number of Users', fontsize=12)

    # Move the legend outside the plot
    plt.legend(title='Feedback Preference', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.xticks(rotation=0)

    plt.tight_layout()
    plt.show()


def _get_melted_df(df, indices_dict, value_name):
    """Helper function to reshape specific index-based columns into long format"""
    records = []
    for part, modalities in indices_dict.items():
        for mod, idx in modalities.items():
            col_name = df.columns[idx]
            for val in df[col_name].dropna():
                # Coerce to numeric in case there are empty strings or invalid chars
                records.append({'Part': part, 'Modality': mod, value_name: pd.to_numeric(val, errors='coerce')})
    return pd.DataFrame(records).dropna()


def plot_mid_modality_confusion(df_questionnaire_mid):
    # Mapping Parts and Modalities to their respective column indices for Confusion
    indices = {
        'Part 1': {'audio': 7, 'haptic': 8, 'visual': 6, },
        'Part 2': {'audio': 16, 'haptic': 17, 'visual': 15, },
        'Part 3': {'audio': 25, 'haptic': 26, 'visual': 24, }
    }
    df_melted = _get_melted_df(df_questionnaire_mid, indices, 'Confusion Score')

    plt.figure(figsize=(10, 6))
    sns.barplot(
        data=df_melted,
        x='Modality',
        y='Confusion Score',
        hue='Part',
        palette='Paired',
        capsize=0.05
    )
    plt.title('Average Confusion by Modality (Grouped by Part)', fontsize=14)
    plt.xlabel('Feedback Modality', fontsize=12)
    plt.ylabel('Average Confusion Score', fontsize=12)
    plt.ylim(0, 5.5)
    plt.legend(title='Experiment Stage', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.show()


def plot_mid_percieved_speed(df_questionnaire_mid):
    # Mapping Parts and Modalities to their respective column indices for Speed
    indices = {
        'Part 1': {'audio': 10, 'haptic': 11, 'visual': 9},
        'Part 2': {'audio': 19, 'haptic': 20, 'visual': 18, },
        'Part 3': {'audio': 28, 'haptic': 29, 'visual': 27, }
    }
    df_melted = _get_melted_df(df_questionnaire_mid, indices, 'Perceived Speed Score')

    plt.figure(figsize=(10, 6))
    sns.barplot(
        data=df_melted,
        x='Modality',
        y='Perceived Speed Score',
        hue='Part',
        palette='Paired',
        capsize=0.05
    )
    plt.title('Average Perceived Speed by Modality (Grouped by Part)', fontsize=14)
    plt.xlabel('Feedback Modality', fontsize=12)
    plt.ylabel('Average Speed Score', fontsize=12)
    plt.ylim(0, 5.5)
    plt.legend(title='Experiment Stage', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.show()


def plot_mid_learning_curve(df_questionnaire_mid):
    # Reusing the Confusion indices for the learning curve
    indices = {
        'Part 1': {'audio': 7,  'haptic': 8, 'visual': 6},
        'Part 2': {'audio': 16, 'haptic': 17, 'visual': 15},
        'Part 3': {'audio': 25, 'haptic': 26, 'visual': 24}
    }
    df_melted = _get_melted_df(df_questionnaire_mid, indices, 'Confusion Score')

    plt.figure(figsize=(8, 6))
    sns.lineplot(
        data=df_melted,
        x='Part',
        y='Confusion Score',
        hue='Modality',
        marker='o',
        markersize=8,
        palette='Set2',
        linewidth=2.5,
        err_style='bars'  # shows confidence interval lines
    )
    plt.title('Learning Curve: Confusion Reduction Over Time', fontsize=14)
    plt.xlabel('Experiment Stage', fontsize=12)
    plt.ylabel('Average Confusion Score', fontsize=12)
    plt.ylim(0, 5.5)
    plt.tight_layout()
    plt.show()


