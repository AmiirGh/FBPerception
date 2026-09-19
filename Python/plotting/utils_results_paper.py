from utils import *


def plot_timing_metrics_unpaired(perception_results_all, color_palette, axes=None):
    """
    Plots response and reaction times.
    Also prints the top 5 highest reaction and response times across all modalities.
    """
    # 1. Safely combine data
    df_list = []
    for pid, df in perception_results_all.items():
        if df is not None and not df.empty:
            df_copy = df.copy()
            df_copy['Participant ID'] = pid
            df_list.append(df_copy)

    df_all = pd.concat(df_list, ignore_index=True)

    valid_df = df_all[~df_all['Perceived angle'].isin([0, -1])].copy()
    valid_df['Modality'] = valid_df['Modality'].str.lower()

    valid_df['Response time'] = valid_df['Response end'] - valid_df['Response start']
    valid_df['Reaction time'] = valid_df['Response start'] - valid_df['Phase timestamp']

    modality_order = ['visual', 'auditory', 'haptic']

    # Extract only the exact modality colors from the broader palette
    mod_palette = {mod: color_palette[mod] for mod in modality_order}

    standalone = axes is None
    if standalone:
        fig, axes = plt.subplots(1, 2, figsize=(12, 6))

    # --- Plot 1: Response Time ---
    sns.boxplot(data=valid_df, x='Modality', y='Response time', order=modality_order,
                palette=mod_palette, ax=axes[0], showfliers=False)

    axes[0].set_title('Response Time by Modality', fontweight='bold')
    axes[0].set_ylabel('Response Time (s)')

    # --- Plot 2: Reaction Time ---
    sns.boxplot(data=valid_df, x='Modality', y='Reaction time', order=modality_order,
                palette=mod_palette, ax=axes[1], showfliers=False)

    axes[1].set_title('Reaction Time by Modality', fontweight='bold')
    axes[1].set_ylabel('Reaction Time (s)')

    # --- Print Top 5 Longest Times ---
    print("\n" + "=" * 60)
    print("TOP 5 LONGEST REACTION TIMES ACROSS ALL MODALITIES")
    print("=" * 60)
    top_reaction = valid_df.nlargest(5, 'Reaction time')[
        ['Participant ID', 'Modality', 'Difficulty level', 'Reaction time']]
    print(top_reaction.to_string(index=False))

    print("\n" + "=" * 60)
    print("TOP 5 LONGEST RESPONSE TIMES ACROSS ALL MODALITIES")
    print("=" * 60)
    top_response = valid_df.nlargest(5, 'Response time')[
        ['Participant ID', 'Modality', 'Difficulty level', 'Response time']]
    print(top_response.to_string(index=False))
    print("=" * 60 + "\n")

    if standalone:
        plt.tight_layout()
        plt.show()


def plot_timing_metrics_unpaired(perception_results_all, color_palette, axes=None):
    """
    Plots response and reaction times.
    Calculates and shows Mann-Whitney U p-values for Reaction Time ONLY,
    comparing Visual vs Auditory and Visual vs Haptic.
    Also prints the top 5 highest reaction and response times across all modalities.
    """
    # 1. Safely combine data
    df_list = []
    for pid, df in perception_results_all.items():
        if df is not None and not df.empty:
            df_copy = df.copy()
            df_copy['Participant ID'] = pid
            df_list.append(df_copy)

    df_all = pd.concat(df_list, ignore_index=True)

    valid_df = df_all[~df_all['Perceived angle'].isin([0, -1])].copy()
    valid_df['Modality'] = valid_df['Modality'].str.lower()

    valid_df['Response time'] = valid_df['Response end'] - valid_df['Response start']
    valid_df['Reaction time'] = valid_df['Response start'] - valid_df['Phase timestamp']

    # Aggregate to subject-level means for the statistical test
    subject_means = valid_df.groupby(['Participant ID', 'Modality'])['Reaction time'].mean().reset_index()

    modality_order = ['visual', 'auditory', 'haptic']

    # Extract only the exact modality colors from the broader palette
    mod_palette = {mod: color_palette[mod] for mod in modality_order}

    standalone = axes is None
    if standalone:
        fig, axes = plt.subplots(1, 2, figsize=(12, 6))

    # --- Plot 1: Response Time (No Stats) ---
    sns.boxplot(data=valid_df, x='Modality', y='Response time', order=modality_order,
                palette=mod_palette, ax=axes[0], showfliers=False)

    axes[0].set_title('Response Time by Modality', fontweight='bold')
    axes[0].set_ylabel('Response Time (s)')

    # --- Plot 2: Reaction Time (With Stats) ---
    sns.boxplot(data=valid_df, x='Modality', y='Reaction time', order=modality_order,
                palette=mod_palette, ax=axes[1], showfliers=False)

    axes[1].set_title('Reaction Time by Modality (with p-values)', fontweight='bold')
    axes[1].set_ylabel('Reaction Time (s)')

    # --- Add Specific Annotations for Reaction Time ---
    pairs_to_test = [('visual', 'auditory'), ('visual', 'haptic')]
    num_comparisons = len(pairs_to_test)

    print(f"\n--- Calculating Unpaired P-Values for Reaction time ---")

    # Determine base height using the actual data being plotted (ignoring outliers)
    max_val = valid_df['Reaction time'].quantile(0.95)
    y_base = max_val * 1.1
    y_step = max_val * 0.15

    for i, (mod1, mod2) in enumerate(pairs_to_test):
        group1 = subject_means[subject_means['Modality'] == mod1]['Reaction time'].dropna()
        group2 = subject_means[subject_means['Modality'] == mod2]['Reaction time'].dropna()

        if group1.empty or group2.empty:
            print(f"Skipping {mod1} vs {mod2} (Empty group detected)")
            continue

        # Mann-Whitney U test
        stat, raw_p = mannwhitneyu(group1, group2, alternative='two-sided')
        bonferroni_p = min(raw_p * num_comparisons, 1.0)

        print(f"{mod1.capitalize()} vs {mod2.capitalize()}: Raw p={raw_p:.5f}, Bonferroni p={bonferroni_p:.5f}")

        if bonferroni_p < 0.001:
            p_text = "p < 0.001"
        elif bonferroni_p < 0.05:
            p_text = f"p = {bonferroni_p:.3f}"
        else:
            p_text = f"p = {bonferroni_p:.2f}"

        x1 = modality_order.index(mod1)
        x2 = modality_order.index(mod2)

        y = y_base + (i * y_step)
        h = max_val * 0.03

        # Draw brackets with high zorder to prevent being hidden by grid/boxplots
        axes[1].plot([x1, x1, x2, x2], [y, y + h, y + h, y], lw=1.5, color='black', zorder=10)

        weight = 'bold' if bonferroni_p < 0.05 else 'normal'
        axes[1].text((x1 + x2) * 0.5, y + h + (max_val * 0.02), p_text,
                     ha='center', va='bottom', color='black', fontsize=10, fontweight=weight, zorder=10)

    # Set limits dynamically so the brackets are never cut off (minimum y-limit of 6.0)
    highest_bracket = y_base + (len(pairs_to_test) * y_step)
    axes[1].set_ylim([0, max(6.0, highest_bracket * 1.15)])

    # --- Print Top 5 Longest Times ---
    print("\n" + "=" * 60)
    print("TOP 5 LONGEST REACTION TIMES ACROSS ALL MODALITIES")
    print("=" * 60)
    top_reaction = valid_df.nlargest(5, 'Reaction time')[
        ['Participant ID', 'Modality', 'Difficulty level', 'Reaction time']]
    print(top_reaction.to_string(index=False))

    print("\n" + "=" * 60)
    print("TOP 5 LONGEST RESPONSE TIMES ACROSS ALL MODALITIES")
    print("=" * 60)
    top_response = valid_df.nlargest(5, 'Response time')[
        ['Participant ID', 'Modality', 'Difficulty level', 'Response time']]
    print(top_response.to_string(index=False))
    print("=" * 60 + "\n")

    if standalone:
        plt.tight_layout()
        plt.show()




def plot_misses_grouped_box(subjects_data_trials, color_palette):
    """
    Calculates the total missed trials per subject and plots them grouped by difficulty, separated by modality.
    """
    records = []

    for subject_id, df in subjects_data_trials.items():
        # Identify missed trials
        df_copy = df.copy()
        df_copy['is_miss'] = df_copy['Perceived angle'].isin([0, -1])

        # Count misses per difficulty and modality for this subject
        misses_agg = df_copy.groupby(['Difficulty level', 'Modality'])['is_miss'].sum().reset_index()
        misses_agg['Subject'] = subject_id

        records.extend(misses_agg.to_dict('records'))

    misses_df = pd.DataFrame(records)

    difficulty_order = ['easy', 'medium', 'hard']
    modality_order = ['visual', 'auditory', 'haptic']

    plt.figure(figsize=(10, 6))

    sns.boxplot(data=misses_df, x='Difficulty level', y='is_miss', hue='Modality', order=difficulty_order,
                hue_order=modality_order, palette=color_palette, showfliers=False)

    plt.title('Missed Trials Distribution by Difficulty and Modality')
    plt.ylabel('Number of Misses (per subject)')
    plt.xlabel('Difficulty')
    plt.legend(title='Modality')
    plt.ylim([0, 15])
    plt.tight_layout()
    plt.show()


def compute_error_by_modality_temp(subjects_data_trials):
    all_results = []
    miss_records = []

    # Iterate through the dictionary unpacking the subject name and their dataframe
    for subject_name, df in subjects_data_trials.items():
        df = df.copy()

        # 1. Remove hardware/setup faults (-1) first
        df = df[df['Perceived angle'] != -1]

        # 2. Calculate Miss Rates/Counts BEFORE filtering out 0s
        for mod in df['Modality'].unique():
            mod_df = df[df['Modality'] == mod]
            total_trials = len(mod_df)

            if total_trials > 0:
                misses = (mod_df['Perceived angle'] == 0).sum()
                miss_rate = misses / total_trials

                miss_records.append({
                    'Participant ID': subject_name,
                    'Modality': mod,
                    'Miss_count': misses,
                    'Miss_rate': miss_rate
                })

        # 3. Now remove misses (0) to calculate angular/distance errors on valid hits
        valid_df = df[df['Perceived angle'] != 0].copy()

        if not valid_df.empty:
            # Angle error (circular: max distance on an 8-point circle is 4)
            diff = np.abs(valid_df['Angle'] - valid_df['Perceived angle'])
            valid_df['Angle error'] = np.minimum(diff, 8 - diff)

            # Distance error (linear)
            valid_df['Distance error'] = np.abs(valid_df['Distance'] - valid_df['Perceived distance'])

            # Record the Participant ID directly from the dictionary key
            valid_df['Participant ID'] = subject_name

            # Append using the correctly mapped column names
            all_results.append(valid_df[['Participant ID', 'Modality', 'Angle error', 'Distance error']])

    # Safety check if no valid data remains
    if not all_results:
        print("No valid error data found after filtering.")
        return pd.DataFrame(), pd.DataFrame()

    combined = pd.concat(all_results, ignore_index=True)
    miss_df = pd.DataFrame(miss_records)

    # =====================================================================
    # --- A. PER-SUBJECT DISTRIBUTIONS ---
    # =====================================================================

    # Group by BOTH modality and Participant ID
    angle_counts_dist = (
        combined.groupby(['Modality', 'Participant ID'])['Angle error']
        .value_counts()
        .unstack(fill_value=0)
        .reindex(columns=range(5), fill_value=0)
    )
    angle_counts_dist.columns = [f"Angle_err_{i}" for i in angle_counts_dist.columns]

    dist_counts_dist = (
        combined.groupby(['Modality', 'Participant ID'])['Distance error']
        .value_counts()
        .unstack(fill_value=0)
        .reindex(columns=range(3), fill_value=0)
    )
    dist_counts_dist.columns = [f"Dist_err_{i}" for i in dist_counts_dist.columns]

    # Combine into the distribution dataframe
    subject_distributions = angle_counts_dist.join(dist_counts_dist).reset_index()

    # Merge the Miss records into the subject distributions
    subject_distributions = pd.merge(
        subject_distributions,
        miss_df,
        on=['Modality', 'Participant ID'],
        how='outer'
    ).fillna(0)

    # =====================================================================
    # --- B. OVERALL AGGREGATE ---
    # =====================================================================

    overall_results = (
        subject_distributions
        .drop(columns=['Participant ID'])
        .groupby('Modality')
        .sum()
        .reset_index()
    )

    # Weighted mean Angle error
    angle_cols = [f"Angle_err_{i}" for i in range(5)]
    angle_weights = np.array(range(5))
    overall_results['weighted_mean_Angle_err'] = ((overall_results[angle_cols].values @ angle_weights)
                                                  / overall_results[angle_cols].sum(axis=1))

    # Weighted mean Distance error
    dist_cols = [f"Dist_err_{i}" for i in range(3)]
    dist_weights = np.array(range(3))
    overall_results['weighted_mean_Dist_err'] = ((overall_results[dist_cols].values @ dist_weights)
                                                 / overall_results[dist_cols].sum(axis=1))

    # Recalculate overall miss rate across all subjects
    overall_results['Overall_Miss_Rate'] = overall_results['Miss_count'] / overall_results[angle_cols].sum(axis=1)

    return overall_results, subject_distributions


def plot_error_boxplots_temp(error_distribution, color_palette, ax=None):
    """Plots the distribution of misses, angular errors, and radial distance errors.

    If `ax` is provided, the plot is drawn onto that Axes instead of creating
    a new figure, allowing this function to be embedded in a larger dashboard.
    """

    if error_distribution is None or error_distribution.empty:
        return

    standalone = ax is None

    sns.set_theme(style="whitegrid")

    # Isolate columns to plot (ignoring 0 errors since they represent perfect hits)
    angle_cols = [col for col in error_distribution.columns if col.startswith('Angle_err_') and col != 'Angle_err_0']
    dist_cols = [col for col in error_distribution.columns if col.startswith('Dist_err_') and col != 'Dist_err_0']

    # Add Miss_count at the very beginning of the list
    all_cols = ['Miss_count'] + angle_cols + dist_cols

    melted_df = error_distribution.melt(
        id_vars=['Participant ID', 'Modality'],
        value_vars=all_cols,
        var_name='error_type',
        value_name='count'
    )

    # Map the backend column names to clean, readable labels for the X-axis
    label_mapping = {
        'Miss_count': 'Misse rate',
        **{col: col.replace('Angle_err_', 'Angle error: ') for col in angle_cols},
        **{col: col.replace('Dist_err_', 'Distance error: ') for col in dist_cols}
    }
    melted_df['error_type'] = melted_df['error_type'].map(label_mapping)

    # Standardize modality names for plotting
    melted_df['Modality'] = melted_df['Modality'].str.lower()

    # Define the new modality order
    modality_order = ['auditory', 'haptic', 'visual']

    if standalone:
        fig, ax = plt.subplots(figsize=(14, 6))

    sns.boxplot(
        data=melted_df,
        x='error_type',
        y='count',
        hue='Modality',
        hue_order=modality_order,
        palette=color_palette,
        ax=ax
    )

    ax.set_ylabel("Count (per subject)", fontweight='bold')
    ax.set_xlabel("")

    # Force Y-axis to show integer ticks only
    ax.yaxis.set_major_locator(mtick.MaxNLocator(integer=True))

    plt.xticks(rotation=45, ha='right')

    ax.legend(title='Modality', bbox_to_anchor=(1.01, 1), loc='upper left')

    # Add subtle vertical lines to separate Misses, Angular, and Distance categories visually
    ax.axvline(0.5, color='gray', linestyle=':', alpha=0.7)
    ax.axvline(4.5, color='gray', linestyle=':', alpha=0.7)

    if standalone:
        plt.tight_layout()
        plt.show()


def compute_error_by_modality(subjects_data_trials):
    all_results = []

    # Iterate through the dictionary unpacking the subject name and their dataframe
    for subject_name, df in subjects_data_trials.items():
        df = df.copy()

        # Remove invalid perceived values (0 = miss, -1 = setup miss)
        df = df[(df['Perceived angle'] != 0) & (df['Perceived angle'] != -1)]

        # Angle error (circular: max distance on an 8-point circle is 4)
        diff = np.abs(df['Angle'] - df['Perceived angle'])
        df['Angle error'] = np.minimum(diff, 8 - diff)

        # Distance error (linear)
        df['Distance error'] = np.abs(df['Distance'] - df['Perceived distance'])

        # Record the Participant ID directly from the dictionary key
        df['Participant ID'] = subject_name

        # Append using the correctly mapped column names
        # Note: If your dataframe uses 'Modality' instead of 'feedback_modality', change it here!
        all_results.append(df[['Participant ID', 'Modality', 'Angle error', 'Distance error']])

    # Safety check if no valid data remains
    if not all_results:
        print("No valid error data found after filtering.")
        return pd.DataFrame(), pd.DataFrame()

    combined = pd.concat(all_results, ignore_index=True)

    # =====================================================================
    # --- A. PER-SUBJECT DISTRIBUTIONS ---
    # =====================================================================

    # Group by BOTH modality and Participant ID
    angle_counts_dist = (
        combined.groupby(['Modality', 'Participant ID'])['Angle error']
        .value_counts()
        .unstack(fill_value=0)
        .reindex(columns=range(5), fill_value=0)
    )
    angle_counts_dist.columns = [f"Angle_err_{i}" for i in angle_counts_dist.columns]

    dist_counts_dist = (
        combined.groupby(['Modality', 'Participant ID'])['Distance error']
        .value_counts()
        .unstack(fill_value=0)
        .reindex(columns=range(3), fill_value=0)
    )
    dist_counts_dist.columns = [f"Dist_err_{i}" for i in dist_counts_dist.columns]

    # Combine into the distribution dataframe
    subject_distributions = angle_counts_dist.join(dist_counts_dist).reset_index()

    # =====================================================================
    # --- B. OVERALL AGGREGATE ---
    # =====================================================================

    # We can efficiently get the overall sums by grouping the subject distributions
    overall_results = (
        subject_distributions
        .drop(columns=['Participant ID'])
        .groupby('Modality')
        .sum()
        .reset_index()
    )

    # Weighted mean Angle error
    angle_cols = [f"Angle_err_{i}" for i in range(5)]
    angle_weights = np.array(range(5))

    overall_results['weighted_mean_Angle_err'] = ((overall_results[angle_cols].values @ angle_weights)
                                                / overall_results[angle_cols].sum(axis=1))

    # Weighted mean Distance error
    dist_cols = [f"Dist_err_{i}" for i in range(3)]
    dist_weights = np.array(range(3))

    overall_results['weighted_mean_Dist_err'] = (
                                                   overall_results[dist_cols].values @ dist_weights
                                               ) / overall_results[dist_cols].sum(axis=1)

    return overall_results, subject_distributions


def test_wickens_with_task_shedding(perception_results_all, experiment_logs_all):
    """
    Evaluates Wickens' Theory by including "task shedding" (missed cues).
    Calculates Miss Rate, Reaction Delay (valid only), and Collision Rates.
    """
    all_trials_list = []

    for subject_id, perc_df in perception_results_all.items():
        logs_df = experiment_logs_all.get(subject_id)
        if logs_df is None:
            continue

        # Filter out hardware faults (-1), keep valid (>0) and missed (0)
        analysis_trials = perc_df[
            (perc_df['Perceived angle'] >= 0) &
            (perc_df['Modality'].isin(['visual', 'auditory', 'haptic']))
            ].copy()

        # Create a boolean column for Missed Cues
        analysis_trials['Is_Missed'] = analysis_trials['Perceived angle'] == 0

        # 1. Calculate Reaction Delay (Only for valid responses, NaN for missed)
        analysis_trials['Reaction_Delay'] = np.where(
            analysis_trials['Is_Missed'],
            np.nan,
            analysis_trials['Response start'] - analysis_trials['Phase timestamp']
        )

        # 2. Calculate Collisions during the cue window
        collisions_during_cue = []

        for _, trial in analysis_trials.iterrows():
            t_start = trial['Timestamp']

            if trial['Is_Missed']:
                # If missed, we don't have a 'Response end'.
                # We look at a standard 4-second window (2s cue + 2s buffer)
                t_end = t_start + 4.0
            else:
                # If valid, look at the exact response window
                time_spent = trial['Response end'] - trial['Phase timestamp']
                t_end = t_start + time_spent

            # Slice the 10Hz logs for this specific time window
            window_logs = logs_df[(logs_df['Timestamp'] >= t_start) & (logs_df['Timestamp'] <= t_end)]

            if not window_logs.empty:
                colls = window_logs['Number of collision'].max() - window_logs['Number of collision'].min()
            else:
                colls = 0

            collisions_during_cue.append(colls)

        analysis_trials['Collisions_During_Window'] = collisions_during_cue
        analysis_trials['Subject_ID'] = subject_id

        all_trials_list.append(analysis_trials)

    # Combine all processed subject data
    df_combined = pd.concat(all_trials_list, ignore_index=True)

    # Generate summary statistics grouped by Modality
    summary_stats = df_combined.groupby('Modality').agg(
        Total_Trials=('Is_Missed', 'count'),
        Miss_Rate_Percent=('Is_Missed', lambda x: (x.mean() * 100).round(2)),
        Mean_Delay_Valid=('Reaction_Delay', 'mean'),
        Collisions_Valid=('Collisions_During_Window', lambda x: x[~df_combined.loc[x.index, 'Is_Missed']].mean()),
        Collisions_Missed=('Collisions_During_Window', lambda x: x[df_combined.loc[x.index, 'Is_Missed']].mean())
    ).reset_index()

    print("--- Wickens' Theory: Task Shedding Analysis ---")
    print(summary_stats.to_string(index=False))

    return df_combined, summary_stats


def test_cross_modal_mapping_cost(perception_results_all):
    """
    Evaluates the cognitive cost of cross-modal spatial mapping (Auditory/Haptic)
    compared to direct unimodal mapping (Visual) by analyzing reaction delays.
    """
    all_trials_list = []

    for subject_id, perc_df in perception_results_all.items():
        # Filter for valid trials only (ignoring missed '0' or invalidated '-1')
        valid_trials = perc_df[
            (perc_df['Perceived angle'] > 0) &
            (perc_df['Modality'].isin(['visual', 'auditory', 'haptic']))
            ].copy()

        # 1. Calculate Reaction Delay (Speed of perception)
        valid_trials['Reaction_Delay'] = valid_trials['Response start'] - valid_trials['Phase timestamp']

        # 2. Categorize the Mapping Type
        # Visual is unimodal (visual cue -> visual space)
        # Auditory and Haptic are cross-modal (ego-centric cue -> visual space)
        valid_trials['Mapping_Type'] = np.where(
            valid_trials['Modality'] == 'visual',
            'Unimodal (Visual)',
            'Cross-modal (Auditory/Haptic)'
        )

        valid_trials['Subject_ID'] = subject_id
        all_trials_list.append(valid_trials)

    # Combine all processed subject data into a single DataFrame
    df_combined = pd.concat(all_trials_list, ignore_index=True)

    # Generate high-level summary statistics grouped by Mapping Type
    summary_stats = df_combined.groupby('Mapping_Type').agg(
        Mean_Delay_Seconds=('Reaction_Delay', 'mean'),
        Std_Delay=('Reaction_Delay', 'std'),
        Total_Valid_Trials=('Reaction_Delay', 'count')
    ).reset_index()

    # Generate a detailed breakdown just to ensure Haptic and Auditory behave similarly
    detailed_stats = df_combined.groupby(['Mapping_Type', 'Modality']).agg(
        Mean_Delay_Seconds=('Reaction_Delay', 'mean'),
        Std_Delay=('Reaction_Delay', 'std')
    ).reset_index()

    print("--- Cognitive Cost of Cross-Modal Spatial Mapping ---")
    print(summary_stats.to_string(index=False))
    print("\n--- Detailed Breakdown by Modality ---")
    print(detailed_stats.to_string(index=False))

    return df_combined, summary_stats, detailed_stats



def test_perceptual_tunneling(perception_results_all, color_palette):
    """
    Evaluates non-uniform perceptual tunneling by tracking Miss Rates
    and Angular Accuracy across changing difficulty levels.
    """
    all_trials_list = []

    for subject_id, perc_df in perception_results_all.items():
        # Filter out hardware faults (-1), keep valid (>0) and missed (0)
        analysis_trials = perc_df[
            (perc_df['Perceived angle'] >= 0) &
            (perc_df['Modality'].isin(['visual', 'auditory', 'haptic']))
            ].copy()

        # Create a boolean column for Missed Cues
        analysis_trials['Is_Missed'] = analysis_trials['Perceived angle'] == 0

        # Calculate Circular Angular Error (1 to 8 positions)
        # We only calculate this for valid responses; missed will be NaN
        def calc_angular_error(row):
            if row['Is_Missed']:
                return np.nan

            diff = abs(row['Angle'] - row['Perceived angle'])
            # The shortest distance around the 8-position circle
            return min(diff, 8 - diff)

        analysis_trials['Angular_Error'] = analysis_trials.apply(calc_angular_error, axis=1)

        # Ensure difficulty level names are standardized for grouping
        analysis_trials['Difficulty level'] = analysis_trials['Difficulty level'].str.lower()
        analysis_trials['Subject_ID'] = subject_id

        all_trials_list.append(analysis_trials)

    # Combine all processed subject data
    df_combined = pd.concat(all_trials_list, ignore_index=True)

    # Generate summary statistics grouped by Difficulty Level and Modality
    summary_stats = df_combined.groupby(['Difficulty level', 'Modality']).agg(
        Total_Trials=('Is_Missed', 'count'),
        Miss_Rate_Percent=('Is_Missed', lambda x: (x.mean() * 100).round(2)),
        Mean_Angular_Error=('Angular_Error', lambda x: x.mean().round(3)),
        Std_Angular_Error=('Angular_Error', lambda x: x.std().round(3))
    ).reset_index()

    # Reorder the output so it reads logically: Easy -> Medium -> Hard
    difficulty_order = {'easy': 1, 'medium': 2, 'hard': 3}
    summary_stats['Sort_Key'] = summary_stats['Difficulty level'].map(difficulty_order)
    summary_stats = summary_stats.sort_values(by=['Sort_Key', 'Modality']).drop(columns=['Sort_Key'])

    print("--- Detailed Perceptual Tunneling Statistics ---")
    print(summary_stats.to_string(index=False))

    # Create a pivot table specifically to see the interaction effect on Miss Rate
    miss_rate_pivot = summary_stats.pivot(index='Difficulty level', columns='Modality', values='Miss_Rate_Percent')
    miss_rate_pivot = miss_rate_pivot.reindex(['easy', 'medium', 'hard'])

    print("\n--- Miss Rate Interaction Table (%) ---")
    print(miss_rate_pivot.to_string())
    data = {
        'Difficulty': ['Easy', 'Medium', 'Hard', 'Easy', 'Medium', 'Hard', 'Easy', 'Medium', 'Hard'],
        'Modality': ['Visual', 'Visual', 'Visual', 'Auditory', 'Auditory', 'Auditory', 'Haptic', 'Haptic', 'Haptic'],
        'Miss_Rate': [12.18, 14.41, 17.40, 0.70, 0.32, 1.32, 0.16, 0.62, 0.88]
    }
    df_plot = pd.DataFrame(data)

    # Set up publication-style formatting
    sns.set_theme(style="whitegrid", context="paper", font_scale=1.2)
    plt.figure(figsize=(8, 6))

    # Define distinct colors and markers, using the shared modality palette
    palette = {mod.capitalize(): color for mod, color in color_palette.items()}
    markers = {'Visual': 'o', 'Auditory': 's', 'Haptic': '^'}

    # Create the interaction plot
    ax = sns.pointplot(
        data=df_plot,
        x='Difficulty',
        y='Miss_Rate',
        hue='Modality',
        palette=palette,
        markers=[markers[m] for m in palette.keys()],
        linestyles=['-', '--', '-.'],
        scale=1.5
    )

    # Formatting the axes and labels
    plt.title('Non-Uniform Perceptual Tunneling: Miss Rate by Difficulty', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Phase Difficulty Level', fontsize=12, fontweight='bold')
    plt.ylabel('Miss Rate (%)', fontsize=12, fontweight='bold')

    # Customize the legend
    plt.legend(title='Cue Modality', title_fontsize='11', fontsize='10', frameon=True, shadow=True)

    # Set y-axis limits to give the top line some breathing room
    plt.ylim(-1, 20)

    plt.tight_layout()
    plt.show()
    test_significance_within_modalities(df_combined)
    return df_combined, summary_stats, miss_rate_pivot


def test_significance_within_modalities(df_combined):
    """Runs Friedman and forces pairwise Wilcoxon tests across all difficulties for each individual modality."""

    subject_rates = df_combined.groupby(['Subject_ID', 'Modality', 'Difficulty level'])[
        'Is_Missed'].mean().reset_index()

    for modality in ['visual', 'auditory', 'haptic']:
        print(f"\n=========================================")
        print(f"Modality: {modality.upper()}")
        print(f"=========================================")

        mod_data = subject_rates[subject_rates['Modality'] == modality]

        easy = mod_data[mod_data['Difficulty level'] == 'easy'].sort_values('Subject_ID')['Is_Missed'].values
        medium = mod_data[mod_data['Difficulty level'] == 'medium'].sort_values('Subject_ID')['Is_Missed'].values
        hard = mod_data[mod_data['Difficulty level'] == 'hard'].sort_values('Subject_ID')['Is_Missed'].values

        if len(easy) == 0 or len(easy) != len(medium) or len(easy) != len(hard):
            print("Error: Incomplete paired data for subjects.")
            continue

        # Overall test
        try:
            f_stat, f_p = friedmanchisquare(easy, medium, hard)
            print(f"Friedman Test (Overall): Stat={f_stat:.3f}, p-value={f_p:.4f}\n")
        except Exception as e:
            print(f"Friedman Test failed: {e}\n")

        # Force pairwise Wilcoxon tests regardless of Friedman outcome
        print("Pairwise Wilcoxon Tests (Bonferroni-corrected alpha = 0.0167):")

        pairs = [('Easy vs Medium', easy, medium),
                 ('Medium vs Hard', medium, hard),
                 ('Easy vs Hard', easy, hard)]

        for label, dist1, dist2 in pairs:
            if np.array_equal(dist1, dist2):
                print(f"  {label}: p=1.0000 (Identical distributions)")
            else:
                try:
                    # 'pratt' handles zero-differences gracefully when many subjects have 0 misses in both phases
                    _, p_val = wilcoxon(dist1, dist2, zero_method='pratt')
                    sig_label = '(Significant)' if p_val < 0.0167 else '(Not Significant)'
                    print(f"  {label}: p={p_val:.4f} {sig_label}")
                except Exception as e:
                    print(f"  {label}: Could not calculate ({e})")



def test_speed_accuracy_tradeoffs(perception_results_all):
    """
    Evaluates speed-accuracy trade-offs by mapping Reaction Delay (Speed)
    against Angular Error (Accuracy) across different sensory modalities.
    """
    all_trials_list = []

    for subject_id, perc_df in perception_results_all.items():
        # Filter for valid trials only (ignoring missed '0' or invalidated '-1')
        valid_trials = perc_df[
            (perc_df['Perceived angle'] > 0) &
            (perc_df['Modality'].isin(['visual', 'auditory', 'haptic']))
            ].copy()

        # 1. Calculate Reaction Delay (Speed)
        valid_trials['Reaction_Delay'] = valid_trials['Response start'] - valid_trials['Phase timestamp']

        # 2. Calculate Circular Angular Error (Accuracy)
        # 0 = Perfect, 4 = Completely opposite direction
        def calc_angular_error(row):
            diff = abs(row['Angle'] - row['Perceived angle'])
            return min(diff, 8 - diff)

        valid_trials['Angular_Error'] = valid_trials.apply(calc_angular_error, axis=1)
        valid_trials['Subject_ID'] = subject_id

        all_trials_list.append(valid_trials)

    # Combine all processed subject data
    df_combined = pd.concat(all_trials_list, ignore_index=True)

    # Calculate Spearman correlation for each modality
    # (Spearman is used instead of Pearson because Angular Error is ordinal/discrete)
    print("--- Speed-Accuracy Correlation (Spearman's Rho) ---")
    for mod in ['visual', 'auditory', 'haptic']:
        subset = df_combined[df_combined['Modality'] == mod].dropna(subset=['Reaction_Delay', 'Angular_Error'])
        rho, p_val = spearmanr(subset['Reaction_Delay'], subset['Angular_Error'])
        print(f"{mod.capitalize()}: rho = {rho:.3f}, p-value = {p_val:.4f}")

    # Generate the 2D Density Plot
    plot_speed_accuracy_density(df_combined)

    return df_combined


def plot_speed_accuracy_density(df, color_palette):
    """
    Generates a faceted 2D KDE contour plot to visualize the density
    of speed (Reaction Delay) vs. accuracy (Angular Error) for each modality.
    """
    # Create a copy to avoid altering the original dataframe's casing
    plot_df = df.copy()
    plot_df['Modality'] = plot_df['Modality'].str.capitalize()

    # Set publication-ready theme
    sns.set_theme(style="whitegrid", context="paper", font_scale=1.2)

    # Define a distinct color palette for the modalities, using the shared palette
    palette = {mod.capitalize(): color for mod, color in color_palette.items()}

    # Create a FacetGrid for side-by-side subplots
    g = sns.FacetGrid(plot_df, col="Modality", hue="Modality", palette=palette, height=5, aspect=1)

    # Map the 2D KDE plot to each facet
    # We clip the y-axis to (0, 4) since angular error cannot physically exceed 4
    g.map(sns.kdeplot, "Reaction_Delay", "Angular_Error",
          fill=True, thresh=0.05, levels=8, alpha=0.7,
          clip=((-np.inf, np.inf), (0, 4)))

    # Format the axes and titles
    g.set_axis_labels("Reaction Delay (Seconds)\n[Speed]", "Absolute Angular Error\n[Accuracy]")
    g.set_titles(col_template="{col_name} Modality", fontweight='bold')

    # Force the Y-axis to show only the possible discrete error steps
    for ax in g.axes.flat:
        ax.set_yticks([0, 1, 2, 3, 4])


    # Adjust layout and add a main title
    plt.subplots_adjust(top=0.85)
    g.figure.suptitle('Speed-Accuracy Density by Sensory Channel', fontsize=16, fontweight='bold')

    plt.show()



def test_depth_perception_limits(perception_results_all):
    """
    Evaluates the absolute limits of non-visual depth perception by generating
    normalized confusion matrices for True Distance vs. Perceived Distance.
    """
    all_trials_list = []

    for subject_id, perc_df in perception_results_all.items():
        # Filter for valid trials where a distance was actually perceived and logged
        valid_trials = perc_df[
            (perc_df['Perceived distance'] > 0) &
            (perc_df['Distance'] > 0) &
            (perc_df['Modality'].isin(['visual', 'auditory', 'haptic']))
            ].copy()

        valid_trials['Subject_ID'] = subject_id
        all_trials_list.append(valid_trials)

    # Combine all processed subject data
    df_combined = pd.concat(all_trials_list, ignore_index=True)

    # Map the numerical distance values to readable labels
    dist_mapping = {1: 'Near', 2: 'Mid', 3: 'Far'}
    df_combined['True_Distance'] = df_combined['Distance'].map(dist_mapping)
    df_combined['Perceived_Distance'] = df_combined['Perceived distance'].map(dist_mapping)

    # Enforce categorical ordering so the matrices plot logically (Near -> Mid -> Far)
    cat_order = ['Near', 'Mid', 'Far']
    df_combined['True_Distance'] = pd.Categorical(df_combined['True_Distance'], categories=cat_order, ordered=True)
    df_combined['Perceived_Distance'] = pd.Categorical(df_combined['Perceived_Distance'], categories=cat_order,
                                                       ordered=True)

    # Print raw accuracy scores
    print("--- Overall Depth Perception Accuracy ---")
    for mod in ['visual', 'auditory', 'haptic']:
        subset = df_combined[df_combined['Modality'] == mod]
        correct = (subset['True_Distance'] == subset['Perceived_Distance']).sum()
        total = len(subset)
        print(f"{mod.capitalize()}: {(correct / total) * 100:.2f}% ({correct}/{total})")

    # Generate Publication-Ready Confusion Matrices
    plot_depth_confusion_matrices(df_combined, cat_order)

    return df_combined




def plot_depth_confusion_matrices(df, labels):
    """
    Generates side-by-side normalized heatmaps to visualize the depth confusion.
    """
    modalities = ['Visual', 'Auditory', 'Haptic']
    df['Modality'] = df['Modality'].str.capitalize()

    sns.set_theme(style="white", context="paper", font_scale=1.2)
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)

    for i, mod in enumerate(modalities):
        subset = df[df['Modality'] == mod]

        # Create a cross-tabulation (confusion matrix) and normalize by row (True Distance)
        cm = pd.crosstab(subset['True_Distance'], subset['Perceived_Distance'], normalize='index') * 100

        # Plot the heatmap
        sns.heatmap(
            cm,
            annot=True,
            fmt=".1f",
            cmap="Blues" if mod == 'Visual' else ("Greens" if mod == 'Auditory' else "Reds"),
            cbar=False,
            vmin=0,
            vmax=100,
            ax=axes[i],
            square=True,
            linewidths=.5,
            annot_kws={"weight": "bold"}
        )

        axes[i].set_title(f"{mod} Modality", fontweight='bold', pad=15)
        axes[i].set_xlabel('Perceived Distance\n(User Response)', fontweight='bold')
        if i == 0:
            axes[i].set_ylabel('True Distance\n(System Generated)', fontweight='bold')
        else:
            axes[i].set_ylabel('')

    plt.suptitle('Limits of Depth Perception: Confusion Matrices by Modality (%)', fontsize=16, fontweight='bold',
                 y=1.05)
    plt.tight_layout()
    plt.show()


def analyze_spatial_anisotropy(perception_results_all):
    """
    Analyzes spatial anisotropy by plotting mean angular error
    across all 8 angles for each modality.
    """
    all_trials = []
    for subject_id, perc_df in perception_results_all.items():
        # Keep only valid trials
        valid = perc_df[perc_df['Perceived angle'] > 0].copy()

        # Calculate circular angular error
        diff = abs(valid['Angle'] - valid['Perceived angle'])
        valid['Error'] = np.minimum(diff, 8 - diff)

        all_trials.append(valid)

    df = pd.concat(all_trials, ignore_index=True)

    # Calculate mean error per modality and angle
    anisotropy_df = df.groupby(['Modality', 'Angle'])['Error'].mean().reset_index()

    # Pivot for heatmap
    heatmap_data = anisotropy_df.pivot(index='Modality', columns='Angle', values='Error')

    # Plotting
    plt.figure(figsize=(12, 6))
    sns.heatmap(heatmap_data, annot=True, cmap="coolwarm", fmt=".2f", cbar_kws={'label': 'Mean Angular Error'})
    plt.title("Spatial Anisotropy: Mean Angular Error by Angle and Modality", fontsize=16)
    plt.ylabel("Modality")
    plt.xlabel("Spatial Cue Angle (1-8)")
    plt.show()

    return anisotropy_df


def analyze_motor_cognitive_interference(perception_results_all, experiment_logs_all):
    """
    Analyzes whether high joystick activity (motor effort) correlates with
    increased reaction delays (cognitive spatial decoding interference).
    """
    all_trials_list = []

    for subject_id, perc_df in perception_results_all.items():
        logs_df = experiment_logs_all.get(subject_id)
        if logs_df is None: continue

        # Get valid trials only
        valid_trials = perc_df[perc_df['Perceived angle'] > 0].copy()
        valid_trials['Reaction_Delay'] = valid_trials['Response start'] - valid_trials['Phase timestamp']

        # Calculate motor effort during the cue window
        motor_effort = []
        for _, trial in valid_trials.iterrows():
            t_start = trial['Timestamp']
            # Window: cue onset to 2 seconds after (or until response)
            t_end = t_start + 2.0

            # Slice logs
            window = logs_df[(logs_df['Timestamp'] >= t_start) & (logs_df['Timestamp'] <= t_end)]

            # Motor Effort = Total Euclidean distance of joystick movement
            if not window.empty:
                dx = window['Thumbstick x'].diff().abs().sum()
                dy = window['Thumbstick y'].diff().abs().sum()
                motor_effort.append(dx + dy)
            else:
                motor_effort.append(0)

        valid_trials['Motor_Effort'] = motor_effort
        valid_trials['Subject_ID'] = subject_id
        all_trials_list.append(valid_trials)

    df = pd.concat(all_trials_list, ignore_index=True)

    # Plotting
    plt.figure(figsize=(10, 6))
    sns.regplot(data=df, x='Motor_Effort', y='Reaction_Delay',
                scatter_kws={'alpha': 0.3}, line_kws={'color': 'red'})
    plt.title("Motor-Cognitive Interference: Joystick Effort vs. Reaction Delay", fontsize=14)
    plt.xlabel("Total Joystick Movement (Motor Effort)")
    plt.ylabel("Reaction Delay (s)")
    plt.show()

    # Correlation
    corr = df[['Motor_Effort', 'Reaction_Delay']].corr(method='spearman')
    print(f"Spearman Correlation between Motor Effort and Reaction Delay:\n{corr}")

    return df


def analyze_attention_redistribution(
    perception_results_all,
    experiment_logs_all,
    demographics,
    ax=None
):
    """
    Calculates perception and motor metrics across difficulty levels,
    including modality-specific accuracy for Visual, Audio, and Haptic.

    Invalidated trial:
        Either perceived value is -1.

    Missed trial:
        The trial is not invalidated and either perceived value is 0.

    Accuracy:
        Both perceived angle and distance must match the actual values,
        calculated among valid-response trials.

    Miss rate:
        Missed trials / (missed + valid-response trials).

    Modality-specific accuracy:
        Calculated separately for Visual, Audio, and Haptic feedback.

    Statistical tests:
        Paired Wilcoxon signed-rank tests between difficulty levels.
    """

    required_demographics_columns = {"Participant ID", "Gender"}
    missing_demographics_columns = (
        required_demographics_columns - set(demographics.columns)
    )

    if missing_demographics_columns:
        raise ValueError(
            f"Missing demographics columns: "
            f"{sorted(missing_demographics_columns)}"
        )

    participant_names = list(perception_results_all.keys())
    demographics = demographics.reset_index(drop=True).copy()

    # ---------------------------------------------------------
    # Standardize demographics
    # ---------------------------------------------------------

    demographics["Gender"] = (
        demographics["Gender"].astype(str).str.strip().str.lower()
    )

    demographics["Participant ID"] = (
        demographics["Participant ID"]
        .astype(str)
        .apply(lambda x: x.zfill(2) if len(x) == 1 else x)
    )

    participant_gender_map = dict(
        zip(
            demographics["Participant ID"],
            demographics["Gender"]
        )
    )

    # ---------------------------------------------------------
    # Settings
    # ---------------------------------------------------------

    difficulty_order = ["easy", "medium", "hard"]

    modality_order = ["Visual", "Auditory", "Haptic"]

    modality_column = "Modality"

    perc_angle_col = "Perceived angle"
    perc_dist_col = "Perceived distance"

    metrics_list = []
    modality_accuracy_list = []

    # ---------------------------------------------------------
    # Calculate metrics for each participant and difficulty
    # ---------------------------------------------------------

    for subject_id in participant_names:

        trials_df = perception_results_all.get(subject_id)
        logs_df = experiment_logs_all.get(subject_id)

        participant_gender = participant_gender_map.get(
            subject_id, np.nan
        )

        if trials_df is None or logs_df is None:
            continue

        for difficulty in difficulty_order:

            phase_trials = trials_df.loc[
                trials_df["Difficulty level"] == difficulty
            ].copy()

            phase_logs = logs_df.loc[
                logs_df["Difficulty level"] == difficulty
            ].copy()

            # -------------------------------------------------
            # Overall perception accuracy
            # -------------------------------------------------

            perceived_angle = pd.to_numeric(
                phase_trials[perc_angle_col],
                errors="coerce"
            )

            perceived_distance = pd.to_numeric(
                phase_trials[perc_dist_col],
                errors="coerce"
            )

            invalidated_mask = (
                perceived_angle.eq(-1) |
                perceived_distance.eq(-1)
            )

            missed_mask = (
                ~invalidated_mask &
                (
                    perceived_angle.eq(0) |
                    perceived_distance.eq(0)
                )
            )

            valid_response_mask = (
                ~invalidated_mask &
                perceived_angle.gt(0) &
                perceived_distance.gt(0)
            )

            valid_trials = phase_trials.loc[
                valid_response_mask
            ].copy()

            if not valid_trials.empty:

                actual_angle = pd.to_numeric(
                    valid_trials["Angle"],
                    errors="coerce"
                )

                actual_distance = pd.to_numeric(
                    valid_trials["Distance"],
                    errors="coerce"
                )

                valid_perceived_angle = pd.to_numeric(
                    valid_trials[perc_angle_col],
                    errors="coerce"
                )

                valid_perceived_distance = pd.to_numeric(
                    valid_trials[perc_dist_col],
                    errors="coerce"
                )

                correct_mask = (
                    actual_angle.eq(valid_perceived_angle) &
                    actual_distance.eq(valid_perceived_distance)
                )

                accuracy = correct_mask.mean() * 100

                # ---------------------------------------------
                # Polar accuracy
                # ---------------------------------------------

                theta_true = actual_angle * (np.pi / 4)
                theta_perc = valid_perceived_angle * (np.pi / 4)

                r_true = actual_distance
                r_perc = valid_perceived_distance

                squared_error = (
                    r_true**2 +
                    r_perc**2 -
                    2 * r_true * r_perc *
                    np.cos(theta_true - theta_perc)
                )

                geom_error = np.sqrt(
                    np.maximum(squared_error, 0)
                )

                r_max = max(
                    r_true.max(),
                    r_perc.max()
                )

                if pd.isna(r_max) or r_max <= 0:
                    polar_accuracy = np.nan
                else:
                    polar_acc_vals = (
                        1 - geom_error / (2 * r_max)
                    ) * 100

                    polar_accuracy = (
                        polar_acc_vals
                        .clip(lower=0, upper=100)
                        .mean()
                    )

            else:
                accuracy = np.nan
                polar_accuracy = np.nan

            # -------------------------------------------------
            # Miss rate
            # -------------------------------------------------

            n_missed = int(missed_mask.sum())

            n_valid_responses = int(
                valid_response_mask.sum()
            )

            n_analyzable_trials = (
                n_missed + n_valid_responses
            )

            miss_rate = (
                n_missed / n_analyzable_trials * 100
                if n_analyzable_trials > 0
                else np.nan
            )

            # -------------------------------------------------
            # Reaction time
            # -------------------------------------------------

            response_start = pd.to_numeric(
                phase_trials["Response start"],
                errors="coerce"
            )

            phase_timestamp = pd.to_numeric(
                phase_trials["Phase timestamp"],
                errors="coerce"
            )

            valid_rt_mask = response_start.gt(0)

            avg_rt = (
                (
                    response_start.loc[valid_rt_mask] -
                    phase_timestamp.loc[valid_rt_mask]
                ).mean()
                if valid_rt_mask.any()
                else np.nan
            )

            # -------------------------------------------------
            # Collisions
            # -------------------------------------------------

            collision_values = pd.to_numeric(
                phase_logs["Number of collision"],
                errors="coerce"
            ).dropna()

            collisions = (
                collision_values.iloc[-1] -
                collision_values.iloc[0]
                if len(collision_values) >= 2
                else np.nan
            )

            # -------------------------------------------------
            # Joystick variance
            # -------------------------------------------------

            thumbstick_x = pd.to_numeric(
                phase_logs["Thumbstick x"],
                errors="coerce"
            )

            joystick_var = thumbstick_x.var()

            # -------------------------------------------------
            # Head variance
            # -------------------------------------------------

            head_x = (
                phase_logs["Head rotation"]
                .astype(str)
                .str.strip("()")
                .str.split(",", expand=True)[0]
            )

            head_var = pd.to_numeric(
                head_x,
                errors="coerce"
            ).var()

            # -------------------------------------------------
            # Store overall metrics
            # -------------------------------------------------

            metrics_list.append({
                "Subject": subject_id,
                "Gender": participant_gender,
                "Difficulty": difficulty,
                "Accuracy": accuracy,
                "Polar Accuracy": polar_accuracy,
                "Miss Rate": miss_rate,
                "Reaction Time": avg_rt,
                "Collisions": collisions,
                "Joystick Variance": joystick_var,
                "Head Variance": head_var,
                "Missed Trials": n_missed,
                "Valid Response Trials": n_valid_responses,
                "Invalidated Trials": int(
                    invalidated_mask.sum()
                ),
                "Analyzable Trials": n_analyzable_trials
            })

            # -------------------------------------------------
            # Modality-specific accuracy
            # -------------------------------------------------

            if modality_column not in phase_trials.columns:
                raise ValueError(
                    f"Missing modality column: "
                    f"'{modality_column}'"
                )

            for modality in modality_order:

                modality_trials = phase_trials.loc[
                    phase_trials[modality_column]
                    .astype(str)
                    .str.strip()
                    .str.lower()
                    == modality.lower()
                ].copy()

                mod_angle = pd.to_numeric(
                    modality_trials[perc_angle_col],
                    errors="coerce"
                )

                mod_distance = pd.to_numeric(
                    modality_trials[perc_dist_col],
                    errors="coerce"
                )

                mod_invalidated = (
                    mod_angle.eq(-1) |
                    mod_distance.eq(-1)
                )

                mod_valid = (
                    ~mod_invalidated &
                    mod_angle.gt(0) &
                    mod_distance.gt(0)
                )

                mod_valid_trials = modality_trials.loc[
                    mod_valid
                ]

                if not mod_valid_trials.empty:

                    mod_actual_angle = pd.to_numeric(
                        mod_valid_trials["Angle"],
                        errors="coerce"
                    )

                    mod_actual_distance = pd.to_numeric(
                        mod_valid_trials["Distance"],
                        errors="coerce"
                    )

                    mod_perceived_angle = pd.to_numeric(
                        mod_valid_trials[perc_angle_col],
                        errors="coerce"
                    )

                    mod_perceived_distance = pd.to_numeric(
                        mod_valid_trials[perc_dist_col],
                        errors="coerce"
                    )

                    mod_correct = (
                        mod_actual_angle.eq(
                            mod_perceived_angle
                        ) &
                        mod_actual_distance.eq(
                            mod_perceived_distance
                        )
                    )

                    mod_accuracy = (
                        mod_correct.mean() * 100
                    )

                else:
                    mod_accuracy = np.nan

                modality_accuracy_list.append({
                    "Subject": subject_id,
                    "Gender": participant_gender,
                    "Difficulty": difficulty,
                    "Modality": modality,
                    "Accuracy": mod_accuracy
                })

    # =========================================================
    # Create dataframes
    # =========================================================

    metrics_df = pd.DataFrame(metrics_list)

    modality_accuracy_df = pd.DataFrame(
        modality_accuracy_list
    )

    # =========================================================
    # Paired Wilcoxon tests
    # =========================================================

    comparisons = [
        ("easy", "medium"),
        ("medium", "hard"),
        ("easy", "hard")
    ]

    modality_pvalues = []

    for modality in modality_order:

        modality_data = modality_accuracy_df.loc[
            modality_accuracy_df["Modality"] == modality
        ]

        modality_pivot = modality_data.pivot(
            index="Subject",
            columns="Difficulty",
            values="Accuracy"
        )

        for diff1, diff2 in comparisons:

            paired_data = modality_pivot[
                [diff1, diff2]
            ].dropna()

            n_pairs = len(paired_data)

            if n_pairs == 0:

                p_val = np.nan

            elif np.allclose(
                paired_data[diff1].values,
                paired_data[diff2].values
            ):

                p_val = 1.0

            else:

                try:
                    _, p_val = wilcoxon(
                        paired_data[diff1],
                        paired_data[diff2],
                        alternative="two-sided"
                    )
                except ValueError:
                    p_val = np.nan

            modality_pvalues.append({
                "Modality": modality,
                "Comparison": (
                    f"{diff1.capitalize()} vs "
                    f"{diff2.capitalize()}"
                ),
                "N": n_pairs,
                "p-value": p_val
            })

    modality_pvalues_df = pd.DataFrame(
        modality_pvalues
    )

    print("\nModality-specific accuracy:")
    print(
        modality_accuracy_df.pivot_table(
            index="Modality",
            columns="Difficulty",
            values="Accuracy",
            aggfunc="mean"
        ).round(2)
    )

    print("\nModality-specific Wilcoxon p-values:")
    print(modality_pvalues_df.to_string(index=False))

    # =========================================================
    # Normalize metrics for plotting
    # =========================================================

    cols_to_norm = [
        "Accuracy",
        "Polar Accuracy",
        "Miss Rate",
        "Reaction Time",
        "Collisions",
        "Joystick Variance",
        "Head Variance"
    ]

    norm_df = metrics_df.copy()

    custom_palette = dict(
        zip(
            cols_to_norm + [
                "Visual Accuracy",
                "Audio Accuracy",
                "Haptic Accuracy"
            ],
            sns.color_palette(
                "tab10",
                len(cols_to_norm) + 3
            )
        )
    )

    for col in cols_to_norm:

        column_std = norm_df[col].std()

        if pd.notna(column_std) and column_std != 0:
            norm_df[col] = (
                norm_df[col] - norm_df[col].mean()
            ) / column_std
        else:
            norm_df[col] = np.nan

    melted_df = norm_df.melt(
        id_vars=["Subject", "Gender", "Difficulty"],
        value_vars=cols_to_norm,
        var_name="Variable",
        value_name="Z-Score"
    )

    # ---------------------------------------------------------
    # Normalize modality-specific accuracy
    # ---------------------------------------------------------

    modality_plot_df = modality_accuracy_df.copy()

    modality_plot_df["Variable"] = (
        modality_plot_df["Modality"] + " Accuracy"
    )

    modality_variable_order = [
        "Visual Accuracy",
        "Audio Accuracy",
        "Haptic Accuracy"
    ]

    for variable in modality_variable_order:

        mask = (
            modality_plot_df["Variable"] == variable
        )

        values = modality_plot_df.loc[
            mask, "Accuracy"
        ]

        column_std = values.std()

        if pd.notna(column_std) and column_std != 0:

            modality_plot_df.loc[
                mask, "Z-Score"
            ] = (
                values - values.mean()
            ) / column_std

        else:

            modality_plot_df.loc[
                mask, "Z-Score"
            ] = np.nan

    modality_melted = modality_plot_df[
        [
            "Subject",
            "Gender",
            "Difficulty",
            "Variable",
            "Z-Score"
        ]
    ].copy()

    melted_df = pd.concat(
        [melted_df, modality_melted],
        ignore_index=True
    )

    melted_df["Difficulty"] = pd.Categorical(
        melted_df["Difficulty"],
        categories=difficulty_order,
        ordered=True
    )

    # =========================================================
    # Plot
    # =========================================================

    standalone = ax is None

    if standalone:
        fig, ax = plt.subplots(
            figsize=(13, 7)
        )
    else:
        fig = ax.figure

    all_variables = (
        cols_to_norm + modality_variable_order
    )

    sns.pointplot(
        data=melted_df,
        x="Difficulty",
        y="Z-Score",
        hue="Variable",
        hue_order=all_variables,
        order=difficulty_order,
        palette=custom_palette,
        dodge=0.4,
        linestyles="-",
        errorbar=("ci", 95),
        capsize=0.05,
        ax=ax
    )

    # =========================================================
    # Statistical annotations
    # =========================================================

    metrics_to_annotate = [
        "Accuracy",
        "Polar Accuracy",
        "Miss Rate",
        "Collisions",
        "Joystick Variance",
        "Visual Accuracy",
        "Audio Accuracy",
        "Haptic Accuracy"
    ]

    bbox_props = dict(
        boxstyle="round,pad=0.2",
        facecolor="white",
        edgecolor="none",
        alpha=0.85
    )

    annotation_segments = [
        ("easy", "medium", 0, 1),
        ("medium", "hard", 1, 2)
    ]

    for metric in metrics_to_annotate:

        color = custom_palette[metric]

        segments = annotation_segments.copy()

        if metric in [
            "Accuracy",
            "Polar Accuracy",
            "Visual Accuracy",
            "Audio Accuracy",
            "Haptic Accuracy"
        ]:
            segments.append(
                ("easy", "hard", 0, 2)
            )

        for diff1, diff2, x1, x2 in segments:

            # ---------------------------------------------
            # Select the appropriate paired data
            # ---------------------------------------------

            if metric in modality_variable_order:

                modality = metric.replace(
                    " Accuracy", ""
                )

                test_row = modality_pvalues_df.loc[
                    (
                        modality_pvalues_df["Modality"]
                        == modality
                    ) &
                    (
                        modality_pvalues_df["Comparison"]
                        == (
                            f"{diff1.capitalize()} vs "
                            f"{diff2.capitalize()}"
                        )
                    )
                ]

                p_val = (
                    test_row["p-value"].iloc[0]
                    if not test_row.empty
                    else np.nan
                )

            else:

                pivot_df = metrics_df.pivot(
                    index="Subject",
                    columns="Difficulty",
                    values=metric
                )

                paired_data = pivot_df[
                    [diff1, diff2]
                ].dropna()

                if len(paired_data) == 0:

                    p_val = np.nan

                elif np.allclose(
                    paired_data[diff1].values,
                    paired_data[diff2].values
                ):

                    p_val = 1.0

                else:

                    try:
                        _, p_val = wilcoxon(
                            paired_data[diff1],
                            paired_data[diff2],
                            alternative="two-sided"
                        )
                    except ValueError:
                        p_val = np.nan

            # ---------------------------------------------
            # Format p-value
            # ---------------------------------------------

            if pd.isna(p_val):
                p_str = "p=NA"
            elif p_val < 0.001:
                p_str = "p<0.001"
            else:
                p_str = f"p={p_val:.3f}"

            # ---------------------------------------------
            # Determine annotation position
            # ---------------------------------------------

            y1 = melted_df.loc[
                (
                    melted_df["Variable"] == metric
                ) &
                (
                    melted_df["Difficulty"] == diff1
                ),
                "Z-Score"
            ].mean()

            y2 = melted_df.loc[
                (
                    melted_df["Variable"] == metric
                ) &
                (
                    melted_df["Difficulty"] == diff2
                ),
                "Z-Score"
            ].mean()

            if pd.isna(y1) or pd.isna(y2):
                continue

            if diff1 == "easy" and diff2 == "hard":

                y_mid = melted_df.loc[
                    (
                        melted_df["Variable"] == metric
                    ) &
                    (
                        melted_df["Difficulty"] == "medium"
                    ),
                    "Z-Score"
                ].mean()

                y_values = [
                    value for value in [
                        y1, y2, y_mid
                    ]
                    if pd.notna(value)
                ]

                y_pos = max(y_values) + 0.35

                p_str = (
                    f"Easy vs Hard: {p_str}"
                )

            else:

                y_pos = (y1 + y2) / 2

            x_pos = (x1 + x2) / 2

            ax.text(
                x_pos,
                y_pos + 0.1,
                p_str,
                color=color,
                ha="center",
                va="bottom",
                fontsize=8,
                fontweight="bold",
                bbox=bbox_props,
                zorder=10
            )

    # =========================================================
    # Final formatting
    # =========================================================

    ax.set_ylabel(
        "Normalized Metric Value (Z-Score)",
        fontsize=11
    )

    ax.grid(True, alpha=0.3)

    legend = ax.get_legend()

    if legend is not None:
        legend.set_title("Variable")
        legend.set_bbox_to_anchor((1.03, 1))
        legend._loc = 2

    fig.tight_layout()

    plt.savefig(
        "across_difficulty.pdf",
        format="pdf",
        bbox_inches="tight"
    )

    plt.show()

    return (
        metrics_df,
        modality_accuracy_df,
        modality_pvalues_df
    )



def plot_cognitive_signatures_heatmap(subjects_data_trials, experiment_logs_all, num_clusters=4):
    """Extracts profiles, applies hierarchical clustering, and visually labels the main participant phenotypes."""

    profiles_list = []

    for subject_id in subjects_data_trials.keys():
        trials_df = subjects_data_trials.get(subject_id)
        logs_df = experiment_logs_all.get(subject_id)

        if trials_df is None or trials_df.empty or logs_df is None or logs_df.empty:
            continue

        perc_angle_col = 'Angle perceived' if 'Angle perceived' in trials_df.columns else 'Perceived angle'
        perc_dist_col = 'Distance perceived' if 'Distance perceived' in trials_df.columns else 'Perceived distance'

        accuracies = {}
        for mod in ['visual', 'auditory', 'haptic']:
            mod_trials = trials_df[trials_df['Modality'] == mod]
            valid_trials = mod_trials[(mod_trials[perc_angle_col] > 0) & (mod_trials[perc_dist_col] > 0)]
            if not valid_trials.empty:
                correct = ((valid_trials['Angle'] == valid_trials[perc_angle_col]) &
                           (valid_trials['Distance'] == valid_trials[perc_dist_col])).sum()
                accuracies[mod] = correct / len(mod_trials)
            else:
                accuracies[mod] = 0.0

        valid_rt = trials_df[trials_df['Response start'] > 0]
        avg_rt = (valid_rt['Response start'] - valid_rt['Phase timestamp']).mean() if not valid_rt.empty else np.nan

        total_collisions = logs_df['Number of collision'].iloc[-1]

        try:
            head_x = logs_df['Head rotation'].str.strip('()').str.split(',', expand=True)[0].astype(float)
            head_var = head_x.var()
        except Exception:
            head_var = np.nan

        profiles_list.append({
            'Subject': str(subject_id),
            'Visual Acc': accuracies['visual'],
            'Auditory Acc': accuracies['auditory'],
            'Haptic Acc': accuracies['haptic'],
            'Reaction Time': avg_rt,
            'Collisions': total_collisions,
            'Head Motion': head_var
        })

    profiles_df = pd.DataFrame(profiles_list).dropna()
    profiles_df.set_index('Subject', inplace=True)

    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(profiles_df)
    scaled_df = pd.DataFrame(scaled_data, index=profiles_df.index, columns=profiles_df.columns)

    # 1. Perform hierarchical clustering manually to extract the labels
    row_linkage = sch.linkage(scaled_df, method='ward', metric='euclidean')

    # 2. Cut the tree into your desired number of main clusters (phenotypes)
    cluster_labels = sch.fcluster(row_linkage, num_clusters, criterion='maxclust')

    # 3. Create a color mapping for the rows based on their assigned cluster
    cluster_palette = sns.color_palette("tab10", num_clusters)
    row_colors = [cluster_palette[label - 1] for label in cluster_labels]

    # 4. Append the cluster label directly to the Subject ID for the Y-axis
    scaled_df.index = [f"{idx} (C{label})" for idx, label in zip(scaled_df.index, cluster_labels)]

    # Create the clustered heatmap
    g = sns.clustermap(
        scaled_df,
        row_linkage=row_linkage,  # Use the pre-computed linkage
        row_colors=row_colors,  # Add the cluster color bar
        cmap="coolwarm",
        figsize=(12, 10),
        linewidths=0.5,
        cbar_pos=(0.02, 0.8, 0.03, 0.18),
        dendrogram_ratio=(0.15, 0.2)
    )

    g.fig.suptitle("Multimodal Perceptual Signatures with Extracted Clusters", fontsize=16, y=1.05)
    g.ax_heatmap.set_xlabel("Cognitive and Motor Features", fontsize=12, labelpad=15)
    g.ax_heatmap.set_ylabel("Participants (and Assigned Cluster)", fontsize=12, labelpad=15)

    # Adjust layout to prevent cut-offs
    plt.setp(g.ax_heatmap.get_xticklabels(), rotation=45, ha="right")
    g.fig.subplots_adjust(bottom=0.25)

    plt.show()

    return profiles_df, cluster_labels


def analyze_latent_strategies(subjects_data_trials, experiment_logs_all, n_clusters=4):
    """Extracts cognitive features, applies clustering to identify distinct latent behavioral strategies, and plots the profile of each strategy."""

    profiles_list = []

    for subject_id in subjects_data_trials.keys():
        trials_df = subjects_data_trials.get(subject_id)
        logs_df = experiment_logs_all.get(subject_id)

        if trials_df is None or trials_df.empty or logs_df is None or logs_df.empty:
            continue

        perc_angle_col = 'Angle perceived' if 'Angle perceived' in trials_df.columns else 'Perceived angle'
        perc_dist_col = 'Distance perceived' if 'Distance perceived' in trials_df.columns else 'Perceived distance'

        accuracies = {}
        for mod in ['visual', 'auditory', 'haptic']:
            mod_trials = trials_df[trials_df['Modality'] == mod]
            valid_trials = mod_trials[(mod_trials[perc_angle_col] > 0) & (mod_trials[perc_dist_col] > 0)]
            if not valid_trials.empty:
                correct = ((valid_trials['Angle'] == valid_trials[perc_angle_col]) &
                           (valid_trials['Distance'] == valid_trials[perc_dist_col])).sum()
                accuracies[mod] = correct / len(mod_trials)
            else:
                accuracies[mod] = 0.0

        valid_rt = trials_df[trials_df['Response start'] > 0]
        avg_rt = (valid_rt['Response start'] - valid_rt['Phase timestamp']).mean() if not valid_rt.empty else np.nan

        total_collisions = logs_df['Number of collision'].iloc[-1]

        try:
            head_x = logs_df['Head rotation'].str.strip('()').str.split(',', expand=True)[0].astype(float)
            head_var = head_x.var()
        except Exception:
            head_var = np.nan

        profiles_list.append({
            'Subject': str(subject_id),
            'Visual Acc': accuracies['visual'],
            'Auditory Acc': accuracies['auditory'],
            'Haptic Acc': accuracies['haptic'],
            'Reaction Time': avg_rt,
            'Collisions': total_collisions,
            'Head Motion': head_var
        })

    profiles_df = pd.DataFrame(profiles_list).dropna()
    profiles_df.set_index('Subject', inplace=True)

    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(profiles_df)
    scaled_df = pd.DataFrame(scaled_data, index=profiles_df.index, columns=profiles_df.columns)

    # Group participants into distinct strategy clusters
    clusterer = AgglomerativeClustering(n_clusters=n_clusters, metric='euclidean', linkage='ward')
    cluster_labels = clusterer.fit_predict(scaled_df)

    scaled_df['Strategy_Cluster'] = cluster_labels + 1
    profiles_df['Strategy_Cluster'] = cluster_labels + 1

    # Calculate the mean Z-score profile for each strategy
    strategy_profiles = scaled_df.groupby('Strategy_Cluster').mean()

    melted_profiles = strategy_profiles.reset_index().melt(
        id_vars='Strategy_Cluster',
        var_name='Feature',
        value_name='Mean_Z_Score'
    )

    plt.figure(figsize=(12, 6))

    sns.barplot(
        data=melted_profiles,
        x='Feature',
        y='Mean_Z_Score',
        hue='Strategy_Cluster',
        palette='tab10'
    )

    plt.title('Latent Behavioral Strategies: Average Feature Profiles per Cluster', fontsize=14, pad=15)
    plt.ylabel('Deviation from Average (Mean Z-Score)', fontsize=12)
    plt.xlabel('Cognitive and Motor Features', fontsize=12)

    plt.axhline(0, color='black', linewidth=1, linestyle='--')
    plt.xticks(rotation=45, ha='right')
    plt.legend(title='Strategy Cluster', bbox_to_anchor=(1.05, 1), loc='upper left')

    plt.tight_layout()
    plt.show()

    return profiles_df, strategy_profiles


def plot_collision_vs_accuracy(perception_results_all, experiment_logs_all, color_palette, ax=None):
    """
    Plots the relationship between Cue Perception Accuracy and
    the Number of Collisions during the cue windows, categorized by modality.

    If `ax` is provided, the regression plot is drawn onto that Axes instead
    of creating a new figure (via `sns.lmplot`), allowing this function to be
    embedded in a larger dashboard.
    """
    records = []

    for subject_id, perc_df in perception_results_all.items():
        logs_df = experiment_logs_all.get(subject_id)
        if logs_df is None:
            continue

        # فیلتر کردن داده‌های معتبر (نادیده گرفتن خطاهای سخت‌افزاری 1-)
        valid_trials = perc_df[
            (perc_df['Perceived angle'] >= 0) &
            (perc_df['Modality'].isin(['visual', 'auditory', 'haptic']))
            ].copy()

        for mod in ['visual', 'auditory', 'haptic']:
            mod_trials = valid_trials[valid_trials['Modality'] == mod]
            if len(mod_trials) == 0:
                continue

            # 1. محاسبه دقت (Accuracy): چند درصد از زوایا دقیقاً درست تشخیص داده شده‌اند؟
            # پاسخ‌های Missed (0) به طور خودکار به عنوان غلط در نظر گرفته می‌شوند.
            correct_count = (mod_trials['Angle'] == mod_trials['Perceived angle']).sum()
            accuracy = (correct_count / len(mod_trials)) * 100

            # 2. محاسبه مجموع برخوردها دقیقاً در پنجره زمانی مربوط به این مدالیته
            total_collisions = 0
            for _, trial in mod_trials.iterrows():
                t_start = trial['Timestamp']

                # تعیین زمان پایان پاسخ
                if trial['Perceived angle'] == 0:  # Missed
                    t_end = t_start + 4.0
                else:
                    time_spent = trial['Response end'] - trial['Phase timestamp']
                    t_end = t_start + time_spent

                # استخراج لاگ‌ها برای این بازه زمانی مشخص
                window = logs_df[(logs_df['Timestamp'] >= t_start) & (logs_df['Timestamp'] <= t_end)]
                if not window.empty:
                    colls = window['Number of collision'].max() - window['Number of collision'].min()
                    total_collisions += colls

            # ذخیره داده‌های این شخص
            records.append({
                'Subject_ID': subject_id,
                'Modality': mod.capitalize(),
                'Accuracy': accuracy,
                'Collisions': total_collisions
            })

    # تبدیل به دیتافریم برای رسم پلات
    df = pd.DataFrame(records)

    # تنظیمات استایل پلات
    sns.set_theme(style="whitegrid", context="paper", font_scale=1.2)
    palette = {mod.capitalize(): color for mod, color in color_palette.items()}

    standalone = ax is None
    if standalone:
        fig, ax = plt.subplots(figsize=(7.8, 6))

    # رسم نمودار پراکندگی همراه با خط برازش (Regression Line) برای هر مدالیته
    for mod in ['Visual', 'Auditory', 'Haptic']:
        sub_df = df[df['Modality'] == mod]
        sns.regplot(
            data=sub_df,
            x='Accuracy',
            y='Collisions',
            color=palette[mod],
            scatter_kws={'alpha': 0.6, 's': 60},
            line_kws={'lw': 2},
            label=mod,
            ax=ax
        )

    # تنظیم نام محورها
    ax.set_xlabel("Perception Accuracy (%)")
    ax.set_ylabel("Total Collisions During Cues")
    ax.set_title("Collision Rate vs. Accuracy by Modality", fontweight='bold')
    ax.legend(title='Modality')

    # محاسبه و اضافه کردن مقادیر پیرسون به گوشه نمودار
    text_y = 0.95
    for mod in ['Visual', 'Auditory', 'Haptic']:
        sub_df = df[df['Modality'] == mod]

        # محاسبه ضریب پیرسون (r) و مقدار P-value
        r, p = pearsonr(sub_df['Accuracy'], sub_df['Collisions'])

        color = palette[mod]
        # اضافه کردن متن روی نمودار
        ax.text(0.05, text_y, f"{mod}: r = {r:.3f} (p-value = {p:.3f})",
                transform=ax.transAxes, color=color, fontweight='bold', fontsize=9)
        text_y -= 0.08

    if standalone:
        plt.tight_layout()
        plt.show()

    return df


def test_mrt_interaction(perception_results_all, experiment_logs_all, color_palette, axes=None):
    """
    Evaluates Multiple Resource Theory by plotting the Modality x Difficulty interaction
    for Reaction Time, Angular Error, and Cue-Window Collisions.

    If `axes` (an array-like of 3 Matplotlib Axes) is provided, the plots are
    drawn onto those axes instead of creating a new figure, allowing this
    function to be embedded in a larger dashboard.
    """
    interaction_data = []

    for subject_id in perception_results_all.keys():
        trials_df = perception_results_all.get(subject_id)
        logs_df = experiment_logs_all.get(subject_id)

        if trials_df is None or trials_df.empty or logs_df is None or logs_df.empty:
            continue

        # Standardize column names
        diff_col = 'Difficulty level' if 'Difficulty level' in trials_df.columns else 'Difficulty'
        perc_angle_col = 'Angle perceived' if 'Angle perceived' in trials_df.columns else 'Perceived angle'

        for _, trial in trials_df.iterrows():
            modality = trial['Modality']
            difficulty = trial[diff_col].lower()

            # Skip invalid modalities or missed trials for RT and Error calculations
            if modality not in ['visual', 'auditory', 'haptic'] or trial[perc_angle_col] <= 0:
                continue

            # 1. Calculate Reaction Time
            rt = trial['Response start'] - trial['Phase timestamp']

            # 2. Calculate Circular Angular Error (0 to 4)
            diff = abs(trial['Angle'] - trial[perc_angle_col])
            angular_error = min(diff, 8 - diff)

            # 3. Calculate Collisions during the cue window (Phase timestamp to Phase timestamp + 2s)
            start_time = trial['Phase timestamp']
            end_time = start_time + 2.0

            # Isolate the continuous log data for this specific 2-second window
            window_logs = logs_df[(logs_df['Timestamp'] >= start_time) &
                                  (logs_df['Timestamp'] <= end_time) &
                                  (logs_df['Difficulty level'].str.lower() == difficulty)]

            if not window_logs.empty:
                # Collisions are cumulative in the logs; subtract the first value from the last
                cue_collisions = window_logs['Number of collision'].iloc[-1] - window_logs['Number of collision'].iloc[
                    0]
            else:
                cue_collisions = 0

            interaction_data.append({
                'Subject': subject_id,
                'Modality': modality.capitalize(),
                'Difficulty': difficulty.capitalize(),
                'Reaction Time': rt,
                'Angular Error': angular_error,
                'Cue Collisions': cue_collisions
            })

    # Create the DataFrame
    df_interaction = pd.DataFrame(interaction_data)

    # Reorder categories for plotting
    difficulty_order = ['Easy', 'Medium', 'Hard']
    df_interaction['Difficulty'] = pd.Categorical(df_interaction['Difficulty'], categories=difficulty_order,
                                                  ordered=True)

    # Generate Interaction Plots
    sns.set_theme(style="whitegrid", context="paper", font_scale=1.2)
    standalone = axes is None
    if standalone:
        fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    palette = {mod.capitalize(): color for mod, color in color_palette.items()}
    markers = {'Visual': 'o', 'Auditory': 's', 'Haptic': '^'}

    # Plot 1: Reaction Time
    sns.pointplot(data=df_interaction, x='Difficulty', y='Reaction Time', hue='Modality',
                  palette=palette, markers=[markers[m] for m in palette.keys()], ax=axes[0], dodge=True)
    axes[0].set_title('Interaction: Reaction Time', fontweight='bold')
    axes[0].set_ylabel('Reaction Time (s)')
    axes[0].get_legend().remove()

    # Plot 2: Angular Error
    sns.pointplot(data=df_interaction, x='Difficulty', y='Angular Error', hue='Modality',
                  palette=palette, markers=[markers[m] for m in palette.keys()], ax=axes[1], dodge=True)
    axes[1].set_title('Interaction: Angular Error', fontweight='bold')
    axes[1].set_ylabel('Mean Angular Error')
    axes[1].get_legend().remove()

    # Plot 3: Collisions during Cue
    sns.pointplot(data=df_interaction, x='Difficulty', y='Cue Collisions', hue='Modality',
                  palette=palette, markers=[markers[m] for m in palette.keys()], ax=axes[2], dodge=True)
    axes[2].set_title('Interaction: Collisions During Cue', fontweight='bold')
    axes[2].set_ylabel('Mean Collisions (per 2s window)')

    # Place a single legend outside the plots
    axes[2].legend(title='Modality', bbox_to_anchor=(1.05, 1), loc='upper left')

    if standalone:
        fig.suptitle('Dual-Task Interference: Multiple Resource Theory Evaluation', fontsize=16, fontweight='bold', y=1.05)
        plt.tight_layout()
        plt.show()

    return df_interaction


def plot_accuracy_over_time_by_modality(perception_results_all, color_palette):
    """Plots longitudinal accuracy trends by modality (auditory, haptic, visual), excluding invalid/missed trials."""

    all_trials = []

    for subject_id, df in perception_results_all.items():
        if df is None or df.empty:
            continue

        df_copy = df.copy()

        perc_angle_col = 'Angle perceived' if 'Angle perceived' in df_copy.columns else 'Perceived angle'
        perc_dist_col = 'Distance perceived' if 'Distance perceived' in df_copy.columns else 'Perceived distance'
        trial_col = 'Trial number' if 'Trial number' in df_copy.columns else 'Trial'

        df_copy = df_copy[(df_copy[perc_angle_col] > 0) & (df_copy[perc_dist_col] > 0)]

        df_copy['Angular_Accuracy'] = (df_copy['Angle'] == df_copy[perc_angle_col]).astype(float)
        df_copy['Distance_Accuracy'] = (df_copy['Distance'] == df_copy[perc_dist_col]).astype(float)
        df_copy['Trial_Index'] = df_copy[trial_col]
        df_copy['Modality'] = df_copy['Modality'].str.lower()

        all_trials.append(df_copy)

    combined_df = pd.concat(all_trials, ignore_index=True)

    sns.set_theme(style="whitegrid", context="paper", font_scale=1.2)
    fig, axes = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

    palette = color_palette
    modality_order = ['auditory', 'haptic', 'visual']

    sns.lineplot(
        data=combined_df,
        x='Trial_Index',
        y='Angular_Accuracy',
        hue='Modality',
        hue_order=modality_order,
        palette=palette,
        ax=axes[0],
        errorbar=('ci', 95),
        alpha=0.5
    )

    for mod in modality_order:
        mod_data = combined_df[combined_df['Modality'] == mod]
        if not mod_data.empty:
            sns.regplot(
                data=mod_data,
                x='Trial_Index',
                y='Angular_Accuracy',
                scatter=False,
                color=palette[mod],
                ax=axes[0],
                line_kws={'linestyle': '--', 'linewidth': 2}
            )

    axes[0].set_title('Angular Accuracy Over Time by Modality (Valid Trials Only)', fontweight='bold', fontsize=14)
    axes[0].set_ylabel('Angular Accuracy Rate', fontweight='bold')
    axes[0].set_ylim(0, 1.05)
    axes[0].legend(title='Modality', loc='lower right')

    sns.lineplot(
        data=combined_df,
        x='Trial_Index',
        y='Distance_Accuracy',
        hue='Modality',
        hue_order=modality_order,
        palette=palette,
        ax=axes[1],
        errorbar=('ci', 95),
        alpha=0.5
    )

    for mod in modality_order:
        mod_data = combined_df[combined_df['Modality'] == mod]
        if not mod_data.empty:
            sns.regplot(
                data=mod_data,
                x='Trial_Index',
                y='Distance_Accuracy',
                scatter=False,
                color=palette[mod],
                ax=axes[1],
                line_kws={'linestyle': '--', 'linewidth': 2}
            )

    axes[1].set_title('Radial Distance Accuracy Over Time by Modality (Valid Trials Only)', fontweight='bold',
                      fontsize=14)
    axes[1].set_ylabel('Distance Accuracy Rate', fontweight='bold')
    axes[1].set_xlabel('Experiment Timeline (Trial 1 to 216)', fontweight='bold')
    axes[1].set_ylim(0, 1.05)
    axes[1].legend(title='Modality', loc='lower right')

    for ax in axes:
        ax.axvline(x=72.5, color='gray', linestyle=':', alpha=0.7)
        ax.axvline(x=144.5, color='gray', linestyle=':', alpha=0.7)

        ax.text(36, 0.05, 'Phase 1', ha='center', va='bottom', color='gray', fontsize=10)
        ax.text(108, 0.05, 'Phase 2', ha='center', va='bottom', color='gray', fontsize=10)
        ax.text(180, 0.05, 'Phase 3', ha='center', va='bottom', color='gray', fontsize=10)

    plt.tight_layout()
    plt.show()

    return combined_df


def plot_longitudinal_performance(perception_results_all, experiment_logs_all, color_palette):
    """
    Plots longitudinal trends of miss rate, angular accuracy, distance accuracy,
    and collisions from trial 1 to 216 without confidence interval shading.
    """
    all_trials = []

    for subject_id, df in perception_results_all.items():
        if df is None or df.empty:
            continue

        logs = experiment_logs_all.get(subject_id)
        df_copy = df.copy()

        perc_angle_col = 'Angle perceived' if 'Angle perceived' in df_copy.columns else 'Perceived angle'
        perc_dist_col = 'Distance perceived' if 'Distance perceived' in df_copy.columns else 'Perceived distance'
        trial_col = 'Trial number' if 'Trial number' in df_copy.columns else 'Trial'

        # Filter out hardware faults (-1). Keep misses (0) and valid hits (>0).
        df_copy = df_copy[df_copy[perc_angle_col] >= 0].copy()

        # Calculate Miss Rate
        df_copy['Is_Missed'] = (df_copy[perc_angle_col] == 0).astype(float)

        # Calculate Accuracies (Filtering out missed trials using NaN)
        df_copy['Is_Hit'] = (df_copy[perc_angle_col] > 0) & (df_copy[perc_dist_col] > 0)

        df_copy['Angular_Accuracy'] = np.where(
            df_copy['Is_Hit'],
            (df_copy['Angle'] == df_copy[perc_angle_col]).astype(float),
            np.nan
        )
        df_copy['Distance_Accuracy'] = np.where(
            df_copy['Is_Hit'],
            (df_copy['Distance'] == df_copy[perc_dist_col]).astype(float),
            np.nan
        )

        # Calculate Collisions per Trial using the logs (Independent of validity)
        if logs is not None and not logs.empty:
            logs_sorted = logs.sort_values('Timestamp').dropna(subset=['Number of collision'])
            df_times = df_copy[[trial_col, 'Phase timestamp']].sort_values('Phase timestamp')

            merged = pd.merge_asof(df_times, logs_sorted[['Timestamp', 'Number of collision']],
                                   left_on='Phase timestamp', right_on='Timestamp', direction='nearest')

            merged['Collisions_in_Trial'] = merged['Number of collision'].diff().shift(-1).fillna(0)
            merged['Collisions_in_Trial'] = merged['Collisions_in_Trial'].clip(lower=0)

            df_copy = pd.merge(df_copy, merged[[trial_col, 'Collisions_in_Trial']], on=trial_col, how='left')
        else:
            df_copy['Collisions_in_Trial'] = np.nan

        df_copy['Trial_Index'] = df_copy[trial_col]
        df_copy['Modality'] = df_copy['Modality'].str.lower()

        all_trials.append(df_copy)

    combined_df = pd.concat(all_trials, ignore_index=True)

    # --- Plotting ---
    sns.set_theme(style="whitegrid", context="paper", font_scale=1.2)
    fig, axes = plt.subplots(4, 1, figsize=(14, 18), sharex=True)

    palette = color_palette
    modality_order = ['auditory', 'haptic', 'visual']

    # Plot 1: Miss Rate (Separated by Modality)
    sns.lineplot(data=combined_df, x='Trial_Index', y='Is_Missed', hue='Modality',
                 hue_order=modality_order, palette=palette, ax=axes[0], errorbar=None, alpha=0.5)

    for mod in modality_order:
        mod_data = combined_df[combined_df['Modality'] == mod].dropna(subset=['Is_Missed'])
        if not mod_data.empty:
            sns.regplot(data=mod_data, x='Trial_Index', y='Is_Missed', scatter=False,
                        color=palette[mod], ax=axes[0], line_kws={'linestyle': '--', 'linewidth': 2})

    axes[0].set_title('Miss Rate Over Time by Modality', fontweight='bold', fontsize=14)
    axes[0].set_ylabel('Miss Rate', fontweight='bold')
    axes[0].set_ylim(-0.05, 1.05)
    axes[0].legend(title='Modality', loc='upper right')

    # Plot 2: Angular Accuracy (Separated by Modality, Valid Only)
    sns.lineplot(data=combined_df, x='Trial_Index', y='Angular_Accuracy', hue='Modality',
                 hue_order=modality_order, palette=palette, ax=axes[1], errorbar=None, alpha=0.5)

    for mod in modality_order:
        mod_data = combined_df[combined_df['Modality'] == mod].dropna(subset=['Angular_Accuracy'])
        if not mod_data.empty:
            sns.regplot(data=mod_data, x='Trial_Index', y='Angular_Accuracy', scatter=False,
                        color=palette[mod], ax=axes[1], line_kws={'linestyle': '--', 'linewidth': 2})

    axes[1].set_title('Angular Accuracy Over Time by Modality (Valid Trials Only)', fontweight='bold', fontsize=14)
    axes[1].set_ylabel('Accuracy Rate', fontweight='bold')
    axes[1].set_ylim(0, 1.05)
    axes[1].legend(title='Modality', loc='lower right')

    # Plot 3: Distance Accuracy (Separated by Modality, Valid Only)
    sns.lineplot(data=combined_df, x='Trial_Index', y='Distance_Accuracy', hue='Modality',
                 hue_order=modality_order, palette=palette, ax=axes[2], errorbar=None, alpha=0.5)

    for mod in modality_order:
        mod_data = combined_df[combined_df['Modality'] == mod].dropna(subset=['Distance_Accuracy'])
        if not mod_data.empty:
            sns.regplot(data=mod_data, x='Trial_Index', y='Distance_Accuracy', scatter=False,
                        color=palette[mod], ax=axes[2], line_kws={'linestyle': '--', 'linewidth': 2})

    axes[2].set_title('Radial Distance Accuracy Over Time by Modality (Valid Trials Only)', fontweight='bold', fontsize=14)
    axes[2].set_ylabel('Accuracy Rate', fontweight='bold')
    axes[2].set_ylim(0, 1.05)
    axes[2].legend(title='Modality', loc='lower right')

    # Plot 4: Collisions (Combined, All Trials)
    sns.lineplot(data=combined_df, x='Trial_Index', y='Collisions_in_Trial',
                 color='#333333', ax=axes[3], errorbar=None, alpha=0.5)

    col_data = combined_df.dropna(subset=['Collisions_in_Trial'])
    if not col_data.empty:
        sns.regplot(data=col_data, x='Trial_Index', y='Collisions_in_Trial', scatter=False,
                    color='#333333', ax=axes[3], line_kws={'linestyle': '--', 'linewidth': 2})

    axes[3].set_title('Average Collisions per Trial Over Time (All Modalities & Trials)', fontweight='bold', fontsize=14)
    axes[3].set_ylabel('Number of Collisions')
    axes[3].set_xlabel('Experiment Timeline (Trial 1 to 216)', fontweight='bold')

    # Add Phase Markers across all four subplots
    for ax in axes:
        ax.axvline(x=72.5, color='gray', linestyle=':', alpha=0.7)
        ax.axvline(x=144.5, color='gray', linestyle=':', alpha=0.7)

        y_min, y_max = ax.get_ylim()
        y_pos = y_min + 0.05 * (y_max - y_min)
        ax.text(36, y_pos, 'Phase 1', ha='center', va='bottom', color='gray', fontsize=10)
        ax.text(108, y_pos, 'Phase 2', ha='center', va='bottom', color='gray', fontsize=10)
        ax.text(180, y_pos, 'Phase 3', ha='center', va='bottom', color='gray', fontsize=10)

    plt.tight_layout()
    plt.show()

    return combined_df


def plot_performance_by_condition(perception_results_all, experiment_logs_all, color_palette, axes=None):
    """
    Calculates subject-level performance metrics broken down by Modality and Difficulty.
    Plots them in a 2x4 grid, annotating all with paired Wilcoxon signed-rank p-values.
    """
    # --- Part A: Extract Modality & Difficulty Metrics ---
    mod_metrics = []
    diff_metrics = []

    for subject, df in perception_results_all.items():
        if df is None or df.empty:
            continue

        df_copy = df.copy()
        perc_angle_col = 'Angle perceived' if 'Angle perceived' in df_copy.columns else 'Perceived angle'
        perc_dist_col = 'Distance perceived' if 'Distance perceived' in df_copy.columns else 'Perceived distance'
        dist_col = 'Distance' if 'Distance' in df_copy.columns else 'Distnce'

        # Filter out hardware faults (-1)
        df_copy = df_copy[df_copy[perc_angle_col] >= 0].copy()

        if 'Modality' in df_copy.columns:
            df_copy['Modality'] = df_copy['Modality'].astype(str).str.strip().str.capitalize()
        if 'Difficulty level' in df_copy.columns:
            df_copy['Difficulty level'] = df_copy['Difficulty level'].astype(str).str.strip().str.capitalize()

        # 1. Extract Modality Metrics
        for mod in ['Visual', 'Auditory', 'Haptic']:
            if 'Modality' not in df_copy.columns: break
            mod_df = df_copy[df_copy['Modality'] == mod]
            if mod_df.empty: continue

            miss_rate = (mod_df[perc_angle_col] == 0).mean()
            valid_trials = mod_df[(mod_df[perc_angle_col] > 0) & (mod_df[perc_dist_col] > 0)]

            if not valid_trials.empty:
                ang_acc = (valid_trials['Angle'] == valid_trials[perc_angle_col]).mean()
                dist_acc = (valid_trials[dist_col] == valid_trials[perc_dist_col]).mean()
                total_acc = ((valid_trials['Angle'] == valid_trials[perc_angle_col]) &
                             (valid_trials[dist_col] == valid_trials[perc_dist_col])).mean()
            else:
                ang_acc, dist_acc, total_acc = np.nan, np.nan, np.nan

            mod_metrics.append({'Subject': subject, 'Modality': mod, 'Miss Rate': miss_rate,
                                'Angular Accuracy': ang_acc, 'Distance Accuracy': dist_acc,
                                'Total Accuracy': total_acc})

        # 2. Extract Difficulty Metrics (Including Total Accuracy)
        for diff in ['Easy', 'Medium', 'Hard']:
            if 'Difficulty level' not in df_copy.columns: break
            diff_df = df_copy[df_copy['Difficulty level'] == diff]
            if diff_df.empty: continue

            miss_rate = (diff_df[perc_angle_col] == 0).mean()
            valid_trials = diff_df[(diff_df[perc_angle_col] > 0) & (diff_df[perc_dist_col] > 0)]

            if not valid_trials.empty:
                ang_acc = (valid_trials['Angle'] == valid_trials[perc_angle_col]).mean()
                dist_acc = (valid_trials[dist_col] == valid_trials[perc_dist_col]).mean()
                total_acc = ((valid_trials['Angle'] == valid_trials[perc_angle_col]) &
                             (valid_trials[dist_col] == valid_trials[perc_dist_col])).mean()
            else:
                ang_acc, dist_acc, total_acc = np.nan, np.nan, np.nan

            diff_metrics.append({'Subject': subject, 'Difficulty': diff, 'Miss Rate': miss_rate,
                                 'Angular Accuracy': ang_acc, 'Distance Accuracy': dist_acc,
                                 'Total Accuracy': total_acc})

    df_mod = pd.DataFrame(mod_metrics)
    df_diff = pd.DataFrame(diff_metrics)

    # --- Helper Function for Statistical Annotation (Wilcoxon Signed-Rank) ---
    def annotate_wilcoxon(ax, data, metric, condition_col, pairs, order):
        # Pivot to align subject data into perfectly matched pairs
        pivot_df = data.pivot(index='Subject', columns=condition_col, values=metric)

        y_max = data[metric].max()
        y_range = data[metric].max() - data[metric].min()
        if pd.isna(y_range) or y_range == 0: y_range = 0.1

        # Expand Y-axis to make room for 3 stacked brackets
        ax.set_ylim(ax.get_ylim()[0], ax.get_ylim()[1] + y_range * 0.35)

        for i, (c1, c2) in enumerate(pairs):
            p_text = "N/A"
            if c1 in pivot_df.columns and c2 in pivot_df.columns:
                paired_data = pivot_df[[c1, c2]].dropna()
                if len(paired_data) > 1:
                    # Wilcoxon requires the differences between pairs to be non-zero
                    diffs = paired_data[c1] - paired_data[c2]
                    if not (diffs == 0).all():
                        stat, p = wilcoxon(paired_data[c1], paired_data[c2], alternative='two-sided')
                        p_text = f"p={p:.3f}" if p >= 0.001 else "p<0.001"

            x1 = order.index(c1)
            x2 = order.index(c2)

            # Stack brackets vertically
            bracket_y = y_max + y_range * 0.05 + (i * y_range * 0.1)
            bracket_h = y_range * 0.02
            ax.plot([x1, x1, x2, x2], [bracket_y, bracket_y + bracket_h, bracket_y + bracket_h, bracket_y], lw=1.2,
                    color='k')

            if p_text != "N/A":
                # Safely strip text for float comparison to avoid crashing on 'p<0.001'
                clean_p_val = p_text.replace('p', '').replace('=', '').replace('<', '').strip()
                weight = 'bold' if float(clean_p_val) < 0.05 else 'normal'
            else:
                weight = 'normal'

            ax.text((x1 + x2) / 2, bracket_y + bracket_h, p_text, ha='center', va='bottom', color='k', fontsize=10,
                    fontweight=weight)

    # --- Plotting ---
    sns.set_theme(style="whitegrid", context="paper", font_scale=1.2)
    standalone = axes is None
    if standalone:
        fig, axes = plt.subplots(2, 4, figsize=(24, 12))

    axes = axes.flatten() if standalone else np.array(axes).flatten()

    mod_order = ['Visual', 'Auditory', 'Haptic']
    diff_order = ['Easy', 'Medium', 'Hard']

    palette_mod = {mod: color_palette[mod.lower()] for mod in mod_order}
    palette_diff = {diff: color_palette[diff.lower()] for diff in diff_order}

    mod_pairs = [('Visual', 'Auditory'), ('Auditory', 'Haptic'), ('Visual', 'Haptic')]
    diff_pairs = [('Easy', 'Medium'), ('Medium', 'Hard'), ('Easy', 'Hard')]

    # -----------------------------------------------
    # Plot Row 1 (axes 0-3): Modality Metrics
    # -----------------------------------------------
    modality_metrics = ['Miss Rate', 'Angular Accuracy', 'Distance Accuracy', 'Total Accuracy']
    for i, metric in enumerate(modality_metrics):
        if not df_mod.empty and metric in df_mod.columns:
            sns.boxplot(data=df_mod, x='Modality', y=metric, order=mod_order, palette=palette_mod, ax=axes[i],
                        showmeans=True,
                        meanprops={"marker": "o", "markerfacecolor": "white", "markeredgecolor": "black"})
            sns.stripplot(data=df_mod, x='Modality', y=metric, order=mod_order, palette=palette_mod, ax=axes[i],
                          alpha=0.6, jitter=True, edgecolor='gray', linewidth=0.5)

            axes[i].set_title(f'{metric}\n(by Modality)', fontsize=13)
            axes[i].set_xlabel('')
            # axes[i].set_ylabel(metric, fontweight='bold')

            annotate_wilcoxon(axes[i], df_mod, metric, 'Modality', mod_pairs, mod_order)

    # -----------------------------------------------
    # Plot Row 2 (axes 4-7): Difficulty Metrics
    # -----------------------------------------------
    difficulty_metrics = ['Miss Rate', 'Angular Accuracy', 'Distance Accuracy', 'Total Accuracy']
    for j, metric in enumerate(difficulty_metrics):
        idx = j + 4
        if not df_diff.empty and metric in df_diff.columns:
            sns.boxplot(data=df_diff, x='Difficulty', y=metric, order=diff_order, palette=palette_diff, ax=axes[idx],
                        showmeans=True,
                        meanprops={"marker": "o", "markerfacecolor": "white", "markeredgecolor": "black"})
            sns.stripplot(data=df_diff, x='Difficulty', y=metric, order=diff_order, palette=palette_diff, ax=axes[idx],
                          alpha=0.6, jitter=True, edgecolor='gray', linewidth=0.5)

            axes[idx].set_title(f'{metric}\n(by Difficulty)', fontweight='bold', fontsize=13)
            axes[idx].set_xlabel('')
            axes[idx].set_ylabel(metric, fontweight='bold')

            annotate_wilcoxon(axes[idx], df_diff, metric, 'Difficulty', diff_pairs, diff_order)

    if standalone:
        plt.tight_layout(pad=2.0)
        plt.show()


def plot_performance_by_gender(perception_results_all, experiment_logs_all, demographics_path, color_palette,
                               axes=None):
    """
    Calculates subject-level performance metrics broken down by Modality, Difficulty, and Gender.
    Plots them in a 3x4 grid, annotating all with unpaired Wilcoxon rank-sum p-values
    comparing Male vs Female within each condition. Colors are mapped to Modality/Difficulty.
    Safely handles omitted participants.
    """
    # Fix potential missing hash in color palette if needed
    for key in color_palette:
        if isinstance(color_palette[key], str) and not color_palette[key].startswith('#'):
            color_palette[key] = '#' + color_palette[key]

    # 1. Load demographics to get Gender mapping safely
    demo_df = pd.read_csv(demographics_path)

    # Safely map Subject IDs to avoid length mismatch errors if participants were omitted
    if 'Participant ID' in demo_df.columns:
        demo_df['Subject'] = demo_df['Participant ID'].astype(str).apply(lambda x: x.zfill(2) if len(x) == 1 else x)
    elif 'Folder_Name' in demo_df.columns:
        demo_df['Subject'] = demo_df['Folder_Name'].astype(str)
    else:
        # Fallback: Create IDs based on the original full cohort sequence
        demo_df['Subject'] = [f"{i:02d}" for i in range(1, len(demo_df) + 1)]

    # --- Part A: Extract Modality, Difficulty, and Collision Metrics ---
    mod_metrics = []
    diff_metrics = []
    diff_col_metrics = []
    tot_col_metrics = []
    tot_metrics = []  # Added for Overall Total Accuracy

    for subject, df in perception_results_all.items():
        if df is None or df.empty:
            continue

        df_copy = df.copy()
        perc_angle_col = 'Angle perceived' if 'Angle perceived' in df_copy.columns else 'Perceived angle'
        perc_dist_col = 'Distance perceived' if 'Distance perceived' in df_copy.columns else 'Perceived distance'
        dist_col = 'Distance' if 'Distance' in df_copy.columns else 'Distnce'

        # Filter out hardware faults (-1)
        df_copy = df_copy[df_copy[perc_angle_col] >= 0].copy()

        if 'Modality' in df_copy.columns:
            df_copy['Modality'] = df_copy['Modality'].astype(str).str.strip().str.capitalize()
        if 'Difficulty level' in df_copy.columns:
            df_copy['Difficulty level'] = df_copy['Difficulty level'].astype(str).str.strip().str.capitalize()

        # 1. Extract Modality Metrics
        for mod in ['Visual', 'Auditory', 'Haptic']:
            if 'Modality' not in df_copy.columns: break
            mod_df = df_copy[df_copy['Modality'] == mod]
            if mod_df.empty: continue

            miss_rate = (mod_df[perc_angle_col] == 0).mean()
            valid_trials = mod_df[(mod_df[perc_angle_col] > 0) & (mod_df[perc_dist_col] > 0)]

            if not valid_trials.empty:
                ang_acc = (valid_trials['Angle'] == valid_trials[perc_angle_col]).mean()
                dist_acc = (valid_trials[dist_col] == valid_trials[perc_dist_col]).mean()
                total_acc = ((valid_trials['Angle'] == valid_trials[perc_angle_col]) &
                             (valid_trials[dist_col] == valid_trials[perc_dist_col])).mean()
            else:
                ang_acc, dist_acc, total_acc = np.nan, np.nan, np.nan

            mod_metrics.append({'Subject': subject, 'Modality': mod, 'Miss Rate': miss_rate,
                                'Angular Accuracy': ang_acc, 'Distance Accuracy': dist_acc,
                                'Total Accuracy': total_acc})

        # 2. Extract Difficulty Metrics
        for diff in ['Easy', 'Medium', 'Hard']:
            if 'Difficulty level' not in df_copy.columns: break
            diff_df = df_copy[df_copy['Difficulty level'] == diff]
            if diff_df.empty: continue

            miss_rate = (diff_df[perc_angle_col] == 0).mean()
            valid_trials = diff_df[(diff_df[perc_angle_col] > 0) & (diff_df[perc_dist_col] > 0)]

            if not valid_trials.empty:
                ang_acc = (valid_trials['Angle'] == valid_trials[perc_angle_col]).mean()
                dist_acc = (valid_trials[dist_col] == valid_trials[perc_dist_col]).mean()
                total_acc = ((valid_trials['Angle'] == valid_trials[perc_angle_col]) &
                             (valid_trials[dist_col] == valid_trials[perc_dist_col])).mean()
            else:
                ang_acc, dist_acc, total_acc = np.nan, np.nan, np.nan

            diff_metrics.append({'Subject': subject, 'Difficulty': diff, 'Miss Rate': miss_rate,
                                 'Angular Accuracy': ang_acc, 'Distance Accuracy': dist_acc,
                                 'Total Accuracy': total_acc})

        # 3. Extract OVERALL Total Accuracy Metric
        all_valid = df_copy[(df_copy[perc_angle_col] > 0) & (df_copy[perc_dist_col] > 0)]
        if not all_valid.empty:
            overall_tot_acc = ((all_valid['Angle'] == all_valid[perc_angle_col]) &
                               (all_valid[dist_col] == all_valid[perc_dist_col])).mean()
        else:
            overall_tot_acc = np.nan

        tot_metrics.append({'Subject': subject, 'Total Accuracy': overall_tot_acc})

        # 4. Extract Collision Metrics (Total and Per Phase)
        logs_df = experiment_logs_all.get(subject)
        if logs_df is not None and not logs_df.empty and 'Number of collision' in logs_df.columns:
            valid_logs = logs_df.dropna(subset=['Number of collision']).copy()
            if not valid_logs.empty:
                valid_logs['Number of collision'] = pd.to_numeric(valid_logs['Number of collision'], errors='coerce')

                # Total Collisions
                tot_col = valid_logs['Number of collision'].max() - valid_logs['Number of collision'].min()
                tot_col_metrics.append({'Subject': subject, 'Total Collisions': tot_col})

                # Phase Collisions
                if 'Difficulty level' in valid_logs.columns:
                    valid_logs['Difficulty level'] = valid_logs['Difficulty level'].astype(
                        str).str.strip().str.capitalize()
                    for diff in ['Easy', 'Medium', 'Hard']:
                        diff_logs = valid_logs[valid_logs['Difficulty level'] == diff]
                        if not diff_logs.empty:
                            phase_col = diff_logs['Number of collision'].max() - diff_logs['Number of collision'].min()
                            diff_col_metrics.append({'Subject': subject, 'Difficulty': diff, 'Collisions': phase_col})

    # Prepare and merge DataFrames with Demographics (inner merge automatically drops omitted participants)
    df_mod = pd.DataFrame(mod_metrics)
    if not df_mod.empty:
        df_mod = pd.merge(df_mod, demo_df, on='Subject', how='inner').dropna(subset=['Gender'])
        df_mod['Gender'] = df_mod['Gender'].str.capitalize()
        df_mod['Group'] = df_mod['Modality'] + '\n' + df_mod['Gender']

    df_diff = pd.DataFrame(diff_metrics)
    if not df_diff.empty:
        df_diff = pd.merge(df_diff, demo_df, on='Subject', how='inner').dropna(subset=['Gender'])
        df_diff['Gender'] = df_diff['Gender'].str.capitalize()
        df_diff['Group'] = df_diff['Difficulty'] + '\n' + df_diff['Gender']

    df_tot = pd.DataFrame(tot_metrics)
    if not df_tot.empty:
        df_tot = pd.merge(df_tot, demo_df, on='Subject', how='inner').dropna(subset=['Gender'])
        df_tot['Gender'] = df_tot['Gender'].str.capitalize()
        df_tot['Group'] = df_tot['Gender']

    df_diff_col = pd.DataFrame(diff_col_metrics)
    if not df_diff_col.empty:
        df_diff_col = pd.merge(df_diff_col, demo_df, on='Subject', how='inner').dropna(subset=['Gender'])
        df_diff_col['Gender'] = df_diff_col['Gender'].str.capitalize()
        df_diff_col['Group'] = df_diff_col['Difficulty'] + '\n' + df_diff_col['Gender']

    df_tot_col = pd.DataFrame(tot_col_metrics)
    if not df_tot_col.empty:
        df_tot_col = pd.merge(df_tot_col, demo_df, on='Subject', how='inner').dropna(subset=['Gender'])
        df_tot_col['Gender'] = df_tot_col['Gender'].str.capitalize()
        df_tot_col['Group'] = df_tot_col['Gender']

    # --- Helper Function for Statistical Annotation (Wilcoxon Rank-Sum Unpaired) ---
    def annotate_wilcoxon_unpaired(ax, data, metric, pairs, order):
        y_max = data[metric].max()
        y_min = data[metric].min()
        y_range = y_max - y_min
        if pd.isna(y_range) or y_range == 0: y_range = 0.1

        # Expand Y-axis to make room for brackets
        ax.set_ylim(ax.get_ylim()[0], ax.get_ylim()[1] + y_range * 0.2)

        for g1, g2 in pairs:
            p_text = "N/A"
            d1 = data[data['Group'] == g1][metric].dropna()
            d2 = data[data['Group'] == g2][metric].dropna()

            if len(d1) > 1 and len(d2) > 1:
                # Unpaired Wilcoxon Rank-Sum test
                stat, p = ranksums(d1, d2, alternative='two-sided')

                if p < 0.001:
                    p_text = "*\np<0.001"
                else:
                    p_text = f"p={p:.3f}"

            x1 = order.index(g1)
            x2 = order.index(g2)

            bracket_y = y_max + y_range * 0.05
            bracket_h = y_range * 0.02
            ax.plot([x1, x1, x2, x2], [bracket_y, bracket_y + bracket_h, bracket_y + bracket_h, bracket_y], lw=1.2,
                    color='k')

            if p_text != "N/A":
                # Safely parse text for float comparison
                if "<" in p_text:
                    weight = 'bold'
                else:
                    clean_p_val = float(p_text.split('=')[-1])
                    weight = 'bold' if clean_p_val < 0.05 else 'normal'
            else:
                weight = 'normal'

            ax.text((x1 + x2) / 2, bracket_y + bracket_h, p_text, ha='center', va='bottom', color='k', fontsize=10,
                    fontweight=weight)

    # --- Plotting ---
    sns.set_theme(style="whitegrid", context="paper", font_scale=1.2)
    standalone = axes is None
    if standalone:
        fig, axes = plt.subplots(3, 4, figsize=(24, 18))

    axes = axes.flatten() if standalone else np.array(axes).flatten()

    mod_order = ['Visual\nMale', 'Visual\nFemale', 'Auditory\nMale', 'Auditory\nFemale', 'Haptic\nMale',
                 'Haptic\nFemale']
    diff_order = ['Easy\nMale', 'Easy\nFemale', 'Medium\nMale', 'Medium\nFemale', 'Hard\nMale', 'Hard\nFemale']

    # Map colors strictly to Modality and Difficulty (using [0] to extract the condition, ignoring gender)
    palette_mod = {group: color_palette[group.split('\n')[0].lower()] for group in mod_order}
    palette_diff = {group: color_palette[group.split('\n')[0].lower()] for group in diff_order}

    mod_pairs = [('Visual\nMale', 'Visual\nFemale'), ('Auditory\nMale', 'Auditory\nFemale'),
                 ('Haptic\nMale', 'Haptic\nFemale')]
    diff_pairs = [('Easy\nMale', 'Easy\nFemale'), ('Medium\nMale', 'Medium\nFemale'), ('Hard\nMale', 'Hard\nFemale')]

    # -----------------------------------------------
    # Plot Row 1 (axes 0-3): Modality Metrics
    # -----------------------------------------------
    modality_metrics = ['Miss Rate', 'Angular Accuracy', 'Distance Accuracy', 'Total Accuracy']
    for i, metric in enumerate(modality_metrics):
        if not df_mod.empty and metric in df_mod.columns:
            sns.boxplot(data=df_mod, x='Group', y=metric, order=mod_order, palette=palette_mod, ax=axes[i],
                        showmeans=True,
                        meanprops={"marker": "o", "markerfacecolor": "white", "markeredgecolor": "black"})
            sns.stripplot(data=df_mod, x='Group', y=metric, order=mod_order, palette=palette_mod, ax=axes[i],
                          alpha=0.6, jitter=True, edgecolor='gray', linewidth=0.5)

            axes[i].set_title(f'{metric}\n(Gender & Modality)', fontweight='bold', fontsize=13)
            axes[i].set_xlabel('')
            axes[i].set_ylabel(metric, fontweight='bold')

            axes[i].axvline(1.5, color='gray', linestyle=':', alpha=0.7)
            axes[i].axvline(3.5, color='gray', linestyle=':', alpha=0.7)

            annotate_wilcoxon_unpaired(axes[i], df_mod, metric, mod_pairs, mod_order)

    # -----------------------------------------------
    # Plot Row 2 (axes 4-7): Difficulty Metrics
    # -----------------------------------------------
    difficulty_metrics = ['Miss Rate', 'Angular Accuracy', 'Distance Accuracy', 'Total Accuracy']
    for j, metric in enumerate(difficulty_metrics):
        idx = j + 4
        if not df_diff.empty and metric in df_diff.columns:
            sns.boxplot(data=df_diff, x='Group', y=metric, order=diff_order, palette=palette_diff, ax=axes[idx],
                        showmeans=True,
                        meanprops={"marker": "o", "markerfacecolor": "white", "markeredgecolor": "black"})
            sns.stripplot(data=df_diff, x='Group', y=metric, order=diff_order, palette=palette_diff, ax=axes[idx],
                          alpha=0.6, jitter=True, edgecolor='gray', linewidth=0.5)

            axes[idx].set_title(f'{metric}\n(Gender & Difficulty)', fontweight='bold', fontsize=13)
            axes[idx].set_xlabel('')
            axes[idx].set_ylabel(metric, fontweight='bold')

            axes[idx].axvline(1.5, color='gray', linestyle=':', alpha=0.7)
            axes[idx].axvline(3.5, color='gray', linestyle=':', alpha=0.7)

            annotate_wilcoxon_unpaired(axes[idx], df_diff, metric, diff_pairs, diff_order)

    # -----------------------------------------------
    # Plot Row 3 (axes 8-10): Collisions & Overall Accuracy
    # -----------------------------------------------
    # Subplot 8: Phase Collisions
    if not df_diff_col.empty:
        sns.boxplot(data=df_diff_col, x='Group', y='Collisions', order=diff_order, palette=palette_diff, ax=axes[8],
                    showmeans=True, meanprops={"marker": "o", "markerfacecolor": "white", "markeredgecolor": "black"})
        sns.stripplot(data=df_diff_col, x='Group', y='Collisions', order=diff_order, palette=palette_diff, ax=axes[8],
                      alpha=0.6, jitter=True, edgecolor='gray', linewidth=0.5)

        axes[8].set_title('Phase Collisions\n(Gender & Difficulty)', fontweight='bold', fontsize=13)
        axes[8].set_xlabel('')
        axes[8].set_ylabel('Collisions', fontweight='bold')

        axes[8].axvline(1.5, color='gray', linestyle=':', alpha=0.7)
        axes[8].axvline(3.5, color='gray', linestyle=':', alpha=0.7)

        annotate_wilcoxon_unpaired(axes[8], df_diff_col, 'Collisions', diff_pairs, diff_order)

    gen_order = ['Male', 'Female']
    palette_gen = {'Male': color_palette['male'], 'Female': color_palette['female']}
    gen_pairs = [('Male', 'Female')]

    # Subplot 9: Total Collisions by Gender
    if not df_tot_col.empty:
        sns.boxplot(data=df_tot_col, x='Group', y='Total Collisions', order=gen_order, palette=palette_gen, ax=axes[9],
                    showmeans=True, width=0.4,
                    meanprops={"marker": "o", "markerfacecolor": "white", "markeredgecolor": "black"})
        sns.stripplot(data=df_tot_col, x='Group', y='Total Collisions', order=gen_order, palette=palette_gen,
                      ax=axes[9],
                      alpha=0.6, jitter=True, edgecolor='gray', linewidth=0.5)

        axes[9].set_title('Total Collisions\n(by Gender)', fontweight='bold', fontsize=13)
        axes[9].set_xlabel('')
        axes[9].set_ylabel('Total Collisions', fontweight='bold')

        annotate_wilcoxon_unpaired(axes[9], df_tot_col, 'Total Collisions', gen_pairs, gen_order)

    # Subplot 10: Overall Total Accuracy by Gender
    if not df_tot.empty:
        sns.boxplot(data=df_tot, x='Group', y='Total Accuracy', order=gen_order, palette=palette_gen, ax=axes[10],
                    showmeans=True, width=0.4,
                    meanprops={"marker": "o", "markerfacecolor": "white", "markeredgecolor": "black"})
        sns.stripplot(data=df_tot, x='Group', y='Total Accuracy', order=gen_order, palette=palette_gen, ax=axes[10],
                      alpha=0.6, jitter=True, edgecolor='gray', linewidth=0.5)

        axes[10].set_title('Overall Total Accuracy\n(by Gender)', fontweight='bold', fontsize=13)
        axes[10].set_xlabel('')
        axes[10].set_ylabel('Total Accuracy', fontweight='bold')

        annotate_wilcoxon_unpaired(axes[10], df_tot, 'Total Accuracy', gen_pairs, gen_order)

    # Clean up empty subplots
    if standalone:
        fig.delaxes(axes[11])  # Remove the 12th slot

        plt.tight_layout(pad=2.0)
        plt.show()


def plot_analysis_dashboard(
    windows_list,
    perception_results_all,
    experiment_logs_all,
    error_distribution,
    demographics_path,
    color_palette,
):
    """
    Combines seven standalone analysis plots into a single dashboard figure,
    each rendered as its own row of subplots:

      1. plot_timing_metrics                   (2 subplots)
      2. plot_multiple_collision_time_windows  (3 stacked subplots)
      3. plot_error_boxplots_temp              (1 subplot)
      4. analyze_attention_redistribution      (1 subplot)
      5. plot_collision_vs_accuracy            (1 subplot)
      6. test_mrt_interaction                  (3 subplots)
      7. plot_gender_differences_by_modality   (4 subplots)

    `perception_results_all` is the per-trial perception data (dict keyed by
    subject) and `experiment_logs_all` is the continuous per-subject
    experiment log data. These are the same dictionaries you already pass to
    the individual functions elsewhere (previously known as
    `subjects_data_trials` and `subjects_data_full`, respectively).

    `color_palette` is the shared {'visual': ..., 'auditory': ..., 'haptic':
    ...} color mapping (defined under `__main__`) used consistently across
    every modality-colored plot in this dashboard.

    Each row is built as its own Matplotlib subfigure so every underlying
    function can keep laying out its own axes exactly as it does when called
    on its own.

    Returns a dict with the intermediate DataFrames produced by the
    sub-functions that return data.
    """
    sns.set_theme(style="whitegrid")

    fig = plt.figure(figsize=(22, 42))

    height_ratios = [1, 3, 1, 1, 1, 1, 1.3]
    row_widths = [0.5, 1.00, 1.00, 1.00, 0.4, 0.75, 1.00]

    outer_grid = fig.add_gridspec(7, 100, height_ratios=height_ratios, hspace=0.18)
    subfigs = []

    for row, width in enumerate(row_widths):
        number_columns = int(width * 100)
        start_column = (100 - number_columns) // 2
        end_column = start_column + number_columns
        subfigs.append(fig.add_subfigure(outer_grid[row, start_column:end_column]))
    # 1. Response/reaction timing by modality
    axes0 = subfigs[0].subplots(1, 2)
    plot_timing_metrics(perception_results_all, color_palette, axes=axes0)
    subfigs[0].suptitle('Response and Reaction Time by Modality', fontweight='bold', fontsize=14)

    # 2. Collisions across time windows (3 stacked rows)
    axes1 = subfigs[1].subplots(3, 1, sharex=True, sharey=True)
    plot_multiple_collision_time_windows(windows_list, experiment_logs_all, perception_results_all, color_palette, axes=axes1)
    subfigs[1].suptitle('Collisions Across Time Windows by Modality', fontweight='bold', fontsize=14)

    # 3. Error distribution boxplots
    ax2 = subfigs[2].subplots(1, 1)
    plot_error_boxplots_temp(error_distribution, color_palette, ax=ax2)
    subfigs[2].suptitle('Error Distribution by Modality', fontweight='bold', fontsize=14)

    # 4. Attention redistribution across difficulty levels
    demographics = pd.read_csv(demographics_path)

    axes3 = subfigs[3].subplots(1, 3, sharex=True, sharey=True)
    attention_df = analyze_attention_redistribution(perception_results_all, experiment_logs_all, demographics,axes=axes3)
    subfigs[3].suptitle('Attention Allocation Across Difficulty Levels', fontweight='bold', fontsize=14)

    # 5. Collision rate vs. accuracy
    ax4 = subfigs[4].subplots(1, 1)
    collision_acc_df = plot_collision_vs_accuracy(perception_results_all, experiment_logs_all, color_palette, ax=ax4)
    subfigs[4].suptitle('Collision Rate vs. Accuracy by Modality', fontweight='bold', fontsize=14)

    # 6. MRT (Modality x Difficulty) interaction
    axes5 = subfigs[5].subplots(1, 3)
    mrt_df = test_mrt_interaction(perception_results_all, experiment_logs_all, color_palette, axes=axes5)
    subfigs[5].suptitle('Dual-Task Interference: Multiple Resource Theory Evaluation', fontweight='bold', fontsize=14)

    # 7. Gender differences by modality
    axes6 = subfigs[6].subplots(1, 4)
    gender_df, gender_collision_df = plot_gender_differences_by_modality(
        perception_results_all, experiment_logs_all, demographics_path, color_palette, axes=axes6
    )
    subfigs[6].suptitle('Gender Differences by Modality', fontweight='bold', fontsize=14)

    plt.show()
    fig.savefig('comprehensive_results.pdf', format='pdf', bbox_inches='tight')
    return {
        'attention_metrics': attention_df,
        'mrt_interaction': mrt_df,
        'collision_vs_accuracy': collision_acc_df,
        'gender_modality_metrics': gender_df,
        'gender_final_collisions': gender_collision_df,
    }


def plot_gender_differences(perception_results_all, demographics_path):
    """
    Calculates subject-level performance metrics and plots box plots
    comparing Miss Rate, Angular Accuracy, Distance Accuracy, and Overall Accuracy across genders.
    """

    # 1. Load demographics
    demo_df = pd.read_csv(demographics_path)

    subject_metrics = []

    # 2. Iterate through subject data to calculate individual means
    for subject_folder, df in perception_results_all.items():
        if df is None or df.empty:
            continue

        df_copy = df.copy()

        perc_angle_col = 'Angle perceived' if 'Angle perceived' in df_copy.columns else 'Perceived angle'
        perc_dist_col = 'Distance perceived' if 'Distance perceived' in df_copy.columns else 'Perceived distance'

        # Filter out hardware faults (-1)
        df_copy = df_copy[df_copy[perc_angle_col] >= 0].copy()

        # Calculate Miss Rate for this subject
        miss_rate = (df_copy[perc_angle_col] == 0).mean()

        # Calculate Accuracies on valid hits only (> 0)
        valid_trials = df_copy[(df_copy[perc_angle_col] > 0) & (df_copy[perc_dist_col] > 0)]

        if not valid_trials.empty:
            ang_acc = (valid_trials['Angle'] == valid_trials[perc_angle_col]).mean()
            dist_acc = (valid_trials['Distance'] == valid_trials[perc_dist_col]).mean()

            # Overall Accuracy: Both angle and distance are correct on the same trial
            overall_acc = ((valid_trials['Angle'] == valid_trials[perc_angle_col]) &
                           (valid_trials['Distance'] == valid_trials[perc_dist_col])).mean()
        else:
            ang_acc = np.nan
            dist_acc = np.nan
            overall_acc = np.nan

        subject_metrics.append({
            'Folder_Name': subject_folder,
            'Miss Rate': miss_rate,
            'Angular Accuracy': ang_acc,
            'Distance Accuracy': dist_acc,
            'Overall Accuracy': overall_acc
        })

    metrics_df = pd.DataFrame(subject_metrics)

    # 3. Merge metrics with Demographics
    metrics_df = metrics_df.reset_index(drop=True)
    demo_df = demo_df.reset_index(drop=True)

    merged_df = pd.concat([metrics_df, demo_df], axis=1)

    if 'Gender' not in merged_df.columns:
        raise ValueError("The column 'Gender' was not found in the provided Demographics file.")

    merged_df = merged_df.dropna(subset=['Gender'])

    # --- Plotting ---
    sns.set_theme(style="whitegrid", context="paper", font_scale=1.2)

    # Increased to 4 subplots and widened the figure
    fig, axes = plt.subplots(1, 4, figsize=(24, 6))

    metrics_to_plot = ['Miss Rate', 'Angular Accuracy', 'Distance Accuracy', 'Overall Accuracy']

    for i, metric in enumerate(metrics_to_plot):
        sns.boxplot(
            data=merged_df,
            x='Gender',
            y=metric,
            ax=axes[i],
            palette="Set2",
            width=0.4,
            showmeans=True,
            meanprops={
                "marker": "o",
                "markerfacecolor": "white",
                "markeredgecolor": "black",
                "markersize": "8"
            }
        )

        sns.stripplot(
            data=merged_df,
            x='Gender',
            y=metric,
            ax=axes[i],
            color=".3",
            alpha=0.6,
            jitter=True
        )

        axes[i].set_title(f'{metric}\nby Gender', fontweight='bold', fontsize=14)
        axes[i].set_xlabel('Gender', fontweight='bold')
        axes[i].set_ylabel(f'Mean {metric}', fontweight='bold')

    plt.tight_layout(pad=3.0)
    plt.show()

    return merged_df


def test_gender_differences(merged_df, metrics_to_test=None):
    """
    Performs pairwise Mann-Whitney U tests (Wilcoxon rank-sum) between genders
    for specified metrics and prints the results.
    """
    # Updated default to include Overall Accuracy
    if metrics_to_test is None:
        metrics_to_test = ['Miss Rate', 'Angular Accuracy', 'Distance Accuracy', 'Overall Accuracy']

    if 'Gender' not in merged_df.columns:
        print("Error: The column 'Gender' is missing from the DataFrame.")
        return

    unique_genders = merged_df['Gender'].dropna().unique()

    print("\n" + "=" * 60)
    print("STATISTICAL SIGNIFICANCE (Wilcoxon Rank-Sum / Mann-Whitney U)")
    print("=" * 60)

    if len(unique_genders) < 2:
        print("Not enough gender categories to perform pairwise tests.")
        print("=" * 60 + "\n")
        return

    for metric in metrics_to_test:
        if metric not in merged_df.columns:
            print(f"\n--- {metric} ---")
            print("Metric not found in DataFrame. Skipping.")
            continue

        print(f"\n--- {metric} ---")

        for g1, g2 in combinations(unique_genders, 2):
            data_g1 = merged_df[merged_df['Gender'] == g1][metric].dropna()
            data_g2 = merged_df[merged_df['Gender'] == g2][metric].dropna()

            if len(data_g1) > 0 and len(data_g2) > 0:
                stat, p_val = mannwhitneyu(data_g1, data_g2, alternative='two-sided')

                significance = "Significant (p < 0.05) *" if p_val < 0.05 else "Not Significant"
                print(f"{g1} vs {g2}:")
                print(f"  n: ({len(data_g1)} vs {len(data_g2)}) | U-Statistic: {stat:.2f} | p-value: {p_val:.4f}")
                print(f"  Result: {significance}")
            else:
                print(f"{g1} vs {g2}: Insufficient data for testing (n=0 for one or both groups).")

    print("=" * 60 + "\n")


def plot_polar_accuracy_by_modality(perception_results_all, color_palette, ax=None):
    """
    Calculates the Polar Accuracy for each trial based on Euclidean distance,
    aggregates by subject, and plots the distribution by Modality.
    Annotated with paired Wilcoxon signed-rank p-values comparing modalities.
    """
    # 1. Safely combine perception data while preserving Participant ID
    df_list = []
    for pid, df in perception_results_all.items():
        if df is not None and not df.empty:
            df_copy = df.copy()
            df_copy['Participant ID'] = pid
            df_list.append(df_copy)

    df_all = pd.concat(df_list, ignore_index=True)

    perc_angle_col = 'Angle perceived' if 'Angle perceived' in df_all.columns else 'Perceived angle'
    perc_dist_col = 'Distance perceived' if 'Distance perceived' in df_all.columns else 'Perceived distance'
    dist_col = 'Distance' if 'Distance' in df_all.columns else 'Distnce'

    # Filter out misses (0) and hardware faults (-1)
    valid_df = df_all[df_all[perc_angle_col] > 0].copy()
    valid_df['Modality'] = valid_df['Modality'].str.capitalize()

    # 2. Calculate Polar Accuracy
    # Convert angles to radians
    theta_true = valid_df['Angle'] * (np.pi / 4)
    theta_perc = valid_df[perc_angle_col] * (np.pi / 4)
    r_true = valid_df[dist_col]
    r_perc = valid_df[perc_dist_col]

    # Law of Cosines (Euclidean Distance in Polar Coordinates)
    valid_df['Geometric_Error'] = np.sqrt(
        r_true ** 2 + r_perc ** 2 - 2 * r_true * r_perc * np.cos(theta_true - theta_perc)
    )

    # Convert to Accuracy Percentage
    # Max possible Euclidean error is 2 * max_radius (opposite ends of the space)
    r_max = max(r_true.max(), r_perc.max())
    max_possible_error = 2 * r_max
    valid_df['Polar_Accuracy'] = 100 * (1 - (valid_df['Geometric_Error'] / max_possible_error))

    # 3. Aggregate to subject-level means
    subject_means = valid_df.groupby(['Participant ID', 'Modality'])['Polar_Accuracy'].mean().reset_index()

    modality_order = ['Visual', 'Auditory', 'Haptic']
    palette_mod = {mod: color_palette[mod.lower()] for mod in modality_order}

    # --- Calculate P-Values: Wilcoxon Signed-Rank (Paired) ---
    wilcoxon_records = []
    pairs_to_test = [('Visual', 'Auditory'), ('Auditory', 'Haptic'), ('Visual', 'Haptic')]
    num_comparisons = len(pairs_to_test)

    print("\n" + "=" * 60)
    print("WILCOXON SIGNED-RANK (PAIRED) POLAR ACCURACY")
    print("=" * 60)

    # Pivot to align subjects for paired testing
    pivot_df = subject_means.pivot(index='Participant ID', columns='Modality', values='Polar_Accuracy').dropna()

    for mod1, mod2 in pairs_to_test:
        if mod1 in pivot_df.columns and mod2 in pivot_df.columns:
            paired_data = pivot_df[[mod1, mod2]].dropna()

            if len(paired_data) > 1:
                stat, raw_p = wilcoxon(paired_data[mod1], paired_data[mod2], alternative='two-sided')
                bonferroni_p = min(raw_p * num_comparisons, 1.0)
                wilcoxon_records.append({
                    'Comparison': f"{mod1} vs {mod2}",
                    'Bonferroni p': bonferroni_p
                })
                print(
                    f"{mod1:<8} vs {mod2:<8} | N={len(paired_data):<2} | Raw p={raw_p:.4f} | Bonf p={bonferroni_p:.4f}")
            else:
                print(f"{mod1:<8} vs {mod2:<8} | Insufficient data.")

    print("=" * 60 + "\n")
    wilcoxon_df = pd.DataFrame(wilcoxon_records)

    # --- Plotting ---
    sns.set_theme(style="whitegrid", context="paper", font_scale=1.2)
    standalone = ax is None
    if standalone:
        fig, ax = plt.subplots(figsize=(8, 6))

    sns.boxplot(data=subject_means, x='Modality', y='Polar_Accuracy', order=modality_order,
                palette=palette_mod, ax=ax, showfliers=False, width=0.5,
                showmeans=True, meanprops={"marker": "o", "markerfacecolor": "white", "markeredgecolor": "black"})

    sns.stripplot(data=subject_means, x='Modality', y='Polar_Accuracy', order=modality_order,
                  palette=palette_mod, ax=ax, alpha=0.6, jitter=True, edgecolor='gray', linewidth=0.5)

    ax.set_title('Polar Accuracy by Modality', fontweight='bold', fontsize=14, pad=20)
    ax.set_ylabel('Mean Polar Accuracy (%)', fontweight='bold')
    ax.set_xlabel('')

    # Annotate Stats
    ylim_max = subject_means['Polar_Accuracy'].max()
    ylim_min = subject_means['Polar_Accuracy'].min()
    y_range = ylim_max - ylim_min
    if pd.isna(y_range) or y_range == 0: y_range = 10.0

    # Expand Y-axis slightly for brackets
    ax.set_ylim(max(0, ylim_min - y_range * 0.1), ylim_max + (y_range * 0.35))
    y_base = ylim_max + (y_range * 0.05)
    y_step = y_range * 0.08

    for i, (mod1, mod2) in enumerate(pairs_to_test):
        match = wilcoxon_df[wilcoxon_df['Comparison'] == f"{mod1} vs {mod2}"]
        if match.empty:
            continue

        bonferroni_p = match['Bonferroni p'].values[0]
        if bonferroni_p < 0.001:
            p_text = "p < 0.001"
        elif bonferroni_p < 0.05:
            p_text = f"p = {bonferroni_p:.3f}"
        else:
            p_text = f"p = {bonferroni_p:.2f}"

        x1 = modality_order.index(mod1)
        x2 = modality_order.index(mod2)

        y = y_base + (i * y_step)
        h = y_range * 0.02

        ax.plot([x1, x1, x2, x2], [y, y + h, y + h, y], lw=1.5, color='black')

        weight = 'bold' if bonferroni_p < 0.05 else 'normal'
        ax.text((x1 + x2) * 0.5, y + h + (y_range * 0.01), p_text,
                ha='center', va='bottom', color='black', fontsize=11, fontweight=weight)

    if standalone:
        plt.tight_layout()
        plt.show()









def plot_modality_spider_chart(perception_results_all, color_palette, save_path=None):
    """
    Plots a publication-ready radar chart comparing 5 normalized metrics.
    Optionally saves the figure at 300 DPI.
    """
    # 1. Safely combine data
    df_list = []
    for pid, df in perception_results_all.items():
        if df is not None and not df.empty:
            df_copy = df.copy()
            df_list.append(df_copy)

    df_all = pd.concat(df_list, ignore_index=True)

    df_all['Modality'] = df_all['Modality'].str.lower()
    perc_angle_col = 'Angle perceived' if 'Angle perceived' in df_all.columns else 'Perceived angle'
    perc_dist_col = 'Distance perceived' if 'Distance perceived' in df_all.columns else 'Perceived distance'

    clean_df = df_all[df_all[perc_angle_col] != -1].copy()
    clean_df['Reaction time'] = clean_df['Response start'] - clean_df['Phase timestamp']
    clean_df['Response duration'] = clean_df['Response end'] - clean_df['Response start']

    modalities = ['auditory', 'haptic', 'visual']
    metrics_data = {mod: [] for mod in modalities}

    # Upper limits for normalization (Adjust based on your session maximums)
    MAX_REACTION_TIME = 8.52  # seconds
    MAX_RESPONSE_DURATION = 8.88  # seconds

    for mod in modalities:
        mod_df = clean_df[clean_df['Modality'] == mod]

        if mod_df.empty:
            metrics_data[mod] = [0, 0, 0, 0, 0]
            continue

        # 1. Detection Rate (Replaces 'Not Missing Rate')
        detection_rate = (mod_df[perc_angle_col] != 0).mean()

        valid_hits = mod_df[mod_df[perc_angle_col] > 0]

        if not valid_hits.empty:
            angular_acc = (valid_hits['Angle'] == valid_hits[perc_angle_col]).mean()
            distance_acc = (valid_hits['Distance'] == valid_hits[perc_dist_col]).mean()
            mean_rt = valid_hits['Reaction time'].mean()
            mean_resp = valid_hits['Response duration'].mean()
        else:
            angular_acc, distance_acc, mean_rt, mean_resp = 0, 0, MAX_REACTION_TIME, MAX_RESPONSE_DURATION

        # Convert times to "Speed" (1.0 = instant, 0.0 = hits MAX threshold)
        reaction_speed = np.clip(1.0 - (mean_rt / MAX_REACTION_TIME), 0, 1)
        response_speed = np.clip(1.0 - (mean_resp / MAX_RESPONSE_DURATION), 0, 1)

        metrics_data[mod] = [
            angular_acc,
            distance_acc,
            detection_rate,
            reaction_speed,
            response_speed
        ]

    # --- Publication Plot Formatting ---
    # Configure categories with clean line breaks
    categories = [
        'Angular\nAccuracy',
        'Distance\nAccuracy',
        'Detection\nRate',
        'Reaction Speed\n(Norm.)',
        'Response Speed\n(Norm.)'
    ]
    N = len(categories)
    angles = [n / float(N) * 2 * pi for n in range(N)]
    angles += angles[:1]

    # Set universal font parameters for academic plotting
    plt.rcParams.update({'font.size': 12, 'axes.linewidth': 1.2})
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

    # Shift the radial labels so they don't intersect the data lines
    ax.set_theta_offset(pi / 2)
    ax.set_theta_direction(-1)

    for mod in modalities:
        values = metrics_data[mod]
        values += values[:1]

        # Plot lines with clearly defined markers
        ax.plot(angles, values, linewidth=2.5, linestyle='solid',
                label=mod.capitalize(), color=color_palette[mod],
                marker='o', markersize=8, markeredgecolor='white', markeredgewidth=1.5, zorder=3)

        # Fill area
        ax.fill(angles, values, alpha=0.15, color=color_palette[mod], zorder=2)

    # Configure axes
    plt.xticks(angles[:-1], categories, size=12, fontweight='bold', color='#333333')

    # Configure concentric circles (Y-ticks)
    ax.set_rlabel_position(22.5)  # Angle the y-tick labels slightly off-center
    plt.yticks([0.2, 0.4, 0.6, 0.8, 1.0], ["0.2", "0.4", "0.6", "0.8", "1.0"],
               color="#666666", size=10, zorder=1)
    plt.ylim(0, 1.0)

    # Clean up grid and spines
    ax.grid(color='#DDDDDD', linestyle='--', linewidth=1.2, zorder=0)
    ax.spines['polar'].set_visible(False)

    # Legend formatting
    legend = ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.15),
                       title='Modality', frameon=False, ncol=3,
                       fontsize=12, title_fontsize=13)
    legend.get_title().set_fontweight('bold')

    plt.tight_layout()

    # Save high-res for publication if path provided (e.g., 'spider_chart.pdf')
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight', format=save_path.split('.')[-1])
        print(f"Figure saved to {save_path}")

    plt.show()

    return metrics_data


def plot_stitched_collision_timeline_with_metric(experiment_logs_all, bin_size=5, time_col='Timestamp',
                                                 color='#DD8452', deviation_percent = 5):
    """
    Plots two subplots:
    1. Overall continuous cumulative collisions up to 2160s (drops incomplete final bins).
    2. Phase-specific collisions separated by Easy, Medium, and Hard, restricted to 0-720s.
    Both include linear baselines, Adaptation Index, Peak metrics, and Pearson correlation.
    """
    overall_records = []
    diff_records = []

    # Standardize difficulty colors
    diff_colors = {'easy': '#2ECC71', 'medium': '#F1C40F', 'hard': '#E74C3C'}

    for pid, logs_df in experiment_logs_all.items():
        if logs_df is None or logs_df.empty:
            continue

        df = logs_df.copy()

        if time_col not in df.columns or "Number of collision" not in df.columns:
            continue

        df[time_col] = pd.to_numeric(df[time_col], errors='coerce')
        df["Number of collision"] = pd.to_numeric(df["Number of collision"], errors='coerce')
        df = df.dropna(subset=[time_col, "Number of collision"]).sort_values(by=time_col)

        if df.empty:
            continue

        # =====================================================================
        # 1. OVERALL DATA PROCESSING (Up to 2160s)
        # =====================================================================
        dt = df[time_col].diff().fillna(0)
        median_dt = dt[dt <= 2].median()
        if pd.isna(median_dt):
            median_dt = 0

        dt = dt.apply(lambda x: median_dt if x > 2 else x)
        df['t_active'] = dt.cumsum()

        df['Time_Bin'] = (df['t_active'] // bin_size) * bin_size
        binned_avg = df.groupby('Time_Bin')['Number of collision'].mean()

        if not binned_avg.empty:
            max_t_active = df['t_active'].max()
            max_bin = df['Time_Bin'].max()

            # Check if the final bin is incomplete
            if (max_t_active - max_bin) < bin_size:
                max_bin -= bin_size

            if max_bin >= 0:
                all_bins = np.arange(0, max_bin + bin_size, bin_size)
                binned_avg = binned_avg.reindex(all_bins).ffill().fillna(0)

                for t_bin, avg_val in binned_avg.items():
                    if t_bin <= 2160:
                        overall_records.append({
                            'Participant ID': pid,
                            'Time (s)': t_bin,
                            'Cumulative Collisions': avg_val
                        })

        # =====================================================================
        # 2. DIFFICULTY LEVEL DATA PROCESSING (Restricted to 720s)
        # =====================================================================
        if 'Difficulty level' in df.columns:
            df['Difficulty level'] = df['Difficulty level'].astype(str).str.strip().str.lower()

            for diff in ['easy', 'medium', 'hard']:
                diff_df = df[df['Difficulty level'] == diff].copy()
                if diff_df.empty:
                    continue

                diff_dt = diff_df[time_col].diff().fillna(0)
                diff_median_dt = diff_dt[diff_dt <= 2].median()
                if pd.isna(diff_median_dt):
                    diff_median_dt = 0

                diff_dt = diff_dt.apply(lambda x: diff_median_dt if x > 2 else x)
                diff_df['phase_time'] = diff_dt.cumsum()

                base_collisions = diff_df['Number of collision'].iloc[0]
                diff_df['phase_collisions'] = diff_df['Number of collision'] - base_collisions

                diff_df['Phase_Time_Bin'] = (diff_df['phase_time'] // bin_size) * bin_size
                diff_binned_avg = diff_df.groupby('Phase_Time_Bin')['phase_collisions'].mean()

                if not diff_binned_avg.empty:
                    diff_max_bin = diff_df['Phase_Time_Bin'].max()
                    diff_all_bins = np.arange(0, diff_max_bin + bin_size, bin_size)
                    diff_binned_avg = diff_binned_avg.reindex(diff_all_bins).ffill().fillna(0)

                    for t_bin, avg_val in diff_binned_avg.items():
                        if t_bin <= 720:
                            diff_records.append({
                                'Participant ID': pid,
                                'Difficulty': diff,
                                'Time (s)': t_bin,
                                'Phase Collisions': avg_val
                            })

    df_overall = pd.DataFrame(overall_records)
    df_diff = pd.DataFrame(diff_records)

    if df_overall.empty:
        print("No valid log data found.")
        return None, None

    # --- Figure Setup ---
    fig, axes = plt.subplots(2, 1, figsize=(12, 13))

    # =====================================================================
    # SUBPLOT 1: OVERALL TIMELINE
    # =====================================================================
    ax1 = axes[0]
    mean_curve = df_overall.groupby('Time (s)')['Cumulative Collisions'].mean().sort_index()
    t_vals = mean_curve.index.values
    y_vals = mean_curve.values

    t_min, t_max = t_vals[0], t_vals[-1]
    y_min, y_max = y_vals[0], y_vals[-1]
    y_linear = np.linspace(y_min, y_max, len(t_vals))

    auc_actual = np.trapz(y_vals, t_vals)
    auc_linear = np.trapz(y_linear, t_vals)

    dev_pct_overall = ((auc_actual - auc_linear) / auc_linear) * 100 if auc_linear > 0 else 0.0

    if dev_pct_overall > deviation_percent:
        conc_overall = "Learning / Adaptation"
    elif dev_pct_overall < -deviation_percent:
        conc_overall = "Fatigue / Degradation"
    else:
        conc_overall = "Steady Rate"

    # Calculate Peak metrics and Pearson correlation
    peak_val_overall = np.max(y_vals)
    peak_time_overall = t_vals[np.argmax(y_vals)]
    corr_overall, _ = pearsonr(t_vals, y_vals) if np.std(y_vals) > 0 else (0.0, 1.0)

    sns.lineplot(data=df_overall, x='Time (s)', y='Cumulative Collisions', errorbar=('ci', 95),
                 color=color, linewidth=2.5, label='Actual Mean Collisions', ax=ax1)

    ax1.plot([t_min, t_max], [y_min, y_max], linestyle='--', color='#444444',
             linewidth=2, label='Steady Baseline (Constant Rate)')

    textstr1 = (f"Overall Adaptation Index: {dev_pct_overall:+.1f}%\n"
                f"Conclusion: {conc_overall}\n"
                f"Pearson r: {corr_overall:.3f}")

    props = dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='gray')
    ax1.text(0.02, 0.95, textstr1, transform=ax1.transAxes, fontsize=11,
             verticalalignment='top', bbox=props, fontweight='bold')

    ax1.set_title(f'Overall Cumulative Collisions ({bin_size}s bins)', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Active Experiment Time (seconds)', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Total Cumulative Collisions', fontsize=11, fontweight='bold')
    ax1.grid(alpha=0.3, linestyle='--')
    ax1.set_xlim(0, 2160)
    ax1.set_ylim(bottom=0)
    ax1.legend(loc='lower right')

    # =====================================================================
    # SUBPLOT 2: PHASE-SPECIFIC TIMELINES
    # =====================================================================
    ax2 = axes[1]
    if not df_diff.empty:
        sns.lineplot(data=df_diff, x='Time (s)', y='Phase Collisions', hue='Difficulty',
                     palette=diff_colors, errorbar=('ci', 95), linewidth=2.5, ax=ax2)

        metrics_text = "Adaptation Index by Phase (0-720s):\n"

        for diff in ['easy', 'medium', 'hard']:
            diff_data = df_diff[df_diff['Difficulty'] == diff]
            if diff_data.empty: continue

            diff_mean = diff_data.groupby('Time (s)')['Phase Collisions'].mean().sort_index()
            t_d = diff_mean.index.values
            y_d = diff_mean.values

            if len(t_d) < 2: continue

            td_min, td_max = t_d[0], t_d[-1]
            yd_min, yd_max = y_d[0], y_d[-1]
            y_d_linear = np.linspace(yd_min, yd_max, len(t_d))

            auc_d_actual = np.trapz(y_d, t_d)
            auc_d_linear = np.trapz(y_d_linear, t_d)

            dev_pct = ((auc_d_actual - auc_d_linear) / auc_d_linear) * 100 if auc_d_linear > 0 else 0.0

            if dev_pct > deviation_percent:
                conc = "Learning"
            elif dev_pct < -deviation_percent:
                conc = "Fatigue"
            else:
                conc = "Steady"

            # Calculate Peak metrics and Pearson correlation for each phase
            peak_val_diff = np.max(y_d)
            peak_time_diff = t_d[np.argmax(y_d)]
            corr_diff, _ = pearsonr(t_d, y_d) if np.std(y_d) > 0 else (0.0, 1.0)

            metrics_text += (f"• {diff.capitalize()}: {dev_pct:+.1f}% ({conc}) | "
                             f"r={corr_diff:.3f}\n")

            ax2.plot([td_min, td_max], [yd_min, yd_max], linestyle='--', color=diff_colors[diff],
                     linewidth=2, alpha=0.8)

        ax2.text(0.02, 0.95, metrics_text.strip(), transform=ax2.transAxes, fontsize=10,
                 verticalalignment='top', bbox=props, fontweight='bold')

        ax2.set_title(f'Collisions Generated Within Phase by Difficulty', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Active Phase Time (seconds)', fontsize=11, fontweight='bold')
        ax2.set_ylabel('Collisions During Phase', fontsize=11, fontweight='bold')
        ax2.grid(alpha=0.3, linestyle='--')

        ax2.set_xlim(0, 720)
        ax2.set_ylim(bottom=0)

        handles, labels = ax2.get_legend_handles_labels()
        ax2.legend(handles[:3], [l.capitalize() for l in labels[:3]], title='Difficulty', loc='lower right')

    plt.tight_layout(pad=3.0)
    plt.savefig('stitched_collision_timelines_subplots.pdf', format='pdf', bbox_inches='tight')
    plt.show()




def analyze_individual_adaptation(experiment_logs_all, bin_size=5, time_col='Timestamp'):
    """
    Plots the individual cumulative collision curves for all participants.
    Calculates the Adaptation Index for each person individually, color-codes
    their curve (Learning, Fatigue, or Steady), and prints the summary counts.
    """
    participant_records = []
    participant_metrics = []

    for pid, logs_df in experiment_logs_all.items():
        if logs_df is None or logs_df.empty:
            continue

        df = logs_df.copy()

        if time_col not in df.columns or "Number of collision" not in df.columns:
            continue

        df[time_col] = pd.to_numeric(df[time_col], errors='coerce')
        df["Number of collision"] = pd.to_numeric(df["Number of collision"], errors='coerce')
        df = df.dropna(subset=[time_col, "Number of collision"]).sort_values(by=time_col)

        if df.empty:
            continue

        # 1. Stitch time gaps
        dt = df[time_col].diff().fillna(0)
        median_dt = dt[dt <= 2].median()
        if pd.isna(median_dt):
            median_dt = 0

        dt = dt.apply(lambda x: median_dt if x > 2 else x)
        df['t_active'] = dt.cumsum()

        # 2. Bin data
        df['Time_Bin'] = (df['t_active'] // bin_size) * bin_size
        binned_avg = df.groupby('Time_Bin')['Number of collision'].mean()

        if not binned_avg.empty:
            max_t_active = df['t_active'].max()
            max_bin = df['Time_Bin'].max()

            # Drop incomplete final bin
            if (max_t_active - max_bin) < bin_size:
                max_bin -= bin_size

            if max_bin >= 0:
                all_bins = np.arange(0, max_bin + bin_size, bin_size)
                binned_avg = binned_avg.reindex(all_bins).ffill().fillna(0)

                # Filter strictly to <= 2160s
                binned_avg = binned_avg[binned_avg.index <= 2160]

                if len(binned_avg) < 2:
                    continue

                # 3. Calculate Individual Metric (AUC)
                t_vals = binned_avg.index.values
                y_vals = binned_avg.values

                y_linear = np.linspace(y_vals[0], y_vals[-1], len(t_vals))

                auc_actual = np.trapz(y_vals, t_vals)
                auc_linear = np.trapz(y_linear, t_vals)

                dev_pct = ((auc_actual - auc_linear) / auc_linear) * 100 if auc_linear > 0 else 0.0

                if dev_pct > 5.0:
                    status = 'Learning'
                    color = '#2ECC71'  # Green
                elif dev_pct < -5.0:
                    status = 'Fatigue'
                    color = '#E74C3C'  # Red
                else:
                    status = 'Steady'
                    color = '#BDC3C7'  # Gray

                participant_metrics.append({
                    'Participant ID': pid,
                    'Adaptation Index (%)': dev_pct,
                    'Status': status,
                    'Color': color
                })

                # Store curve data for plotting
                for t_bin, avg_val in binned_avg.items():
                    participant_records.append({
                        'Participant ID': pid,
                        'Time (s)': t_bin,
                        'Collisions': avg_val,
                        'Color': color
                    })

    df_curves = pd.DataFrame(participant_records)
    df_metrics = pd.DataFrame(participant_metrics)

    if df_curves.empty:
        print("No valid log data found.")
        return None, None

    # --- Print Summary Statistics ---
    print("\n" + "=" * 55)
    print("INDIVIDUAL PARTICIPANT ADAPTATION SUMMARY")
    print("=" * 55)
    status_counts = df_metrics['Status'].value_counts()

    learning_count = status_counts.get('Learning', 0)
    steady_count = status_counts.get('Steady', 0)
    fatigue_count = status_counts.get('Fatigue', 0)
    total_valid = len(df_metrics)

    print(f"Total valid participants analyzed: {total_valid}")
    print(f"  • Learning / Adaptation (> 5% dev) : {learning_count} participants")
    print(f"  • Steady Rate (within ±5% dev)     : {steady_count} participants")
    print(f"  • Fatigue / Degradation (< -5% dev): {fatigue_count} participants")
    print("=" * 55 + "\n")

    # --- Plotting ---
    fig, ax = plt.subplots(figsize=(12, 7))

    # Plot individual lines
    for pid in df_curves['Participant ID'].unique():
        p_data = df_curves[df_curves['Participant ID'] == pid]
        # We only need the color from the first row of this participant
        p_color = p_data['Color'].iloc[0]

        ax.plot(p_data['Time (s)'], p_data['Collisions'], color=p_color, alpha=0.3, linewidth=1.5)

    # Plot overall average as a thick black line for reference
    mean_curve = df_curves.groupby('Time (s)')['Collisions'].mean()
    ax.plot(mean_curve.index, mean_curve.values, color='black', linewidth=3.5, label='Overall Group Mean')

    # Custom legend for the colors
    from matplotlib.lines import Line2D
    custom_lines = [
        Line2D([0], [0], color='#2ECC71', lw=2, alpha=0.8),
        Line2D([0], [0], color='#BDC3C7', lw=2, alpha=0.8),
        Line2D([0], [0], color='#E74C3C', lw=2, alpha=0.8),
        Line2D([0], [0], color='black', lw=3.5)
    ]
    ax.legend(custom_lines,
              [f'Learning (N={learning_count})', f'Steady (N={steady_count})', f'Fatigue (N={fatigue_count})',
               'Overall Mean'],
              loc='upper left', fontsize=11, framealpha=0.9)

    ax.set_title('Individual Cumulative Collisions by Adaptation Profile', fontsize=15, fontweight='bold', pad=15)
    ax.set_xlabel('Active Experiment Time (seconds)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Cumulative Collisions', fontsize=12, fontweight='bold')

    ax.grid(alpha=0.3, linestyle='--')
    ax.set_xlim(0, 2160)
    ax.set_ylim(bottom=0)

    plt.tight_layout()
    plt.savefig('individual_adaptation_curves.pdf', format='pdf', bbox_inches='tight')
    plt.show()


def analyze_sequence_vs_adaptation(experiment_logs_all, bin_size=5, time_col='Timestamp'):
    """
    Extracts the chronological difficulty sequence for each participant.
    Calculates their Adaptation Index (Learning, Steady, Fatigue).
    Cross-tabulates and prints the number of participants for each sequence within each group.
    """
    participant_metrics = []

    for pid, logs_df in experiment_logs_all.items():
        if logs_df is None or logs_df.empty:
            continue

        df = logs_df.copy()

        required_cols = [time_col, "Number of collision", "Difficulty level"]
        if not all(col in df.columns for col in required_cols):
            continue

        df[time_col] = pd.to_numeric(df[time_col], errors='coerce')
        df["Number of collision"] = pd.to_numeric(df["Number of collision"], errors='coerce')
        df = df.dropna(subset=[time_col, "Number of collision"]).sort_values(by=time_col)

        if df.empty:
            continue

        # 1. Extract chronological sequence of difficulty
        df['Difficulty level'] = df['Difficulty level'].astype(str).str.strip().str.lower()

        # Keep only the rows where the difficulty level changes
        sequence_list = df['Difficulty level'][df['Difficulty level'].shift() != df['Difficulty level']].tolist()
        # Filter to ensure we only capture valid phases
        valid_phases = [s.capitalize() for s in sequence_list if s in ['easy', 'medium', 'hard']]
        sequence_str = " -> ".join(valid_phases)

        # 2. Stitch time gaps and calculate Active Time
        dt = df[time_col].diff().fillna(0)
        median_dt = dt[dt <= 2].median()
        if pd.isna(median_dt):
            median_dt = 0

        dt = dt.apply(lambda x: median_dt if x > 2 else x)
        df['t_active'] = dt.cumsum()

        # 3. Bin data and calculate Adaptation Status
        df['Time_Bin'] = (df['t_active'] // bin_size) * bin_size
        binned_avg = df.groupby('Time_Bin')['Number of collision'].mean()

        if not binned_avg.empty:
            max_t_active = df['t_active'].max()
            max_bin = df['Time_Bin'].max()

            # Drop incomplete final bin
            if (max_t_active - max_bin) < bin_size:
                max_bin -= bin_size

            if max_bin >= 0:
                all_bins = np.arange(0, max_bin + bin_size, bin_size)
                binned_avg = binned_avg.reindex(all_bins).ffill().fillna(0)

                # Filter strictly to <= 2160s
                binned_avg = binned_avg[binned_avg.index <= 2160]

                if len(binned_avg) < 2:
                    continue

                t_vals = binned_avg.index.values
                y_vals = binned_avg.values

                y_linear = np.linspace(y_vals[0], y_vals[-1], len(t_vals))

                auc_actual = np.trapz(y_vals, t_vals)
                auc_linear = np.trapz(y_linear, t_vals)

                dev_pct = ((auc_actual - auc_linear) / auc_linear) * 100 if auc_linear > 0 else 0.0

                if dev_pct > 5.0:
                    status = 'Learning'
                elif dev_pct < -5.0:
                    status = 'Fatigue'
                else:
                    status = 'Steady'

                participant_metrics.append({
                    'Participant ID': pid,
                    'Sequence': sequence_str,
                    'Status': status
                })

    df_metrics = pd.DataFrame(participant_metrics)

    if df_metrics.empty:
        print("No valid data found to map sequences.")
        return None

    # --- Generate Summary Table ---
    # Create a cross-tabulation of Status vs. Sequence
    cross_tab = pd.crosstab(df_metrics['Status'], df_metrics['Sequence'])

    # Ensure all three statuses exist in the index even if they have 0 count
    for stat in ['Learning', 'Steady', 'Fatigue']:
        if stat not in cross_tab.index:
            cross_tab.loc[stat] = 0

    # Define the 6 expected sequences to ensure columns are ordered uniformly
    expected_sequences = [
        'Easy -> Medium -> Hard',
        'Easy -> Hard -> Medium',
        'Medium -> Easy -> Hard',
        'Medium -> Hard -> Easy',
        'Hard -> Easy -> Medium',
        'Hard -> Medium -> Easy'
    ]

    # Add any missing sequence columns with 0
    for seq in expected_sequences:
        if seq not in cross_tab.columns:
            cross_tab[seq] = 0

    # Reorder columns and rows for clean output
    cross_tab = cross_tab[expected_sequences].loc[['Learning', 'Steady', 'Fatigue']]

    print("\n" + "=" * 80)
    print("DISTRIBUTION OF DIFFICULTY SEQUENCES BY ADAPTATION GROUP")
    print("=" * 80)

    for status in ['Learning', 'Steady', 'Fatigue']:
        print(f"\n[{status.upper()}] Group (Total: {cross_tab.loc[status].sum()})")
        print("-" * 40)
        for seq in expected_sequences:
            count = cross_tab.loc[status, seq]
            print(f"  • {seq:<25} : {count}")

    print("\n" + "=" * 80 + "\n")


def plot_adaptation_index_by_difficulty(experiment_logs_all, bin_size=5, time_col='Timestamp', deviation_percent = 5):
    """
    Calculates the Adaptation Index (Deviation %) for each participant within
    each difficulty phase independently, then plots the distribution across all
    participants using box plots.
    Also reports the number of participants > 5% and < -5% on the plot.
    """
    records = []

    # Standardize difficulty colors
    diff_colors = {'easy': '#2ECC71', 'medium': '#F1C40F', 'hard': '#E74C3C'}
    difficulty_order = ['easy', 'medium', 'hard']

    for pid, logs_df in experiment_logs_all.items():
        if logs_df is None or logs_df.empty:
            continue

        df = logs_df.copy()

        if time_col not in df.columns or "Number of collision" not in df.columns or "Difficulty level" not in df.columns:
            continue

        df[time_col] = pd.to_numeric(df[time_col], errors='coerce')
        df["Number of collision"] = pd.to_numeric(df["Number of collision"], errors='coerce')
        df['Difficulty level'] = df['Difficulty level'].astype(str).str.strip().str.lower()

        df = df.dropna(subset=[time_col, "Number of collision"]).sort_values(by=time_col)

        if df.empty:
            continue

        # Process each difficulty phase separately
        for diff in difficulty_order:
            diff_df = df[df['Difficulty level'] == diff].copy()
            if diff_df.empty:
                continue

            # 1. Reset clock (Stitching gaps just in case there are pauses within the phase)
            diff_dt = diff_df[time_col].diff().fillna(0)
            diff_median_dt = diff_dt[diff_dt <= 2].median()
            if pd.isna(diff_median_dt):
                diff_median_dt = 0

            diff_dt = diff_dt.apply(lambda x: diff_median_dt if x > 2 else x)
            diff_df['phase_time'] = diff_dt.cumsum()

            # 2. Reset collisions so the phase always starts at 0
            base_collisions = diff_df['Number of collision'].iloc[0]
            diff_df['phase_collisions'] = diff_df['Number of collision'] - base_collisions

            # 3. Bin the data
            diff_df['Phase_Time_Bin'] = (diff_df['phase_time'] // bin_size) * bin_size
            diff_binned_avg = diff_df.groupby('Phase_Time_Bin')['phase_collisions'].mean()

            if not diff_binned_avg.empty:
                diff_max_bin = diff_df['Phase_Time_Bin'].max()
                diff_all_bins = np.arange(0, diff_max_bin + bin_size, bin_size)
                diff_binned_avg = diff_binned_avg.reindex(diff_all_bins).ffill().fillna(0)

                # We need at least 2 points to calculate AUC
                if len(diff_binned_avg) < 2:
                    continue

                # 4. Calculate AUC and Deviation Percentage
                t_vals = diff_binned_avg.index.values
                y_vals = diff_binned_avg.values

                # If they never collided in this phase, deviation is strictly 0%
                if y_vals[-1] == 0:
                    dev_pct = 0.0
                else:
                    y_linear = np.linspace(y_vals[0], y_vals[-1], len(t_vals))

                    auc_actual = np.trapz(y_vals, t_vals)
                    auc_linear = np.trapz(y_linear, t_vals)

                    dev_pct = ((auc_actual - auc_linear) / auc_linear) * 100 if auc_linear > 0 else 0.0

                records.append({
                    'Participant ID': pid,
                    'Difficulty': diff.capitalize(),
                    'Adaptation Index (%)': dev_pct
                })

    df_plot = pd.DataFrame(records)

    if df_plot.empty:
        print("No valid log data found.")
        return None

    # --- Plotting ---
    fig, ax = plt.subplots(figsize=(10, 6))

    # Capitalize the order for plotting matching
    plot_order = [d.capitalize() for d in difficulty_order]
    plot_colors = {k.capitalize(): v for k, v in diff_colors.items()}

    # Draw a reference line at 0% (Steady rate / perfectly linear)
    ax.axhline(0, color='#444444', linestyle='--', linewidth=1.5, zorder=1)

    # Box plot for distribution
    sns.boxplot(
        data=df_plot,
        x='Difficulty',
        y='Adaptation Index (%)',
        order=plot_order,
        palette=plot_colors,
        ax=ax,
        showfliers=False,
        width=0.5,
        zorder=2
    )

    # Overlay individual participant data points to see the exact spread
    sns.stripplot(
        data=df_plot,
        x='Difficulty',
        y='Adaptation Index (%)',
        order=plot_order,
        color='black',
        alpha=0.4,
        jitter=True,
        size=5,
        ax=ax,
        zorder=3
    )

    # --- Calculate Counts for Summary Box ---
    stats_text = "Participant Counts per Zone:\n"
    for diff in plot_order:
        diff_data = df_plot[df_plot['Difficulty'] == diff]

        n_learning = len(diff_data[diff_data['Adaptation Index (%)'] > deviation_percent])
        n_fatigue = len(diff_data[diff_data['Adaptation Index (%)'] < -deviation_percent])
        n_steady = len(
            diff_data[(diff_data['Adaptation Index (%)'] >= -5.0) & (diff_data['Adaptation Index (%)'] <= 5.0)])

        stats_text += f"• {diff}: {n_learning} Learn | {n_steady} Steady | {n_fatigue} Fatigue\n"

    # Add the stats text box to the top-left of the plot
    props = dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='gray')
    ax.text(0.02, 0.96, stats_text.strip(), transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=props, fontweight='bold', zorder=10)

    # Annotate plot regions for easy interpretation on the right side
    x_lims = ax.get_xlim()
    ax.text(x_lims[1], 5, 'Learning Zone (+%)', color='#2ECC71', fontweight='bold',
            ha='right', va='bottom', alpha=0.8, fontsize=10)
    ax.text(x_lims[1], -5, 'Fatigue Zone (-%)', color='#E74C3C', fontweight='bold',
            ha='right', va='top', alpha=0.8, fontsize=10)

    ax.set_title('Adaptation Index (Deviation from Linear) by Task Difficulty', fontsize=15, fontweight='bold', pad=15)
    ax.set_xlabel('Phase Difficulty', fontsize=12, fontweight='bold')
    ax.set_ylabel('Adaptation Index (Deviation %)', fontsize=12, fontweight='bold')

    ax.grid(alpha=0.2, linestyle='--')

    plt.tight_layout()
    plt.savefig('adaptation_index_by_difficulty_boxplot.pdf', format='pdf', bbox_inches='tight')
    plt.show()





def correlate_fatigue_and_adaptation(experiment_logs_all, df_questionnaire_mid, bin_size=5, time_col='Timestamp'):
    """
    Determines the chronological phase order for each participant to match
    the correct questionnaire column (Q1.1, Q1.2, Q1.3) to the correct difficulty.
    Calculates the Adaptation Index and correlates it with reported fatigue.
    """
    records = []

    # 1. Extract Adaptation Index and Map Phases
    for pid, logs_df in experiment_logs_all.items():
        if logs_df is None or logs_df.empty:
            continue

        df = logs_df.copy()

        req_cols = [time_col, "Number of collision", "Difficulty level"]
        if not all(col in df.columns for col in req_cols):
            continue

        df[time_col] = pd.to_numeric(df[time_col], errors='coerce')
        df["Number of collision"] = pd.to_numeric(df["Number of collision"], errors='coerce')
        df['Difficulty level'] = df['Difficulty level'].astype(str).str.strip().str.lower()

        df = df.dropna(subset=[time_col, "Number of collision"]).sort_values(by=time_col)
        if df.empty:
            continue

        # Find the start time of each difficulty to determine chronological phase order (1, 2, 3)
        phase_starts = df.groupby('Difficulty level')[time_col].min().sort_values()

        diff_to_phase = {}
        # Enumerate gives 0, 1, 2 -> we add 1 to get Phase 1, 2, 3
        for i, diff in enumerate(phase_starts.index):
            if diff in ['easy', 'medium', 'hard']:
                diff_to_phase[diff] = i + 1

        for diff in ['easy', 'medium', 'hard']:
            diff_df = df[df['Difficulty level'] == diff].copy()
            if diff_df.empty or diff not in diff_to_phase:
                continue

            phase_num = diff_to_phase[diff]

            # Reset clock for the phase
            diff_dt = diff_df[time_col].diff().fillna(0)
            diff_median_dt = diff_dt[diff_dt <= 2].median()
            if pd.isna(diff_median_dt): diff_median_dt = 0

            diff_dt = diff_dt.apply(lambda x: diff_median_dt if x > 2 else x)
            diff_df['phase_time'] = diff_dt.cumsum()

            # Reset collisions
            base_collisions = diff_df['Number of collision'].iloc[0]
            diff_df['phase_collisions'] = diff_df['Number of collision'] - base_collisions

            # Bin the data
            diff_df['Phase_Time_Bin'] = (diff_df['phase_time'] // bin_size) * bin_size
            diff_binned_avg = diff_df.groupby('Phase_Time_Bin')['phase_collisions'].mean()

            if not diff_binned_avg.empty:
                diff_max_bin = diff_df['Phase_Time_Bin'].max()
                diff_all_bins = np.arange(0, diff_max_bin + bin_size, bin_size)
                diff_binned_avg = diff_binned_avg.reindex(diff_all_bins).ffill().fillna(0)

                if len(diff_binned_avg) < 2:
                    continue

                # Calculate AUC Deviation %
                t_vals = diff_binned_avg.index.values
                y_vals = diff_binned_avg.values

                if y_vals[-1] == 0:
                    dev_pct = 0.0
                else:
                    y_linear = np.linspace(y_vals[0], y_vals[-1], len(t_vals))
                    auc_actual = np.trapz(y_vals, t_vals)
                    auc_linear = np.trapz(y_linear, t_vals)
                    dev_pct = ((auc_actual - auc_linear) / auc_linear) * 100 if auc_linear > 0 else 0.0

                # Q1.1 is Phase 1, Q1.2 is Phase 2, Q1.3 is Phase 3
                q_col = f"Q1.{phase_num}"

                records.append({
                    'Participant ID': int(pid),
                    'Difficulty': diff,
                    'Questionnaire_Column': q_col,
                    'Adaptation Index (%)': dev_pct
                })

    df_metrics = pd.DataFrame(records)

    if df_metrics.empty:
        print("No valid adaptation data found to correlate.")
        return None, None

    # 2. Match with Questionnaire Data
    # Ensure Participant ID columns match types perfectly for lookup
    df_questionnaire_mid['Participant ID'] = pd.to_numeric(df_questionnaire_mid['Participant ID'], errors='coerce')

    merged_records = []
    for _, row in df_metrics.iterrows():
        pid = row['Participant ID']
        q_col = row['Questionnaire_Column']
        diff = row['Difficulty']
        dev_pct = row['Adaptation Index (%)']

        # Look up this participant in the questionnaire dataframe
        q_row = df_questionnaire_mid[df_questionnaire_mid['Participant ID'] == pid]

        if not q_row.empty and q_col in q_row.columns:
            fatigue_score = q_row[q_col].values[0]
            if pd.notna(fatigue_score):
                merged_records.append({
                    'Participant ID': pid,
                    'Difficulty': diff,
                    'Reported Fatigue': float(fatigue_score),
                    'Adaptation Index (%)': dev_pct
                })

    df_merged = pd.DataFrame(merged_records)

    # 3. Calculate and Print Correlations
    print("\n" + "=" * 65)
    print("SPEARMAN CORRELATION: REPORTED FATIGUE vs ADAPTATION INDEX")
    print("=" * 65)

    results = {}
    for diff in ['easy', 'medium', 'hard']:
        diff_data = df_merged[df_merged['Difficulty'] == diff]

        if len(diff_data) > 2:
            # Spearman is used because Questionnaire data (1-5) is Ordinal
            correlation, p_value = spearmanr(diff_data['Reported Fatigue'], diff_data['Adaptation Index (%)'])
            results[diff] = {'correlation': correlation, 'p_value': p_value, 'n': len(diff_data)}

            print(f"[{diff.upper()} DIFFICULTY]")
            print(f"  • Spearman Correlation (rho): {correlation:+.3f}")
            print(f"  • P-value:                    {p_value:.4f}")
            print(f"  • Valid Participants (N):     {len(diff_data)}")
            print("-" * 65)
        else:
            print(f"[{diff.upper()} DIFFICULTY] Not enough matching data to compute correlation.")
            print("-" * 65)


def plot_performance_and_polar_accuracy(perception_results_all, experiment_logs_all, color_palette, axes=None):
    """
    Plots Miss Rate, Angular Accuracy, Distance Accuracy, and Polar Accuracy
    by modality in a 2x2 subplot arrangement.
    """

    mod_metrics = []
    all_trials = []

    for subject, df in perception_results_all.items():
        if df is None or df.empty:
            continue

        df_copy = df.copy()
        df_copy["Participant ID"] = subject

        perc_angle_col = "Angle perceived" if "Angle perceived" in df_copy.columns else "Perceived angle"
        perc_dist_col = "Distance perceived" if "Distance perceived" in df_copy.columns else "Perceived distance"
        dist_col = "Distance" if "Distance" in df_copy.columns else "Distnce"

        df_copy[perc_angle_col] = pd.to_numeric(df_copy[perc_angle_col], errors="coerce")
        df_copy[perc_dist_col] = pd.to_numeric(df_copy[perc_dist_col], errors="coerce")
        df_copy["Angle"] = pd.to_numeric(df_copy["Angle"], errors="coerce")
        df_copy[dist_col] = pd.to_numeric(df_copy[dist_col], errors="coerce")
        df_copy["Modality"] = df_copy["Modality"].astype(str).str.strip().str.capitalize()

        invalidated_mask = df_copy[perc_angle_col].eq(-1) | df_copy[perc_dist_col].eq(-1)
        df_copy = df_copy.loc[~invalidated_mask].copy()
        all_trials.append(df_copy)

        for modality in ["Visual", "Auditory", "Haptic"]:
            mod_df = df_copy.loc[df_copy["Modality"] == modality].copy()

            if mod_df.empty:
                continue

            missed_mask = mod_df[perc_angle_col].eq(0) | mod_df[perc_dist_col].eq(0)
            valid_mask = mod_df[perc_angle_col].gt(0) & mod_df[perc_dist_col].gt(0)
            analyzable_mask = missed_mask | valid_mask

            miss_rate = missed_mask.sum() / analyzable_mask.sum() if analyzable_mask.sum() > 0 else np.nan
            valid_trials = mod_df.loc[valid_mask]

            if not valid_trials.empty:
                ang_acc = valid_trials["Angle"].eq(valid_trials[perc_angle_col]).mean()
                dist_acc = valid_trials[dist_col].eq(valid_trials[perc_dist_col]).mean()
            else:
                ang_acc, dist_acc = np.nan, np.nan

            mod_metrics.append({
                "Subject": subject,
                "Modality": modality,
                "Miss Rate": miss_rate,
                "Angular Accuracy": ang_acc,
                "Distance Accuracy": dist_acc
            })

    if not mod_metrics or not all_trials:
        raise ValueError("No valid perception data was found.")

    df_mod = pd.DataFrame(mod_metrics)
    df_all = pd.concat(all_trials, ignore_index=True)

    perc_angle_col = "Angle perceived" if "Angle perceived" in df_all.columns else "Perceived angle"
    perc_dist_col = "Distance perceived" if "Distance perceived" in df_all.columns else "Perceived distance"
    dist_col = "Distance" if "Distance" in df_all.columns else "Distnce"

    valid_polar_df = df_all.loc[
        df_all[perc_angle_col].gt(0)
        & df_all[perc_dist_col].gt(0)
        & df_all["Angle"].notna()
        & df_all[dist_col].notna()
    ].copy()

    if valid_polar_df.empty:
        raise ValueError("No valid trials were available for polar accuracy.")

    theta_true = valid_polar_df["Angle"] * (np.pi / 4)
    theta_perceived = valid_polar_df[perc_angle_col] * (np.pi / 4)
    r_true = valid_polar_df[dist_col]
    r_perceived = valid_polar_df[perc_dist_col]

    squared_error = (
        r_true ** 2
        + r_perceived ** 2
        - 2 * r_true * r_perceived * np.cos(theta_true - theta_perceived)
    )

    valid_polar_df["Geometric Error"] = np.sqrt(np.maximum(squared_error, 0))

    r_max = max(r_true.max(), r_perceived.max())

    if pd.isna(r_max) or r_max <= 0:
        raise ValueError("The maximum distance must be greater than zero.")

    valid_polar_df["Polar Accuracy"] = (1 - valid_polar_df["Geometric Error"] / (2 * r_max))
    valid_polar_df["Polar Accuracy"] = valid_polar_df["Polar Accuracy"].clip(lower=0, upper=100)

    polar_subject_means = (
        valid_polar_df.groupby(["Participant ID", "Modality"], as_index=False)["Polar Accuracy"].mean()
    )

    modality_order = ["Visual", "Auditory", "Haptic"]
    modality_pairs = [("Visual", "Auditory"), ("Auditory", "Haptic"), ("Visual", "Haptic")]
    palette_mod = {modality: color_palette[modality.lower()] for modality in modality_order}

    def calculate_wilcoxon(data, subject_col, condition_col, metric, pairs, bonferroni=False):
        pivot_df = data.pivot(index=subject_col, columns=condition_col, values=metric)
        results = {}

        for condition1, condition2 in pairs:
            if condition1 not in pivot_df.columns or condition2 not in pivot_df.columns:
                results[(condition1, condition2)] = np.nan
                continue

            paired_data = pivot_df[[condition1, condition2]].dropna()

            if len(paired_data) <= 1:
                results[(condition1, condition2)] = np.nan
                continue

            differences = paired_data[condition1] - paired_data[condition2]

            if differences.eq(0).all():
                p_value = 1.0
            else:
                _, p_value = wilcoxon(
                    paired_data[condition1],
                    paired_data[condition2],
                    alternative="two-sided"
                )

            results[(condition1, condition2)] = min(p_value * len(pairs), 1.0) if bonferroni else p_value

        return results

    def annotate_wilcoxon(ax, data, subject_col, condition_col, metric, pairs, order, bonferroni=False):
        p_values = calculate_wilcoxon(
            data=data,
            subject_col=subject_col,
            condition_col=condition_col,
            metric=metric,
            pairs=pairs,
            bonferroni=bonferroni
        )

        values = data[metric].dropna()

        if values.empty:
            return

        y_min = values.min()
        y_max = values.max()
        y_range = y_max - y_min

        if pd.isna(y_range) or y_range == 0:
            y_range = 0.1 if y_max <= 1 else 10

        lower_limit = min(ax.get_ylim()[0], y_min - y_range * 0.05)
        upper_limit = y_max + y_range * 0.42
        ax.set_ylim(lower_limit, upper_limit)

        for index, (condition1, condition2) in enumerate(pairs):
            p_value = p_values[(condition1, condition2)]
            p_text = "N/A" if pd.isna(p_value) else ("p<0.001" if p_value < 0.001 else f"p={p_value:.3f}")

            x1 = order.index(condition1)
            x2 = order.index(condition2)
            y = y_max + y_range * (0.05 + index * 0.11)
            h = y_range * 0.025

            ax.plot([x1, x1, x2, x2], [y, y + h, y + h, y], lw=1.2, color="black")
            ax.text(
                (x1 + x2) / 2,
                y + h,
                p_text,
                ha="center",
                va="bottom",
                fontsize=12,
                fontweight="bold" if pd.notna(p_value) and p_value < 0.05 else "normal"
            )

    sns.set_theme(style="whitegrid", context="paper", font_scale=1.15)
    standalone = axes is None

    if standalone:
        fig, axes = plt.subplots(1, 4, figsize=(16, 4))

    axes = np.asarray(axes).flatten()

    if len(axes) != 4:
        raise ValueError("Exactly four axes are required for the 2x2 plot.")
    for ax in axes:
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color("black")
        ax.spines["bottom"].set_color("black")
    performance_metrics = ["Miss Rate", "Angular Accuracy", "Distance Accuracy"]

    for index, metric in enumerate(performance_metrics):
        sns.boxplot(data=df_mod, x="Modality", y=metric, order=modality_order, palette=palette_mod,
            ax=axes[index], showmeans=True, meanprops={"marker": "o","markerfacecolor": "white","markeredgecolor": "black"})

        sns.stripplot(data=df_mod, x="Modality", y=metric, order=modality_order, palette=palette_mod, ax=axes[index],
            alpha=0.6, jitter=True, edgecolor="gray", linewidth=0.5)

        # axes[index].set_title(f"{metric} by Modality", fontweight="bold", fontsize=13)
        axes[index].set_xlabel("")
        axes[index].set_ylabel(metric, fontsize=15)

        annotate_wilcoxon(ax=axes[index], data=df_mod, subject_col="Subject", condition_col="Modality", metric=metric,
            pairs=modality_pairs, order=modality_order)

    sns.boxplot(data=polar_subject_means, x="Modality", y="Polar Accuracy", order=modality_order, palette=palette_mod,
        ax=axes[3], showfliers=False, width=0.5, showmeans=True, meanprops={"marker": "o", "markerfacecolor": "white","markeredgecolor": "black"})

    sns.stripplot(data=polar_subject_means, x="Modality", y="Polar Accuracy", order=modality_order,
        palette=palette_mod, ax=axes[3], alpha=0.6, jitter=True, edgecolor="gray", linewidth=0.5)

    # axes[3].set_title("Polar Accuracy by Modality", fontweight="bold", fontsize=13)
    axes[3].set_xlabel("")
    axes[3].set_ylabel("Mean Polar Accuracy", fontweight="bold")

    for i in [0, 1, 2, 3]:
        axes[i].tick_params(axis='y', labelsize=12)
        axes[i].set_xticks([])

    axes[0].set_yticks([0, 0.2, 0.4, 0.5])
    axes[1].set_yticks([0.4, 0.6, 0.8, 1])
    axes[2].set_yticks([0.4, 0.6, 0.8, 1])
    axes[3].set_yticks([0.7, 0.8, 0.9, 1])



    annotate_wilcoxon(ax=axes[3], data=polar_subject_means, subject_col="Participant ID", condition_col="Modality",
        metric="Polar Accuracy", pairs=modality_pairs, order=modality_order, bonferroni=True)

    legend_handles = [
        Patch(facecolor=palette_mod["Visual"], label="Visual"),
        Patch(facecolor=palette_mod["Auditory"], label="Auditory"),
        Patch(facecolor=palette_mod["Haptic"], label="Haptic")]

    fig = axes[0].figure
    fig.legend(handles=legend_handles, loc="upper center", ncol=3, frameon=False, fontsize=15, bbox_to_anchor=(0.5, 1.005))


    fig.savefig('across_modality.pdf', format='pdf', bbox_inches='tight')

    if standalone:
        # fig.suptitle("Perception Performance by Feedback Modality", fontsize=16, fontweight="bold", y=1.01)
        plt.tight_layout(rect=[0, 0, 1, 0.92])
        plt.show()


def print_extreme_participants(perception_results_all, experiment_logs_all, demographics_path):
    """
    Identifies and prints extreme participants based on specific gender and performance criteria,
    along with their experienced difficulty phase sequence. Accounts for missing/omitted participants.
    Also identifies candidates that appear most frequently across all extreme categories.
    """
    metrics_list = []

    # 1. Calculate metrics and extract sequence for each participant
    for subject, df in perception_results_all.items():
        if df is None or df.empty:
            continue

        df_copy = df.copy()
        perc_angle_col = 'Angle perceived' if 'Angle perceived' in df_copy.columns else 'Perceived angle'
        perc_dist_col = 'Distance perceived' if 'Distance perceived' in df_copy.columns else 'Perceived distance'
        dist_col = 'Distance' if 'Distance' in df_copy.columns else 'Distnce'

        # Standardize strings
        df_copy['Modality'] = df_copy['Modality'].astype(str).str.strip().str.lower()
        if 'Difficulty level' in df_copy.columns:
            df_copy['Difficulty level'] = df_copy['Difficulty level'].astype(str).str.strip().str.lower()

        # Extract Phase Sequence (ordered by appearance)
        if 'Difficulty level' in df_copy.columns:
            seq = df_copy['Difficulty level'].dropna().unique().tolist()
            seq_str = " -> ".join([s.capitalize() for s in seq])
        else:
            seq_str = "Unknown"

        # Drop hardware faults (-1) for accuracy calculations
        df_clean = df_copy[df_copy[perc_angle_col] >= 0].copy()

        # Helper to calculate accuracy (penalizing misses)
        def calc_acc(sub_df):
            if sub_df.empty:
                return np.nan, np.nan, np.nan
            valid = sub_df[(sub_df[perc_angle_col] > 0) & (sub_df[perc_dist_col] > 0)]
            if valid.empty:
                return 0.0, 0.0, 0.0

            ang_hits = (valid['Angle'] == valid[perc_angle_col]).sum()
            dist_hits = (valid[dist_col] == valid[perc_dist_col]).sum()
            tot_hits = ((valid['Angle'] == valid[perc_angle_col]) & (valid[dist_col] == valid[perc_dist_col])).sum()

            total_trials = len(sub_df)
            return ang_hits / total_trials, dist_hits / total_trials, tot_hits / total_trials

        # Helper to calculate polar accuracy (geometric error)
        def calc_polar_acc(sub_df):
            valid = sub_df[(sub_df[perc_angle_col] >= 1) & (sub_df[perc_dist_col] >= 1)].copy()
            if valid.empty:
                return np.nan

            theta_true = pd.to_numeric(valid['Angle'], errors='coerce') * (np.pi / 4)
            theta_perc = pd.to_numeric(valid[perc_angle_col], errors='coerce') * (np.pi / 4)
            r_true = pd.to_numeric(valid[dist_col], errors='coerce')
            r_perc = pd.to_numeric(valid[perc_dist_col], errors='coerce')

            squared_error = r_true ** 2 + r_perc ** 2 - 2 * r_true * r_perc * np.cos(theta_true - theta_perc)
            geom_error = np.sqrt(np.maximum(squared_error, 0))

            r_max = max(r_true.max(), r_perc.max())
            if pd.isna(r_max) or r_max <= 0:
                return np.nan

            polar_acc_vals = 1 - (geom_error / (2 * r_max))
            return polar_acc_vals.clip(lower=0, upper=1).mean()

        # Auditory Angular Accuracy
        aud_df = df_clean[df_clean['Modality'] == 'auditory']
        aud_ang_acc, _, _ = calc_acc(aud_df)

        # Easy Accuracies
        easy_df = df_clean[df_clean['Difficulty level'] == 'easy']
        _, _, easy_tot_acc = calc_acc(easy_df)
        easy_polar_acc = calc_polar_acc(easy_df)

        # Medium Accuracies
        med_df = df_clean[df_clean['Difficulty level'] == 'medium']
        med_ang_acc, med_dist_acc, _ = calc_acc(med_df)

        # Hard Accuracies
        hard_df = df_clean[df_clean['Difficulty level'] == 'hard']
        _, _, hard_tot_acc = calc_acc(hard_df)
        hard_polar_acc = calc_polar_acc(hard_df)

        # Overall Total Accuracy
        _, _, overall_tot_acc = calc_acc(df_clean)

        # Total Collisions
        logs_df = experiment_logs_all.get(subject)
        tot_col = np.nan
        if logs_df is not None and not logs_df.empty and 'Number of collision' in logs_df.columns:
            valid_logs = logs_df.dropna(subset=['Number of collision']).copy()
            if not valid_logs.empty:
                valid_logs['Number of collision'] = pd.to_numeric(valid_logs['Number of collision'], errors='coerce')
                tot_col = valid_logs['Number of collision'].max() - valid_logs['Number of collision'].min()

        metrics_list.append({
            'Subject': subject,
            'Sequence': seq_str,
            'Total Collisions': tot_col,
            'Auditory Ang Acc': aud_ang_acc,
            'Easy Tot Acc': easy_tot_acc,
            'Easy Polar Acc': easy_polar_acc,
            'Medium Ang Acc': med_ang_acc,
            'Medium Dist Acc': med_dist_acc,
            'Hard Tot Acc': hard_tot_acc,
            'Hard Polar Acc': hard_polar_acc,
            'Total Accuracy': overall_tot_acc
        })

    metrics_df = pd.DataFrame(metrics_list)

    # 2. Map Demographics (Gender) safely
    demo_df = pd.read_csv(demographics_path)

    if 'Participant ID' in demo_df.columns:
        demo_df['Subject'] = demo_df['Participant ID'].astype(str)
        # Pad to ensure consistency (e.g., '1' -> '01') if your folder structure uses padding
        demo_df['Subject'] = demo_df['Subject'].apply(lambda x: x.zfill(2) if len(x) == 1 else x)
    elif 'Folder_Name' in demo_df.columns:
        demo_df['Subject'] = demo_df['Folder_Name'].astype(str)
    else:
        all_possible_subjects = [f"{i:02d}" for i in range(1, len(demo_df) + 1)]
        demo_df['Subject'] = all_possible_subjects

    demo_df['Gender'] = demo_df['Gender'].astype(str).str.strip().str.capitalize()

    final_df = pd.merge(metrics_df, demo_df[['Subject', 'Gender']], on='Subject', how='inner')

    # 3. Helpers for sorting, printing, and tracking
    def print_top(df, gender, metric, ascending, title, n=2, is_percentage=True):
        filtered = df[df['Gender'] == gender].dropna(subset=[metric]).sort_values(by=metric, ascending=ascending)
        top_n = filtered.head(n)
        print(f"\n--- {title} ---")
        subjects_found = []
        for _, row in top_n.iterrows():
            val = row[metric] * 100 if is_percentage else row[metric]
            unit = "%" if is_percentage else ""
            print(f"Participant: {row['Subject']:<10} | {metric}: {val:<6.2f}{unit} | Sequence: {row['Sequence']}")
            subjects_found.append(row['Subject'])
        return subjects_found

    def print_top_overall(df, metric, ascending, title, n=2, is_percentage=True):
        filtered = df.dropna(subset=[metric]).sort_values(by=metric, ascending=ascending)
        top_n = filtered.head(n)
        print(f"\n--- {title} ---")
        subjects_found = []
        for _, row in top_n.iterrows():
            val = row[metric] * 100 if is_percentage else row[metric]
            unit = "%" if is_percentage else ""
            print(
                f"Participant: {row['Subject']:<10} | Gender: {row['Gender']:<6} | {metric}: {val:<6.2f}{unit} | Sequence: {row['Sequence']}")
            subjects_found.append(row['Subject'])
        return subjects_found

    # 4. Print outputs and collect candidates
    print("=" * 80)
    print("EXTREME PARTICIPANTS CANDIDATE LIST")
    print("=" * 80)

    all_extreme_candidates = []

    # Original requested extremes
    all_extreme_candidates.extend(
        print_top(final_df, 'Male', 'Total Collisions', ascending=False, title="2 Males with MOST Total Collisions",
                  is_percentage=False))
    all_extreme_candidates.extend(
        print_top(final_df, 'Female', 'Total Collisions', ascending=True, title="2 Females with LEAST Total Collisions",
                  is_percentage=False))

    all_extreme_candidates.extend(print_top(final_df, 'Male', 'Auditory Ang Acc', ascending=True,
                                            title="2 Males with LEAST Auditory Angular Accuracy"))
    all_extreme_candidates.extend(print_top(final_df, 'Female', 'Auditory Ang Acc', ascending=False,
                                            title="2 Females with MOST Auditory Angular Accuracy"))

    all_extreme_candidates.extend(print_top(final_df, 'Male', 'Medium Ang Acc', ascending=True,
                                            title="2 Males with LEAST Medium Angular Accuracy"))
    all_extreme_candidates.extend(print_top(final_df, 'Female', 'Medium Ang Acc', ascending=False,
                                            title="2 Females with MOST Medium Angular Accuracy"))

    all_extreme_candidates.extend(print_top(final_df, 'Male', 'Medium Dist Acc', ascending=True,
                                            title="2 Males with LEAST Medium Distance Accuracy"))
    all_extreme_candidates.extend(print_top(final_df, 'Female', 'Medium Dist Acc', ascending=False,
                                            title="2 Females with MOST Medium Distance Accuracy"))

    all_extreme_candidates.extend(print_top(final_df, 'Male', 'Total Accuracy', ascending=True,
                                            title="2 Males with LEAST Overall Total Accuracy"))
    all_extreme_candidates.extend(print_top(final_df, 'Female', 'Total Accuracy', ascending=False,
                                            title="2 Females with MOST Overall Total Accuracy"))

    # Overall Total Accuracy Extremes
    all_extreme_candidates.extend(print_top_overall(final_df, 'Hard Tot Acc', ascending=False,
                                                    title="2 Participants with MOST Total Accuracy in Hard"))
    all_extreme_candidates.extend(print_top_overall(final_df, 'Easy Tot Acc', ascending=True,
                                                    title="2 Participants with LEAST Total Accuracy in Easy"))

    # Newly requested Polar Accuracy extremes
    least_easy_polar = print_top_overall(final_df, 'Easy Polar Acc', ascending=True, n=19,
                                         title="15 Participants with LEAST Polar Accuracy in Easy")

    most_hard_polar = print_top_overall(final_df, 'Hard Polar Acc', ascending=False, n=19,
                                        title="15 Participants with MOST Polar Accuracy in Hard")

    # 2. Extend the main tracking list so the final frequency tally still works
    all_extreme_candidates.extend(least_easy_polar)
    all_extreme_candidates.extend(most_hard_polar)

    # 3. Find the intersection (common participants) between these two specific lists
    common_polar_participants = set(least_easy_polar).intersection(set(most_hard_polar))

    # 4. Print the common participants
    print("\n" + "-" * 80)
    print("COMMON PARTICIPANTS: LEAST Easy Polar Acc AND MOST Hard Polar Acc")
    print("-" * 80)

    if common_polar_participants:
        for sub in common_polar_participants:
            sub_info = final_df[final_df['Subject'] == sub].iloc[0]
            print(f"Participant {sub:<5} | Gender: {sub_info['Gender']:<6} | Sequence: {sub_info['Sequence']}")
    else:
        print("No common participants found between these two specific lists.")

    # 5. Tally the most frequent candidates
    print("\n" + "=" * 80)
    print("MOST FREQUENT CANDIDATES (Appeared in Multiple Extreme Categories)")
    print("=" * 80)

    candidate_counts = Counter(all_extreme_candidates)

    # Filter to only show those who appeared more than once, sorted by frequency
    frequent_candidates = [(sub, count) for sub, count in candidate_counts.most_common() if count > 1]

    if frequent_candidates:
        for sub, count in frequent_candidates:
            # Grab their gender and sequence for context
            sub_info = final_df[final_df['Subject'] == sub].iloc[0]
            print(
                f"Participant {sub:<5} | Count: {count} | Gender: {sub_info['Gender']:<6} | Sequence: {sub_info['Sequence']}")
    else:
        print("No participants appeared in more than one extreme category.")

    print("=" * 80)




def plot_accuracy_by_modality_and_difficulty(perception_results_all, color_palette, axes=None):
    """
    Creates a 1x3 subplot grid (Visual, Auditory, Haptic).
    For each modality, plots Total Accuracy across Easy, Medium, and Hard phases.
    Annotates paired Wilcoxon signed-rank p-values between difficulties.
    Safely handles omitted participants.
    """
    # Fix potential missing hash in color palette
    for key in color_palette:
        if isinstance(color_palette[key], str) and not color_palette[key].startswith('#'):
            color_palette[key] = '#' + color_palette[key]

    metrics_list = []

    # 1. Extract Metrics
    for subject, df in perception_results_all.items():
        if df is None or df.empty:
            continue

        df_copy = df.copy()
        perc_angle_col = 'Angle perceived' if 'Angle perceived' in df_copy.columns else 'Perceived angle'
        perc_dist_col = 'Distance perceived' if 'Distance perceived' in df_copy.columns else 'Perceived distance'
        dist_col = 'Distance' if 'Distance' in df_copy.columns else 'Distnce'

        # Filter out hardware faults (-1) entirely from the calculations
        df_clean = df_copy[df_copy[perc_angle_col] >= 0].copy()

        if 'Modality' in df_clean.columns:
            df_clean['Modality'] = df_clean['Modality'].astype(str).str.strip().str.capitalize()
        if 'Difficulty level' in df_clean.columns:
            df_clean['Difficulty level'] = df_clean['Difficulty level'].astype(str).str.strip().str.capitalize()

        for mod in ['Visual', 'Auditory', 'Haptic']:
            for diff in ['Easy', 'Medium', 'Hard']:
                cond_df = df_clean[(df_clean['Modality'] == mod) & (df_clean['Difficulty level'] == diff)]

                if cond_df.empty:
                    continue

                # Calculate Accuracy (penalizing misses by dividing by the length of the clean condition DataFrame)
                valid_responses = cond_df[(cond_df[perc_angle_col] > 0) & (cond_df[perc_dist_col] > 0)]

                if not valid_responses.empty:
                    correct_trials = ((valid_responses['Angle'] == valid_responses[perc_angle_col]) &
                                      (valid_responses[dist_col] == valid_responses[perc_dist_col])).sum()
                    accuracy = correct_trials / len(cond_df)
                else:
                    accuracy = 0.0

                metrics_list.append({
                    'Subject': subject,
                    'Modality': mod,
                    'Difficulty': diff,
                    'Accuracy': accuracy
                })

    df_metrics = pd.DataFrame(metrics_list)
    if df_metrics.empty:
        raise ValueError("No valid accuracy data found.")

    # --- Helper Function for Statistical Annotation (Paired Wilcoxon) ---
    def annotate_wilcoxon_paired_3way(ax, data, metric, condition_col, pairs, order):
        pivot_df = data.pivot(index='Subject', columns=condition_col, values=metric)

        y_max = data[metric].max()
        y_min = data[metric].min()
        y_range = y_max - y_min
        if pd.isna(y_range) or y_range == 0: y_range = 0.1

        # Expand Y-axis to make room for 3 stacked brackets
        ax.set_ylim(min(0, y_min - y_range * 0.05), y_max + y_range * 0.45)

        for i, (c1, c2) in enumerate(pairs):
            p_text = "N/A"
            if c1 in pivot_df.columns and c2 in pivot_df.columns:
                paired_data = pivot_df[[c1, c2]].dropna()
                if len(paired_data) > 1:
                    diffs = paired_data[c1] - paired_data[c2]
                    if not (diffs == 0).all():
                        stat, p = wilcoxon(paired_data[c1], paired_data[c2], alternative='two-sided')
                        if p < 0.001:
                            p_text = "*\np<0.001"
                        else:
                            p_text = f"p={p:.3f}"

            x1 = order.index(c1)
            x2 = order.index(c2)

            # Layout logic: Stack E-M and M-H lower, float E-H higher
            if c1 == 'Easy' and c2 == 'Hard':
                bracket_y = y_max + y_range * 0.28
            else:
                bracket_y = y_max + y_range * 0.08 + (i * y_range * 0.05)

            bracket_h = y_range * 0.02

            ax.plot([x1, x1, x2, x2], [bracket_y, bracket_y + bracket_h, bracket_y + bracket_h, bracket_y], lw=1.2,
                    color='k')

            if p_text != "N/A":
                clean_p_val = float(p_text.split('=')[-1]) if "=" in p_text else 0.0001
                weight = 'bold' if clean_p_val < 0.05 else 'normal'
            else:
                weight = 'normal'

            ax.text((x1 + x2) / 2, bracket_y + bracket_h, p_text, ha='center', va='bottom', color='k', fontsize=10,
                    fontweight=weight)

    # --- Plotting ---
    sns.set_theme(style="whitegrid", context="paper", font_scale=1.2)
    standalone = axes is None
    if standalone:
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    axes = np.array(axes).flatten()

    modalities = ['Visual', 'Auditory', 'Haptic']
    diff_order = ['Easy', 'Medium', 'Hard']
    diff_pairs = [('Easy', 'Medium'), ('Medium', 'Hard'), ('Easy', 'Hard')]

    palette_diff = {diff: color_palette[diff.lower()] for diff in diff_order}

    for i, mod in enumerate(modalities):
        mod_data = df_metrics[df_metrics['Modality'] == mod]

        if not mod_data.empty:
            sns.boxplot(data=mod_data, x='Difficulty', y='Accuracy', order=diff_order, palette=palette_diff, ax=axes[i],
                        showmeans=True,
                        meanprops={"marker": "o", "markerfacecolor": "white", "markeredgecolor": "black"})
            sns.stripplot(data=mod_data, x='Difficulty', y='Accuracy', order=diff_order, palette=palette_diff,
                          ax=axes[i],
                          alpha=0.6, jitter=True, edgecolor='gray', linewidth=0.5)

            axes[i].set_title(f'{mod} Accuracy\n(Across Difficulties)', fontweight='bold', fontsize=14)
            axes[i].set_xlabel('')

            if i == 0:
                axes[i].set_ylabel('Total Accuracy', fontweight='bold', fontsize=12)
            else:
                axes[i].set_ylabel('')

            annotate_wilcoxon_paired_3way(axes[i], mod_data, 'Accuracy', 'Difficulty', diff_pairs, diff_order)

    if standalone:
        plt.tight_layout()
        plt.show()


# ===============================
# Thesis-only result visualizations
# ===============================

def _resolve_perception_columns(df):
    """Resolve renamed perception columns safely."""
    perc_angle_col = 'Perceived angle' if 'Perceived angle' in df.columns else 'Angle perceived'
    perc_dist_col = 'Perceived distance' if 'Perceived distance' in df.columns else 'Distance perceived'
    dist_col = 'Distance' if 'Distance' in df.columns else 'Distnce'
    trial_col = 'Trial number' if 'Trial number' in df.columns else ('Trial' if 'Trial' in df.columns else None)
    return perc_angle_col, perc_dist_col, dist_col, trial_col


def _build_trial_level_dataframe(perception_results_all):
    """Create unified trial-level dataframe with validity, correctness and timing fields."""
    all_trials = []

    for subject_id, df in perception_results_all.items():
        if df is None or df.empty:
            continue

        dfc = df.copy()
        perc_angle_col, perc_dist_col, dist_col, trial_col = _resolve_perception_columns(dfc)

        if 'Modality' not in dfc.columns:
            continue

        dfc['Participant ID'] = subject_id
        dfc['Modality'] = dfc['Modality'].astype(str).str.strip().str.lower()

        if 'Difficulty level' in dfc.columns:
            dfc['Difficulty level'] = dfc['Difficulty level'].astype(str).str.strip().str.lower()

        for col in ['Angle', dist_col, perc_angle_col, perc_dist_col, 'Response start', 'Response end', 'Phase timestamp']:
            if col in dfc.columns:
                dfc[col] = pd.to_numeric(dfc[col], errors='coerce')

        dfc['Is_Invalid'] = dfc[perc_angle_col].eq(-1) | dfc[perc_dist_col].eq(-1)
        dfc['Is_Miss'] = (~dfc['Is_Invalid']) & (dfc[perc_angle_col].eq(0) | dfc[perc_dist_col].eq(0))
        dfc['Is_Valid_Response'] = (~dfc['Is_Invalid']) & dfc[perc_angle_col].gt(0) & dfc[perc_dist_col].gt(0)

        dfc['Is_Correct'] = np.where(
            dfc['Is_Valid_Response'],
            (dfc['Angle'].eq(dfc[perc_angle_col]) & dfc[dist_col].eq(dfc[perc_dist_col])).astype(float),
            np.nan
        )

        angle_diff = np.abs(dfc['Angle'] - dfc[perc_angle_col])
        dfc['Angular_Error'] = np.where(dfc['Is_Valid_Response'], np.minimum(angle_diff, 8 - angle_diff), np.nan)
        dfc['Distance_Error'] = np.where(dfc['Is_Valid_Response'], np.abs(dfc[dist_col] - dfc[perc_dist_col]), np.nan)

        dfc['Reaction_Time'] = dfc['Response start'] - dfc['Phase timestamp']
        dfc['Response_Duration'] = dfc['Response end'] - dfc['Response start']

        if trial_col is not None:
            dfc['Trial_Index'] = pd.to_numeric(dfc[trial_col], errors='coerce')
        else:
            dfc['Trial_Index'] = np.arange(1, len(dfc) + 1)

        all_trials.append(dfc)

    if not all_trials:
        return pd.DataFrame()

    return pd.concat(all_trials, ignore_index=True)


def plot_modality_difficulty_performance_matrices(perception_results_all, color_palette):
    """
    Plot two side-by-side heatmaps:
      1) Total accuracy (%) by modality x difficulty
      2) Miss rate (%) by modality x difficulty

    This gives a compact, publication-ready summary of where performance
    breaks down across experimental conditions.
    """
    df = _build_trial_level_dataframe(perception_results_all)
    if df.empty:
        print('No valid perception data was found for performance matrices.')
        return None

    modality_order = ['visual', 'auditory', 'haptic']
    difficulty_order = ['easy', 'medium', 'hard']

    summary = (
        df.groupby(['Participant ID', 'Modality', 'Difficulty level'], as_index=False)
        .agg(
            accuracy=('Is_Correct', lambda x: np.nanmean(x) * 100),
            miss_rate=('Is_Miss', lambda x: np.nanmean(x) * 100)
        )
    )

    agg = (
        summary.groupby(['Modality', 'Difficulty level'], as_index=False)
        .agg(
            accuracy=('accuracy', 'mean'),
            miss_rate=('miss_rate', 'mean')
        )
    )

    acc_mat = (agg.pivot(index='Modality', columns='Difficulty level', values='accuracy')
               .reindex(index=modality_order, columns=difficulty_order))
    miss_mat = (agg.pivot(index='Modality', columns='Difficulty level', values='miss_rate')
                .reindex(index=modality_order, columns=difficulty_order))

    sns.set_theme(style='white', context='paper', font_scale=1.1)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8), constrained_layout=True)

    sns.heatmap(
        acc_mat,
        ax=axes[0],
        annot=True,
        fmt='.1f',
        cmap='YlGnBu',
        cbar_kws={'label': 'Accuracy (%)'},
        linewidths=0.5,
        linecolor='white',
        vmin=max(0, np.nanmin(acc_mat.values) - 2),
        vmax=min(100, np.nanmax(acc_mat.values) + 2)
    )
    axes[0].set_title('Total Accuracy Matrix', fontweight='bold')
    axes[0].set_xlabel('Difficulty')
    axes[0].set_ylabel('Modality')

    sns.heatmap(
        miss_mat,
        ax=axes[1],
        annot=True,
        fmt='.1f',
        cmap='OrRd',
        cbar_kws={'label': 'Miss rate (%)'},
        linewidths=0.5,
        linecolor='white',
        vmin=max(0, np.nanmin(miss_mat.values) - 1),
        vmax=max(5, np.nanmax(miss_mat.values) + 1)
    )
    axes[1].set_title('Miss Rate Matrix', fontweight='bold')
    axes[1].set_xlabel('Difficulty')
    axes[1].set_ylabel('')

    fig.suptitle('Condition-Level Performance Landscape', fontsize=13, fontweight='bold')
    plt.show()
    fig.savefig('thesis_plot_1_performance_matrices.pdf', format='pdf', bbox_inches='tight')

    return {
        'subject_level': summary,
        'condition_level': agg,
        'accuracy_matrix': acc_mat,
        'miss_matrix': miss_mat
    }


def plot_efficiency_frontier_by_modality(perception_results_all, experiment_logs_all, color_palette):
    """
    Plot subject-level efficiency frontier per modality:
    x = collisions during cue windows (lower is better)
    y = total accuracy on valid trials (higher is better)

    Includes modality-specific Pareto envelopes to visualize best achievable
    trade-off regions.
    """
    records = []

    for subject_id, trials_df in perception_results_all.items():
        logs_df = experiment_logs_all.get(subject_id)
        if trials_df is None or trials_df.empty or logs_df is None or logs_df.empty:
            continue

        dfc = trials_df.copy()
        perc_angle_col, perc_dist_col, _, _ = _resolve_perception_columns(dfc)
        dfc['Modality'] = dfc['Modality'].astype(str).str.strip().str.lower()

        valid_mask = dfc[perc_angle_col].gt(0) & dfc[perc_dist_col].gt(0)
        valid_df = dfc.loc[valid_mask].copy()
        if valid_df.empty:
            continue

        valid_df['Is_Correct'] = (
            valid_df['Angle'].eq(valid_df[perc_angle_col]) &
            valid_df['Distance'].eq(valid_df[perc_dist_col])
        ).astype(float)

        acc_by_mod = valid_df.groupby('Modality')['Is_Correct'].mean() * 100

        collision_df = extract_collision_modality(logs_df, dfc, start_offset=24, end_offset=48)
        if collision_df.empty:
            continue

        collision_df['Modality'] = collision_df['Modality'].astype(str).str.strip().str.lower()
        col_by_mod = collision_df.groupby('Modality')['collisions'].mean()

        for mod in ['visual', 'auditory', 'haptic']:
            if mod in acc_by_mod.index and mod in col_by_mod.index:
                records.append({
                    'Participant ID': subject_id,
                    'Modality': mod,
                    'Accuracy (%)': float(acc_by_mod[mod]),
                    'Cue-Window Collisions': float(col_by_mod[mod])
                })

    plot_df = pd.DataFrame(records)
    if plot_df.empty:
        print('No matched perception/log data found for efficiency frontier plot.')
        return None

    sns.set_theme(style='whitegrid', context='paper', font_scale=1.1)
    fig, ax = plt.subplots(figsize=(8.5, 6))

    for mod in ['visual', 'auditory', 'haptic']:
        mod_df = plot_df[plot_df['Modality'] == mod].sort_values('Cue-Window Collisions')
        if mod_df.empty:
            continue

        sns.scatterplot(
            data=mod_df,
            x='Cue-Window Collisions',
            y='Accuracy (%)',
            color=color_palette[mod],
            s=55,
            alpha=0.75,
            edgecolor='black',
            linewidth=0.3,
            label=mod.capitalize(),
            ax=ax
        )

        frontier_x = []
        frontier_y = []
        best_y = -np.inf
        for _, row in mod_df.iterrows():
            y = row['Accuracy (%)']
            if y > best_y:
                frontier_x.append(row['Cue-Window Collisions'])
                frontier_y.append(y)
                best_y = y

        if len(frontier_x) >= 2:
            ax.plot(frontier_x, frontier_y, color=color_palette[mod], linewidth=2.0, linestyle='--', alpha=0.9)

    ax.set_title('Efficiency Frontier: Accuracy vs Collision Cost', fontweight='bold')
    ax.set_xlabel('Mean Collisions in Cue Window (lower is better)')
    ax.set_ylabel('Total Accuracy (%)')
    ax.legend(title='Modality', frameon=True)

    plt.tight_layout()
    plt.show()
    fig.savefig('thesis_plot_2_efficiency_frontier.pdf', format='pdf', bbox_inches='tight')

    return plot_df


def plot_learning_shift_early_vs_late(perception_results_all, color_palette):
    """
    Quantifies adaptation by comparing early vs late performance per participant
    and modality.

    Left subplot: ΔReaction Time vs ΔAccuracy (late - early)
    Right subplot: Distribution of ΔAccuracy by modality
    """
    rows = []

    for subject_id, df in perception_results_all.items():
        if df is None or df.empty:
            continue

        dfc = df.copy()
        perc_angle_col, perc_dist_col, _, trial_col = _resolve_perception_columns(dfc)
        dfc['Modality'] = dfc['Modality'].astype(str).str.strip().str.lower()

        for col in [perc_angle_col, perc_dist_col, 'Angle', 'Distance', 'Response start', 'Phase timestamp']:
            if col in dfc.columns:
                dfc[col] = pd.to_numeric(dfc[col], errors='coerce')

        if trial_col and trial_col in dfc.columns:
            dfc['Trial_Index'] = pd.to_numeric(dfc[trial_col], errors='coerce')
        else:
            dfc['Trial_Index'] = np.arange(1, len(dfc) + 1)

        dfc = dfc.sort_values('Trial_Index')

        for mod in ['visual', 'auditory', 'haptic']:
            mod_df = dfc[dfc['Modality'] == mod].copy()
            if len(mod_df) < 12:
                continue

            one_third = max(4, len(mod_df) // 3)
            early = mod_df.iloc[:one_third].copy()
            late = mod_df.iloc[-one_third:].copy()

            def compute_block_metrics(block_df):
                valid = block_df[(block_df[perc_angle_col] > 0) & (block_df[perc_dist_col] > 0)].copy()
                if valid.empty:
                    return np.nan, np.nan

                acc = ((valid['Angle'] == valid[perc_angle_col]) & (valid['Distance'] == valid[perc_dist_col])).mean() * 100
                rt = (valid['Response start'] - valid['Phase timestamp']).median()
                return acc, rt

            early_acc, early_rt = compute_block_metrics(early)
            late_acc, late_rt = compute_block_metrics(late)

            if pd.isna(early_acc) or pd.isna(late_acc) or pd.isna(early_rt) or pd.isna(late_rt):
                continue

            rows.append({
                'Participant ID': subject_id,
                'Modality': mod,
                'Delta Accuracy (%)': late_acc - early_acc,
                'Delta Reaction Time (s)': late_rt - early_rt
            })

    delta_df = pd.DataFrame(rows)
    if delta_df.empty:
        print('No enough data found for early-vs-late learning shift plot.')
        return None

    sns.set_theme(style='whitegrid', context='paper', font_scale=1.1)
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 5), gridspec_kw={'width_ratios': [1.2, 1]})

    for mod in ['visual', 'auditory', 'haptic']:
        md = delta_df[delta_df['Modality'] == mod]
        if md.empty:
            continue

        axes[0].scatter(
            md['Delta Reaction Time (s)'],
            md['Delta Accuracy (%)'],
            s=55,
            alpha=0.75,
            color=color_palette[mod],
            edgecolor='black',
            linewidth=0.3,
            label=mod.capitalize()
        )

    axes[0].axhline(0, color='black', linewidth=1, linestyle='--', alpha=0.7)
    axes[0].axvline(0, color='black', linewidth=1, linestyle='--', alpha=0.7)
    axes[0].set_title('Adaptation Shift Map', fontweight='bold')
    axes[0].set_xlabel('Δ Reaction Time (Late - Early, s)')
    axes[0].set_ylabel('Δ Accuracy (Late - Early, %)')
    axes[0].legend(title='Modality', frameon=True)

    sns.boxplot(
        data=delta_df,
        x='Modality',
        y='Delta Accuracy (%)',
        order=['visual', 'auditory', 'haptic'],
        palette={m: color_palette[m] for m in ['visual', 'auditory', 'haptic']},
        showfliers=False,
        ax=axes[1]
    )
    sns.stripplot(
        data=delta_df,
        x='Modality',
        y='Delta Accuracy (%)',
        order=['visual', 'auditory', 'haptic'],
        color='black',
        alpha=0.45,
        jitter=True,
        ax=axes[1]
    )
    axes[1].set_title('ΔAccuracy Distribution', fontweight='bold')
    axes[1].set_xlabel('')
    axes[1].set_ylabel('Δ Accuracy (%)')

    fig.suptitle('Early-to-Late Learning Dynamics', fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.show()
    fig.savefig('thesis_plot_3_learning_shift.pdf', format='pdf', bbox_inches='tight')

    return delta_df


def plot_spatial_error_landscape(perception_results_all, color_palette):
    """
    Shows where perception fails in space by modality:
    heatmap of mean angular error across true angle (1..8) and true distance (1..3).
    """
    df = _build_trial_level_dataframe(perception_results_all)
    if df.empty:
        print('No valid perception data was found for spatial error landscape.')
        return None

    valid = df[df['Is_Valid_Response']].copy()
    if valid.empty:
        print('No valid-response trials found for spatial error landscape.')
        return None

    valid['Angle'] = pd.to_numeric(valid['Angle'], errors='coerce')
    valid['Distance'] = pd.to_numeric(valid['Distance'], errors='coerce')

    modalities = ['visual', 'auditory', 'haptic']
    pivots = {}

    for mod in modalities:
        md = valid[valid['Modality'] == mod]
        piv = (md.pivot_table(index='Distance', columns='Angle', values='Angular_Error', aggfunc='mean')
               .reindex(index=[1, 2, 3], columns=[1, 2, 3, 4, 5, 6, 7, 8]))
        pivots[mod] = piv

    combined_vals = np.concatenate([p.values.flatten() for p in pivots.values()])
    combined_vals = combined_vals[~np.isnan(combined_vals)]
    if len(combined_vals) == 0:
        print('No valid angular error values available for spatial landscape.')
        return None

    vmin = max(0.0, np.nanmin(combined_vals))
    vmax = min(4.0, np.nanmax(combined_vals))

    sns.set_theme(style='white', context='paper', font_scale=1.05)
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.6), sharey=True, constrained_layout=True)

    for ax, mod in zip(axes, modalities):
        cmap = sns.light_palette(color_palette[mod], as_cmap=True)
        sns.heatmap(
            pivots[mod],
            ax=ax,
            cmap=cmap,
            vmin=vmin,
            vmax=vmax,
            annot=True,
            fmt='.2f',
            linewidths=0.4,
            linecolor='white',
            cbar=(mod == 'haptic'),
            cbar_kws={'label': 'Mean angular error'} if mod == 'haptic' else None
        )
        ax.set_title(mod.capitalize(), fontweight='bold')
        ax.set_xlabel('True Angle Index')
        if mod == 'visual':
            ax.set_ylabel('True Distance Level')
        else:
            ax.set_ylabel('')

    fig.suptitle('Spatial Error Landscape by Modality', fontsize=13, fontweight='bold')
    plt.show()
    fig.savefig('thesis_plot_4_spatial_error_landscape.pdf', format='pdf', bbox_inches='tight')

    return pivots


def plot_workload_vs_accuracy_by_difficulty(perception_results_all, experiment_logs_all, color_palette):
    """
    Tests whether workload proxies explain performance drops:
      - Subplot A: Accuracy vs collisions-per-second
      - Subplot B: Accuracy vs joystick effort
    Each point is participant x difficulty.
    """
    records = []
    difficulty_order = ['easy', 'medium', 'hard']

    for subject_id, trials_df in perception_results_all.items():
        logs_df = experiment_logs_all.get(subject_id)
        if trials_df is None or trials_df.empty or logs_df is None or logs_df.empty:
            continue

        tdf = trials_df.copy()
        ldf = logs_df.copy()
        perc_angle_col, perc_dist_col, _, _ = _resolve_perception_columns(tdf)

        if 'Difficulty level' not in tdf.columns or 'Difficulty level' not in ldf.columns:
            continue

        tdf['Difficulty level'] = tdf['Difficulty level'].astype(str).str.strip().str.lower()
        ldf['Difficulty level'] = ldf['Difficulty level'].astype(str).str.strip().str.lower()

        for diff in difficulty_order:
            t_phase = tdf[tdf['Difficulty level'] == diff].copy()
            l_phase = ldf[ldf['Difficulty level'] == diff].copy()

            if t_phase.empty or l_phase.empty:
                continue

            valid = t_phase[(t_phase[perc_angle_col] > 0) & (t_phase[perc_dist_col] > 0)].copy()
            if valid.empty:
                continue

            accuracy = ((valid['Angle'] == valid[perc_angle_col]) &
                        (valid['Distance'] == valid[perc_dist_col])).mean() * 100

            l_phase['Timestamp'] = pd.to_numeric(l_phase['Timestamp'], errors='coerce')
            l_phase['Number of collision'] = pd.to_numeric(l_phase['Number of collision'], errors='coerce')
            l_phase['Thumbstick x'] = pd.to_numeric(l_phase.get('Thumbstick x', np.nan), errors='coerce')
            l_phase['Thumbstick y'] = pd.to_numeric(l_phase.get('Thumbstick y', np.nan), errors='coerce')

            l_phase = l_phase.dropna(subset=['Timestamp', 'Number of collision']).sort_values('Timestamp')
            if l_phase.empty:
                continue

            duration = max(1e-6, l_phase['Timestamp'].max() - l_phase['Timestamp'].min())
            collision_rate = (l_phase['Number of collision'].max() - l_phase['Number of collision'].min()) / duration

            if 'Thumbstick x' in l_phase.columns and 'Thumbstick y' in l_phase.columns:
                joystick_effort = l_phase['Thumbstick x'].diff().abs().sum() + l_phase['Thumbstick y'].diff().abs().sum()
                joystick_effort = joystick_effort / max(1, len(l_phase))
            else:
                joystick_effort = np.nan

            records.append({
                'Participant ID': subject_id,
                'Difficulty': diff,
                'Accuracy (%)': accuracy,
                'Collision rate (per sec)': collision_rate,
                'Joystick effort (normalized)': joystick_effort
            })

    plot_df = pd.DataFrame(records)
    if plot_df.empty:
        print('No valid joined workload/accuracy data was found.')
        return None

    sns.set_theme(style='whitegrid', context='paper', font_scale=1.05)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), constrained_layout=True)

    diff_palette = {
        'easy': color_palette.get('easy', '#AEFF52'),
        'medium': color_palette.get('medium', '#FFE252'),
        'hard': color_palette.get('hard', '#FF5252')
    }

    for diff in difficulty_order:
        sub = plot_df[plot_df['Difficulty'] == diff]
        if sub.empty:
            continue

        sns.regplot(
            data=sub,
            x='Collision rate (per sec)',
            y='Accuracy (%)',
            ax=axes[0],
            scatter_kws={'s': 45, 'alpha': 0.65, 'color': diff_palette[diff], 'edgecolor': 'black'},
            line_kws={'color': diff_palette[diff], 'linewidth': 2},
            ci=95,
            truncate=False
        )

        sns.regplot(
            data=sub,
            x='Joystick effort (normalized)',
            y='Accuracy (%)',
            ax=axes[1],
            scatter_kws={'s': 45, 'alpha': 0.65, 'color': diff_palette[diff], 'edgecolor': 'black'},
            line_kws={'color': diff_palette[diff], 'linewidth': 2},
            ci=95,
            truncate=False
        )

    legend_handles = [
        mlines.Line2D([], [], color=diff_palette[d], marker='o', linestyle='-', label=d.capitalize())
        for d in difficulty_order
    ]

    axes[0].set_title('Accuracy vs Collision Load', fontweight='bold')
    axes[0].set_xlabel('Collision rate (collisions/sec)')
    axes[0].set_ylabel('Total Accuracy (%)')

    axes[1].set_title('Accuracy vs Joystick Effort', fontweight='bold')
    axes[1].set_xlabel('Joystick effort (mean |Δx|+|Δy| per sample)')
    axes[1].set_ylabel('Total Accuracy (%)')

    axes[1].legend(handles=legend_handles, title='Difficulty', frameon=True, loc='best')

    corr_rows = []
    for diff in difficulty_order:
        sub = plot_df[plot_df['Difficulty'] == diff].dropna(subset=['Accuracy (%)', 'Collision rate (per sec)'])
        if len(sub) > 2:
            rho_col, p_col = spearmanr(sub['Collision rate (per sec)'], sub['Accuracy (%)'])
        else:
            rho_col, p_col = np.nan, np.nan

        sub2 = plot_df[plot_df['Difficulty'] == diff].dropna(subset=['Accuracy (%)', 'Joystick effort (normalized)'])
        if len(sub2) > 2:
            rho_eff, p_eff = spearmanr(sub2['Joystick effort (normalized)'], sub2['Accuracy (%)'])
        else:
            rho_eff, p_eff = np.nan, np.nan

        corr_rows.append({
            'Difficulty': diff,
            'rho(accuracy, collision_rate)': rho_col,
            'p_collision': p_col,
            'rho(accuracy, joystick_effort)': rho_eff,
            'p_joystick': p_eff
        })

    corr_df = pd.DataFrame(corr_rows)

    plt.show()
    fig.savefig('thesis_plot_5_workload_vs_accuracy.pdf', format='pdf', bbox_inches='tight')

    print('\n=== Workload vs Accuracy correlations by difficulty (Spearman) ===')
    print(corr_df.to_string(index=False))

    return {
        'point_data': plot_df,
        'correlations': corr_df
    }




