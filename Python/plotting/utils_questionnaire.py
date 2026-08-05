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


def plot_metacognition_correlations(perception_results_all, df_questionnaire_final, color_palette):
    """
    Calculate participant accuracy for each modality, correlate accuracy
    with the corresponding questionnaire rating, and plot them on a SINGLE axis.

    Questionnaire mapping:
        auditory -> Q10
        visual   -> Q11
        haptic   -> Q12

    Invalidated trials:
        Trials where either perceived value is -1 are excluded.

    Returns
    -------
    correlation_df : pandas.DataFrame
        Spearman correlation and p-value for each modality.

    participant_results_df : pandas.DataFrame
        Participant-level accuracy and questionnaire ratings.

    fig : matplotlib.figure.Figure
        Generated figure.

    ax : matplotlib.axes.Axes
        The single plot axis.
    """

    modality_question_map = {"auditory": "Q10", "visual": "Q11", "haptic": "Q12"}
    plot_order = ["auditory", "visual", "haptic"]

    # Offsets to prevent dots from the 3 modalities from completely overlapping on the 1-5 integers
    modality_offsets = {"auditory": -0.15, "visual": 0.0, "haptic": 0.15}

    required_questionnaire_columns = {"Participant ID", "Q10", "Q11", "Q12"}
    missing_questionnaire_columns = required_questionnaire_columns - set(df_questionnaire_final.columns)

    if missing_questionnaire_columns:
        raise ValueError(f"Missing questionnaire columns: {sorted(missing_questionnaire_columns)}")

    participant_names = list(perception_results_all.keys())
    questionnaire = df_questionnaire_final.reset_index(drop=True).copy()

    if len(participant_names) != len(questionnaire):
        raise ValueError(
            f"The number of participants does not match. Perception participants: {len(participant_names)}, questionnaire participants: {len(questionnaire)}")

    required_perception_columns = {"Modality", "Angle", "Perceived angle", "Distance", "Perceived distance"}
    numeric_columns = ["Angle", "Perceived angle", "Distance", "Perceived distance"]
    participant_records = []

    for participant_index, participant_name in enumerate(participant_names):
        trials = perception_results_all[participant_name].copy()
        missing_perception_columns = required_perception_columns - set(trials.columns)

        if missing_perception_columns:
            raise ValueError(
                f"Participant '{participant_name}' is missing columns: {sorted(missing_perception_columns)}")

        trials["Modality"] = trials["Modality"].astype(str).str.strip().str.lower()

        for column in numeric_columns:
            trials[column] = pd.to_numeric(trials[column], errors="coerce")

        participant_id = questionnaire.loc[participant_index, "Participant ID"]

        for modality in plot_order:
            modality_trials = trials.loc[trials["Modality"] == modality].copy()

            valid_mask = modality_trials["Perceived angle"].notna() & ~modality_trials["Perceived angle"].isin(
                [0, -1]) & modality_trials[numeric_columns].notna().all(axis=1)
            valid_trials = modality_trials.loc[valid_mask]

            accurate_mask = valid_trials["Angle"].eq(valid_trials["Perceived angle"]) & valid_trials["Distance"].eq(
                valid_trials["Perceived distance"])

            number_valid = len(valid_trials)
            number_accurate = int(accurate_mask.sum())
            accuracy = number_accurate / number_valid if number_valid > 0 else np.nan

            question_column = modality_question_map[modality]
            rating = \
            pd.to_numeric(pd.Series([questionnaire.loc[participant_index, question_column]]), errors="coerce").iloc[0]

            participant_records.append({
                "Participant ID": participant_id,
                "Participant folder": participant_name,
                "Modality": modality,
                "Question": question_column,
                "Rating": rating,
                "Valid trials": number_valid,
                "Accurate trials": number_accurate,
                "Accuracy": accuracy,
                "Accuracy percent": accuracy * 100,
            })

    participant_results_df = pd.DataFrame(participant_records)

    # --- Plotting on a single axis ---
    fig, ax = plt.subplots(figsize=(10, 7))
    correlation_records = []
    rng = np.random.default_rng(42)

    for modality in plot_order:
        modality_data = participant_results_df.loc[
            participant_results_df["Modality"] == modality, ["Rating", "Accuracy percent"]].dropna()

        x = modality_data["Rating"].to_numpy(dtype=float)
        y = modality_data["Accuracy percent"].to_numpy(dtype=float)

        if len(modality_data) >= 3 and modality_data["Rating"].nunique() > 1 and modality_data[
            "Accuracy percent"].nunique() > 1:
            correlation, p_value = spearmanr(x, y)
        else:
            correlation, p_value = np.nan, np.nan

        correlation_records.append({
            "Modality": modality,
            "Question": modality_question_map[modality],
            "N": len(modality_data),
            "Spearman correlation": correlation,
            "p-value": p_value,
        })

        # Apply deterministic offset + slight random jitter so the 3 modalities don't completely overlap
        base_x = x + modality_offsets[modality]
        jittered_x = base_x + rng.normal(loc=0, scale=0.03, size=len(x))

        # Format legend label to include statistics
        if np.isnan(correlation):
            label_str = f"{modality.capitalize()} (ρ=N/A)"
        else:
            label_str = f"{modality.capitalize()} (ρ={correlation:.2f}, p={p_value:.3f})"

        # Scatter plot
        ax.scatter(jittered_x, y, s=65, color=color_palette[modality],
                   edgecolor="black", linewidth=0.6, alpha=0.75, label=label_str)

        # Trendline
        if len(x) >= 2 and np.unique(x).size > 1:
            slope, intercept = np.polyfit(x, y, 1)
            line_x = np.linspace(1, 5, 100)
            line_y = slope * line_x + intercept
            ax.plot(line_x, line_y, color=color_palette[modality], linewidth=2.5)

    # Axis formatting
    ax.set_title("Cue Clarity Rating vs. Perception Accuracy", fontsize=15, fontweight="bold", pad=15)
    ax.set_xlabel("Cue clarity rating", fontsize=12, fontweight="bold")
    ax.set_ylabel("Accuracy (%)", fontsize=12, fontweight="bold")
    ax.set_xticks([1, 2, 3, 4, 5])
    ax.set_xlim(0.5, 5.5)
    ax.set_ylim(-5, 105)
    ax.grid(alpha=0.3, linestyle="--")

    # Place legend neatly in the lower right (or wherever fits best)
    ax.legend(title="Modality & Spearman Correlation", fontsize=10,
              title_fontsize=11, loc="lower right", framealpha=0.9, edgecolor="gray")

    fig.tight_layout()
    fig.savefig('metacog_corr.pdf', format='pdf', bbox_inches='tight')

    correlation_df = pd.DataFrame(correlation_records)
    plt.show()

    print("\nSpearman correlation results:")
    print(correlation_df.round(3).to_string(index=False))


def plot_self_perc_success_vs_performance_correlations(perception_results_all, experiment_logs_all, df_questionnaire_final, color_palette):
    """
    Plot:
        1. Q4 localization-success rating versus total perception accuracy.
        2. Q5 obstacle-avoidance rating versus final collision count.

    Returns:
        correlation_df
        participant_results_df
        fig
        axes
    """

    required_questionnaire_columns = {"Participant ID", "Q4", "Q5"}
    missing_questionnaire_columns = required_questionnaire_columns - set(df_questionnaire_final.columns)

    if missing_questionnaire_columns:
        raise ValueError(f"Missing questionnaire columns: {sorted(missing_questionnaire_columns)}")

    participant_names = list(perception_results_all.keys())
    experiment_participant_names = list(experiment_logs_all.keys())
    questionnaire = df_questionnaire_final.reset_index(drop=True).copy()

    if len(participant_names) != len(questionnaire):
        raise ValueError(f"The participant counts do not match. Perception participants: {len(participant_names)}, questionnaire participants: {len(questionnaire)}")

    if len(experiment_participant_names) != len(questionnaire):
        raise ValueError(f"The participant counts do not match. Experiment-log participants: {len(experiment_participant_names)}, questionnaire participants: {len(questionnaire)}")

    if participant_names != experiment_participant_names:
        raise ValueError("The participant-folder order in perception_results_all and experiment_logs_all does not match.")

    required_perception_columns = {"Angle", "Perceived angle", "Distance", "Perceived distance"}
    numeric_columns = ["Angle", "Perceived angle", "Distance", "Perceived distance"]
    participant_records = []

    for participant_index, participant_name in enumerate(participant_names):
        trials = perception_results_all[participant_name].copy()
        experiment_logs = experiment_logs_all[participant_name].copy()

        missing_perception_columns = required_perception_columns - set(trials.columns)

        if missing_perception_columns:
            raise ValueError(f"Participant '{participant_name}' is missing perception columns: {sorted(missing_perception_columns)}")

        if "Number of collision" not in experiment_logs.columns:
            raise ValueError(f"Participant '{participant_name}' is missing the 'Number of collision' column.")

        for column in numeric_columns:
            trials[column] = pd.to_numeric(trials[column], errors="coerce")

        valid_mask = trials["Perceived angle"].notna() & ~trials["Perceived angle"].isin([0, -1]) & trials[numeric_columns].notna().all(axis=1)
        valid_trials = trials.loc[valid_mask].copy()

        accurate_mask = valid_trials["Angle"].eq(valid_trials["Perceived angle"]) & valid_trials["Distance"].eq(valid_trials["Perceived distance"])

        number_valid = len(valid_trials)
        number_accurate = int(accurate_mask.sum())
        total_accuracy = number_accurate / number_valid if number_valid > 0 else np.nan

        collision_values = pd.to_numeric(experiment_logs["Number of collision"], errors="coerce")
        final_collisions = collision_values.iloc[-1] if len(collision_values) > 0 else np.nan

        participant_id = questionnaire.loc[participant_index, "Participant ID"]
        q4_rating = pd.to_numeric(pd.Series([questionnaire.loc[participant_index, "Q4"]]), errors="coerce").iloc[0]
        q5_rating = pd.to_numeric(pd.Series([questionnaire.loc[participant_index, "Q5"]]), errors="coerce").iloc[0]

        participant_records.append({
            "Participant ID": participant_id,
            "Participant folder": participant_name,
            "Q4": q4_rating,
            "Q5": q5_rating,
            "Valid perception trials": number_valid,
            "Accurate perception trials": number_accurate,
            "Total accuracy": total_accuracy,
            "Total accuracy percent": total_accuracy * 100,
            "Final number of collisions": final_collisions,
        })

    participant_results_df = pd.DataFrame(participant_records)

    localization_data = participant_results_df[["Q4", "Total accuracy percent"]].dropna()
    collision_data = participant_results_df[["Q5", "Final number of collisions"]].dropna()

    if len(localization_data) >= 2 and localization_data["Q4"].nunique() > 1 and localization_data["Total accuracy percent"].nunique() > 1:
        localization_r, localization_p = pearsonr(localization_data["Q4"], localization_data["Total accuracy percent"])
    else:
        localization_r, localization_p = np.nan, np.nan

    if len(collision_data) >= 2 and collision_data["Q5"].nunique() > 1 and collision_data["Final number of collisions"].nunique() > 1:
        collision_r, collision_p = pearsonr(collision_data["Q5"], collision_data["Final number of collisions"])
    else:
        collision_r, collision_p = np.nan, np.nan

    correlation_df = pd.DataFrame([
        {"Relationship": "Q4 vs total accuracy", "N": len(localization_data), "Pearson r": localization_r, "p-value": localization_p},
        {"Relationship": "Q5 vs final collisions", "N": len(collision_data), "Pearson r": collision_r, "p-value": collision_p},
    ])

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    rng = np.random.default_rng(42)

    q4_x = localization_data["Q4"].to_numpy(dtype=float)
    accuracy_y = localization_data["Total accuracy percent"].to_numpy(dtype=float)
    q4_jittered = q4_x + rng.normal(loc=0, scale=0.04, size=len(q4_x))

    axes[0].scatter(q4_jittered, accuracy_y, s=65, color=color_palette["visual"], edgecolor="black", linewidth=0.6, alpha=0.85)

    if len(q4_x) >= 2 and np.unique(q4_x).size > 1:
        slope, intercept = np.polyfit(q4_x, accuracy_y, 1)
        line_x = np.linspace(q4_x.min(), q4_x.max(), 100)
        axes[0].plot(line_x, slope * line_x + intercept, color=color_palette["visual"], linewidth=2.5)

    localization_text = f"N = {len(localization_data)}\nPearson r = {localization_r:.3f}\np = {localization_p:.3f}" if not np.isnan(localization_r) else f"N = {len(localization_data)}\nPearson r = undefined"

    axes[0].text(0.04, 0.96, localization_text, transform=axes[0].transAxes, ha="left", va="top", fontsize=10, bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.8})
    axes[0].set_title("Perceived Localization Success")
    axes[0].set_xlabel("Q4 rating")
    axes[0].set_ylabel("Total accuracy (%)")
    axes[0].set_xticks(sorted(localization_data["Q4"].unique()))
    axes[0].set_ylim(-5, 105)
    axes[0].grid(alpha=0.25)

    q5_x = collision_data["Q5"].to_numpy(dtype=float)
    collision_y = collision_data["Final number of collisions"].to_numpy(dtype=float)
    q5_jittered = q5_x + rng.normal(loc=0, scale=0.04, size=len(q5_x))

    axes[1].scatter(q5_jittered, collision_y, s=65, color=color_palette["haptic"], edgecolor="black", linewidth=0.6, alpha=0.85)

    if len(q5_x) >= 2 and np.unique(q5_x).size > 1:
        slope, intercept = np.polyfit(q5_x, collision_y, 1)
        line_x = np.linspace(q5_x.min(), q5_x.max(), 100)
        axes[1].plot(line_x, slope * line_x + intercept, color=color_palette["haptic"], linewidth=2.5)

    collision_text = f"N = {len(collision_data)}\nPearson r = {collision_r:.3f}\np = {collision_p:.3f}" if not np.isnan(collision_r) else f"N = {len(collision_data)}\nPearson r = undefined"

    axes[1].text(0.04, 0.96, collision_text, transform=axes[1].transAxes, ha="left", va="top", fontsize=10, bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.8})
    axes[1].set_title("Perceived Obstacle-Avoidance Success")
    axes[1].set_xlabel("Q5 rating")
    axes[1].set_ylabel("Final number of collisions")
    axes[1].set_xticks(sorted(collision_data["Q5"].unique()))
    axes[1].set_ylim(bottom=0)
    axes[1].grid(alpha=0.25)

    fig.suptitle("Self-Reported Performance and Actual Performance", fontsize=15)
    fig.tight_layout()
    plt.show()
    fig.savefig('self_perc_perform_corr.pdf', format='pdf', bbox_inches='tight')
    print("\nPearson correlation results:")
    print(correlation_df.round(3).to_string(index=False))

    return correlation_df, participant_results_df, fig, axes


def plot_questionnaire_results(df, color_code):
    """
    Plots box plots for questionnaire columns Q1 to Q7.

    Parameters:
    df (pd.DataFrame): The dataframe containing the questionnaire data.
    color_code (str): Hex color code or standard color name (e.g., '#4C72B0' or 'skyblue').
    """
    # 1. Define the columns to plot
    columns_to_plot = ['Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7']

    # 2. Dictionary to rename the x-axis labels.
    # Change the values on the right side to rename your box plots on the chart.
    label_mapping = {
        'Q1': 'Mental demand',
        'Q2': 'Physical demand',
        'Q3': 'Reporting quickly',
        'Q4': 'Localizing success',
        'Q5': 'Avoidance success',
        'Q6': 'Improve performance ',
        'Q7': 'Stress'
    }

    # Extract only the relevant columns and filter out missing data if necessary
    df_subset = df[columns_to_plot].copy()

    # Melt the dataframe into a long format which is optimal for seaborn plotting
    df_melted = df_subset.melt(var_name='Question', value_name='Score')

    # Apply the renaming dictionary to the 'Question' column
    df_melted['Question'] = df_melted['Question'].map(label_mapping)

    # 3. Plotting
    sns.set_theme(style="whitegrid", context="paper", font_scale=1.2)
    fig, ax = plt.subplots(figsize=(10, 6))

    sns.boxplot(
        data=df_melted,
        x='Question',
        y='Score',
        color=color_code,
        width=0.5,
        ax=ax,
        showmeans=True,
        meanprops={
            "marker": "o",
            "markerfacecolor": "white",
            "markeredgecolor": "black",
            "markersize": "6"
        }
    )



    ax.set_title('Questionnaire Responses (Q1 - Q7)', fontweight='bold', fontsize=14)
    ax.set_ylabel('Score', fontweight='bold')
    ax.set_xlabel('')

    # Force Y-axis to clearly show the 1 to 5 scale
    ax.set_ylim(0.5, 5.5)
    ax.set_yticks([1, 2, 3, 4, 5])

    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()


def plot_unified_performance_correlations(perception_results_all, experiment_logs_all, df_questionnaire_final,
                                          color_palette):
    """
    Creates a 1x2 unified subplot figure:
      Subplot 1: Q10, Q11, Q12, & Q4 ratings vs. Modality/Total Accuracies.
      Subplot 2: Q5 rating vs. Final number of collisions.
    """

    # 1. Update color palette with the new requirements
    palette = color_palette.copy()
    palette.update({'total': '#2205d1', 'collision': '#8a754d'})

    # 2. Map the data structure
    # Relationship: (Modality/Group Name, Questionnaire Column, Data Column Name)
    accuracy_groups = [
        ("auditory", "Q10", "Auditory accuracy"),
        ("visual", "Q11", "Visual accuracy"),
        ("haptic", "Q12", "Haptic accuracy"),
        ("total", "Q4", "Total accuracy")
    ]

    # Offsets so the 4 scatter groups don't perfectly overlap on the integers 1-5
    x_offsets = {"auditory": -0.22, "visual": -0.07, "haptic": 0.07, "total": 0.22}

    # 3. Data Processing and Aggregation
    participant_names = list(perception_results_all.keys())
    questionnaire = df_questionnaire_final.reset_index(drop=True).copy()
    numeric_columns = ["Angle", "Perceived angle", "Distance", "Perceived distance"]

    participant_records = []

    for idx, p_name in enumerate(participant_names):
        trials = perception_results_all[p_name].copy()
        exp_logs = experiment_logs_all[p_name].copy()

        # Format perception data
        trials["Modality"] = trials["Modality"].astype(str).str.strip().str.lower()
        for col in numeric_columns:
            trials[col] = pd.to_numeric(trials[col], errors="coerce")

        # Get valid trials (excluding hardware faults -1)
        valid_trials = trials[trials["Perceived angle"].notna() & (trials["Perceived angle"] != -1)].copy()

        # Function to calculate accuracy percentage
        def calc_acc(df):
            if len(df) == 0: return np.nan
            hits = (df["Angle"] == df["Perceived angle"]) & (df["Distance"] == df["Perceived distance"])
            return (hits.sum() / len(df)) * 100

        # Accuracies
        acc_aud = calc_acc(valid_trials[valid_trials["Modality"] == "auditory"])
        acc_vis = calc_acc(valid_trials[valid_trials["Modality"] == "visual"])
        acc_hap = calc_acc(valid_trials[valid_trials["Modality"] == "haptic"])
        acc_tot = calc_acc(valid_trials)

        # Collisions
        col_vals = pd.to_numeric(exp_logs["Number of collision"], errors="coerce").dropna()
        final_col = col_vals.iloc[-1] if not col_vals.empty else np.nan

        # Questionnaire
        pid = questionnaire.loc[idx, "Participant ID"]
        q_vals = {q: pd.to_numeric(pd.Series([questionnaire.loc[idx, q]]), errors="coerce").iloc[0]
                  for q in ["Q4", "Q5", "Q10", "Q11", "Q12"]}

        participant_records.append({
            "Participant ID": pid,
            "Auditory accuracy": acc_aud, "visual_q": q_vals["Q11"],
            "Visual accuracy": acc_vis, "auditory_q": q_vals["Q10"],
            "Haptic accuracy": acc_hap, "haptic_q": q_vals["Q12"],
            "Total accuracy": acc_tot, "total_q": q_vals["Q4"],
            "Final collisions": final_col, "collision_q": q_vals["Q5"],
            "Q4": q_vals["Q4"], "Q5": q_vals["Q5"], "Q10": q_vals["Q10"], "Q11": q_vals["Q11"], "Q12": q_vals["Q12"]
        })

    results_df = pd.DataFrame(participant_records)

    # 4. Setup Plotting
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    rng = np.random.default_rng(42)
    correlation_records = []

    # ==========================================
    # Subplot 1: Ratings vs Accuracies
    # ==========================================
    for name, q_col, acc_col in accuracy_groups:
        data = results_df[[q_col, acc_col]].dropna()
        x = data[q_col].to_numpy(dtype=float)
        y = data[acc_col].to_numpy(dtype=float)

        if len(data) >= 3 and len(np.unique(x)) > 1:
            corr, p_val = spearmanr(x, y)
        else:
            corr, p_val = np.nan, np.nan

        correlation_records.append(
            {"Relationship": f"{q_col} vs {acc_col}", "N": len(data), "Spearman r": corr, "p-value": p_val})

        # Apply deterministic offset + slight jitter
        jittered_x = x + x_offsets[name] + rng.normal(loc=0, scale=0.02, size=len(x))

        label_str = f"{name.capitalize()} (ρ={corr:.2f}, p={p_val:.3f})" if not np.isnan(
            corr) else f"{name.capitalize()}"

        axes[0].scatter(jittered_x, y, s=50, color=palette[name], edgecolor="black",
                        linewidth=0.5, alpha=0.75, label=label_str)

        # Trendline
        if len(np.unique(x)) > 1:
            slope, intercept = np.polyfit(x, y, 1)
            line_x = np.linspace(1, 5, 100)
            axes[0].plot(line_x, slope * line_x + intercept, color=palette[name], linewidth=2.5)

    axes[0].set_title("Perceived Clarity/Success vs. Accuracy", fontsize=14, fontweight="bold")
    axes[0].set_xlabel("Questionnaire Rating (1-5)", fontsize=12)
    axes[0].set_ylabel("Accuracy (%)", fontsize=12)
    axes[0].set_xticks([1, 2, 3, 4, 5])
    axes[0].set_xlim(0.5, 5.5)
    axes[0].set_ylim(-5, 105)
    axes[0].grid(alpha=0.3, linestyle="--")
    axes[0].legend(title="Metric (Spearman ρ)", fontsize=9, loc="lower right", framealpha=0.9)

    # ==========================================
    # Subplot 2: Q5 vs Collisions
    # ==========================================
    col_data = results_df[["Q5", "Final collisions"]].dropna()
    x_col = col_data["Q5"].to_numpy(dtype=float)
    y_col = col_data["Final collisions"].to_numpy(dtype=float)

    if len(col_data) >= 3 and len(np.unique(x_col)) > 1:
        corr_col, p_val_col = spearmanr(x_col, y_col)
    else:
        corr_col, p_val_col = np.nan, np.nan

    correlation_records.append(
        {"Relationship": "Q5 vs Final collisions", "N": len(col_data), "Spearman r": corr_col, "p-value": p_val_col})

    jittered_x_col = x_col + rng.normal(loc=0, scale=0.04, size=len(x_col))

    axes[1].scatter(jittered_x_col, y_col, s=65, color=palette["collision"], edgecolor="black",
                    linewidth=0.6, alpha=0.85)

    if len(np.unique(x_col)) > 1:
        slope_c, intercept_c = np.polyfit(x_col, y_col, 1)
        line_x_c = np.linspace(x_col.min(), x_col.max(), 100)
        axes[1].plot(line_x_c, slope_c * line_x_c + intercept_c, color=palette["collision"], linewidth=2.5)

    col_text = f"N = {len(col_data)}\nSpearman ρ = {corr_col:.3f}\np = {p_val_col:.3f}" if not np.isnan(
        corr_col) else "undefined"
    axes[1].text(0.04, 0.96, col_text, transform=axes[1].transAxes, ha="left", va="top",
                 fontsize=11, bbox={"facecolor": "white", "edgecolor": "gray", "alpha": 0.8})

    axes[1].set_title("Perceived Obstacle-Avoidance vs. Collisions", fontsize=14, fontweight="bold")
    axes[1].set_xlabel("Q5 Rating (1-5)", fontsize=12)
    axes[1].set_ylabel("Final Number of Collisions", fontsize=12)
    axes[1].set_xticks([1, 2, 3, 4, 5])
    axes[1].set_xlim(0.5, 5.5)
    axes[1].set_ylim(bottom=-1)
    axes[1].grid(alpha=0.3, linestyle="--")

    # Finalize
    fig.tight_layout()
    fig.savefig('metacognition.pdf', format='pdf', bbox_inches='tight')
    plt.show()

    corr_df = pd.DataFrame(correlation_records)
    print("\nSpearman Correlation Results:")
    print(corr_df.round(3).to_string(index=False))


def plot_metacognitive_awareness_stacked(perception_results_all, experiment_logs_all, df_questionnaire_final):
    """
    Splits participants into exact halves based on Total Accuracy and Final Collisions,
    then plots how each group answered Q9 (Most challenging task) using stacked bar charts.
    """

    # --- 1. Q9 Data Mapping ---
    q9_mapping = {
        'cue localization': 'Localization',
        'localization': 'Localization',
        1: 'Localization',

        'avoidance': 'Avoidance',
        'obstacle avoidance': 'Avoidance',
        2: 'Avoidance',

        'both': 'Both',
        3: 'Both'
    }

    # --- 2. Data Extraction ---
    participant_names = list(perception_results_all.keys())
    questionnaire = df_questionnaire_final.reset_index(drop=True).copy()
    participant_records = []

    for idx, p_name in enumerate(participant_names):
        trials = perception_results_all[p_name].copy()
        exp_logs = experiment_logs_all[p_name].copy()

        # Calculate Total Accuracy
        trials['Perceived angle'] = pd.to_numeric(trials['Perceived angle'], errors='coerce')
        valid_trials = trials[trials['Perceived angle'].notna() & (trials['Perceived angle'] != -1)].copy()

        if len(valid_trials) > 0:
            hits = (valid_trials['Angle'] == valid_trials['Perceived angle']) & \
                   (valid_trials['Distance'] == valid_trials[
                       'Distance perceived' if 'Distance perceived' in valid_trials.columns else 'Perceived distance'])
            acc_tot = hits.sum() / len(valid_trials)
        else:
            acc_tot = np.nan

        # Calculate Final Collisions
        col_vals = pd.to_numeric(exp_logs["Number of collision"], errors="coerce").dropna()
        final_col = col_vals.iloc[-1] if not col_vals.empty else np.nan

        # Get Q9 Answer
        raw_q9 = questionnaire.loc[idx, "Q9"]
        if isinstance(raw_q9, str):
            raw_q9 = raw_q9.strip().lower()

        clean_q9 = q9_mapping.get(raw_q9, "Unknown")

        participant_records.append({
            "Participant ID": questionnaire.loc[idx, "Participant ID"],
            "Total Accuracy": acc_tot,
            "Final Collisions": final_col,
            "Q9 Response": clean_q9
        })

    df = pd.DataFrame(participant_records)
    df = df[df['Q9 Response'] != 'Unknown'].copy()

    # --- 3. Strict 50/50 Median Splits ---
    half_n = len(df) / 2

    # Accuracy Split
    df['Acc_Rank'] = df['Total Accuracy'].rank(method='first', ascending=True)
    df['Accuracy Group'] = np.where(df['Acc_Rank'] <= half_n, 'Lower Accuracy\n(Worse)', 'Higher Accuracy\n(Better)')

    # Collision Split
    df['Col_Rank'] = df['Final Collisions'].rank(method='first', ascending=True)
    df['Collision Group'] = np.where(df['Col_Rank'] <= half_n, 'Fewer Collisions\n(Better)', 'More Collisions\n(Worse)')

    # --- 4. Calculate Percentages & Pivot for Stacking ---
    def get_pivot_proportions(group_col):
        counts = df.groupby([group_col, 'Q9 Response']).size().reset_index(name='Count')
        totals = df.groupby(group_col).size().reset_index(name='Total')
        merged = pd.merge(counts, totals, on=group_col)
        merged['Percentage'] = (merged['Count'] / merged['Total']) * 100

        # Pivot so rows are Groups and columns are Q9 Responses
        pivot = merged.pivot(index=group_col, columns='Q9 Response', values='Percentage').fillna(0)

        # Ensure consistent column order
        cols = [c for c in ['Localization', 'Avoidance', 'Both'] if c in pivot.columns]
        return pivot[cols]

    acc_pivot = get_pivot_proportions('Accuracy Group')
    # Order the rows explicitly
    acc_pivot = acc_pivot.reindex(['Lower Accuracy\n(Worse)', 'Higher Accuracy\n(Better)'])

    col_pivot = get_pivot_proportions('Collision Group')
    col_pivot = col_pivot.reindex(['More Collisions\n(Worse)', 'Fewer Collisions\n(Better)'])

    # --- 5. Plotting Stacked Bars ---
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    q9_colors = ['#4C72B0', '#DD8452', '#8C8C8C']  # Blue for Loc, Orange for Avoid, Gray for Both

    # Subplot 1: Accuracy Split
    acc_pivot.plot(kind='bar', stacked=True, ax=axes[0], color=q9_colors, edgecolor='black', width=0.6)
    axes[0].set_title('Q9 Answers by Actual Accuracy', fontweight='bold', fontsize=14)
    axes[0].set_ylabel('Percentage of Participants (%)', fontweight='bold')
    axes[0].set_xlabel('')

    # Subplot 2: Collision Split
    col_pivot.plot(kind='bar', stacked=True, ax=axes[1], color=q9_colors, edgecolor='black', width=0.6)
    axes[1].set_title('Q9 Answers by Actual Collisions', fontweight='bold', fontsize=14)
    axes[1].set_ylabel('')
    axes[1].set_xlabel('')

    # Formatting and labels
    for ax in axes:
        ax.set_ylim(0, 100)
        ax.tick_params(axis='x', labelrotation=0)  # Keep X-axis text horizontal

        # Center the percentage text inside each stacked block
        for container in ax.containers:
            labels = [f'{v.get_height():.1f}%' if v.get_height() > 0 else '' for v in container]
            ax.bar_label(container, labels=labels, label_type='center', color='white', fontweight='bold', fontsize=10)

    # Clean up legends
    axes[0].get_legend().remove()
    axes[1].legend(title='Q9: "What was more challenging?"', title_fontsize=11,
                   fontsize=10, loc='upper left', bbox_to_anchor=(1.02, 1))

    plt.tight_layout()
    plt.savefig('metacognitive_awareness_stacked.pdf', format='pdf', bbox_inches='tight')
    plt.show()


def print_questionnaire_stats_and_pvalue(df_questionnaire_final):
    """
    Calculates mean and standard deviation for Q1, Q2, Q13, and Q15.
    Performs Mann-Whitney U and Wilcoxon signed-rank tests between Q1 and Q2.
    """
    # 1. Print Means and Standard Deviations
    target_columns = {
        'Q1': 'Mental workload',
        'Q2': 'Physical fatigue',
        'Q13': 'Felt immersed in VR',
        'Q14': 'Performing dual task was hard',
        'Q15': 'Avoidance harder w/ diff',
        'Q16': 'Localization harder w/ diff',
    }

    # Widened the table format slightly to accommodate the Q15 description
    print("=" * 65)
    print(f"{'Col':<5} | {'Description':<28} | {'Mean':<7} | {'Std Dev':<7}")
    print("-" * 65)

    for col, desc in target_columns.items():
        if col in df_questionnaire_final.columns:
            numeric_data = pd.to_numeric(df_questionnaire_final[col], errors='coerce').dropna()
            if not numeric_data.empty:
                print(f"{col:<5} | {desc:<28} | {numeric_data.mean():<7.2f} | {numeric_data.std():<7.2f}")
            else:
                print(f"{col:<5} | {desc:<28} | {'No data':<7} | {'No data':<7}")
        else:
            print(f"{col:<5} | {desc:<28} | {'Missing':<7} | {'Missing':<7}")

    print("=" * 65 + "\n")

    # 2. Statistical Testing (Q1 vs Q2)
    if 'Q1' in df_questionnaire_final.columns and 'Q2' in df_questionnaire_final.columns:
        # Create a clean dataframe with just Q1 and Q2, dropping rows where either is missing
        test_df = df_questionnaire_final[['Q1', 'Q2']].copy()
        test_df['Q1'] = pd.to_numeric(test_df['Q1'], errors='coerce')
        test_df['Q2'] = pd.to_numeric(test_df['Q2'], errors='coerce')
        test_df = test_df.dropna()

        q1_data = test_df['Q1']
        q2_data = test_df['Q2']

        if len(test_df) > 0:
            # Mann-Whitney U test (Unpaired - As requested)
            mw_stat, mw_p = mannwhitneyu(q1_data, q2_data, alternative='two-sided')

            # Wilcoxon signed-rank test (Paired - Recommended for within-subjects)
            w_stat, w_p = wilcoxon(q1_data, q2_data, alternative='two-sided')

            print("STATISTICAL COMPARISON: Mental Workload (Q1) vs Physical Fatigue (Q2)")
            print("-" * 75)
            print(f"Mann-Whitney U Test (Unpaired) : U = {mw_stat:<6.1f} | p-value = {mw_p:.4f}")
            print(f"Wilcoxon Signed-Rank (Paired)  : W = {w_stat:<6.1f} | p-value = {w_p:.4f}")
            print("-" * 75)
        else:
            print("Not enough valid paired data to perform statistical tests.")







