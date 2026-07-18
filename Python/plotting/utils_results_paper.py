from utils import *


def plot_timing_metrics(subjects_data_trials, modality_colors):
    """
    Generates side-by-side box plots for response and reaction times across visual, auditory, and haptic modalities.
    """
    # Combine dictionary of DataFrames into one
    df_all = pd.concat(subjects_data_trials.values(), ignore_index=True)

    valid_df = df_all[~df_all['Perceived angle'].isin([0, -1])].copy()

    valid_df['Response time'] = valid_df['Response end'] - valid_df['Response start']
    valid_df['Reaction time'] = valid_df['Response start'] - valid_df['Phase timestamp']

    modality_order = ['visual', 'auditory', 'haptic']

    fig, axes = plt.subplots(1, 2, figsize=(12, 6))

    sns.boxplot(
        data=valid_df,
        x='Modality',
        y='Response time',
        order=modality_order,
        palette=modality_colors,
        ax=axes[0],
        showfliers=False
    )
    axes[0].set_title('Response Time by Modality')
    axes[0].set_ylabel('Response Time (s)')
    axes[0].set_ylim([0, 1.5])

    sns.boxplot(
        data=valid_df,
        x='Modality',
        y='Reaction time',
        order=modality_order,
        palette=modality_colors,
        ax=axes[1],
        showfliers=False
    )
    axes[1].set_title('Reaction Time by Modality')
    axes[1].set_ylabel('Reaction Time (s)')
    axes[1].set_ylim([0, 6])
    plt.tight_layout()
    plt.show()


def plot_misses_grouped_box(subjects_data_trials, modality_colors):
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

    sns.boxplot(
        data=misses_df,
        x='Difficulty level',
        y='is_miss',
        hue='Modality',
        order=difficulty_order,
        hue_order=modality_order,
        palette=modality_colors,
        showfliers=False
    )

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


def plot_error_boxplots_temp(error_distribution, ax=None):
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

    # Extract Set2 colors and map them to the desired order
    set2_colors = sns.color_palette("Set2")
    custom_palette = {
        'auditory': set2_colors[0],
        'haptic': set2_colors[1],
        'visual': set2_colors[2]
    }

    if standalone:
        fig, ax = plt.subplots(figsize=(14, 6))

    sns.boxplot(
        data=melted_df,
        x='error_type',
        y='count',
        hue='Modality',
        hue_order=modality_order,
        palette=custom_palette,
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



def test_perceptual_tunneling(perception_results_all):
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

    # Define distinct colors and markers
    palette = {'Visual': '#4C72B0', 'Auditory': '#55A868', 'Haptic': '#C44E52'}
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


def plot_speed_accuracy_density(df):
    """
    Generates a faceted 2D KDE contour plot to visualize the density
    of speed (Reaction Delay) vs. accuracy (Angular Error) for each modality.
    """
    # Create a copy to avoid altering the original dataframe's casing
    plot_df = df.copy()
    plot_df['Modality'] = plot_df['Modality'].str.capitalize()

    # Set publication-ready theme
    sns.set_theme(style="whitegrid", context="paper", font_scale=1.2)

    # Define a distinct color palette for the modalities
    palette = {'Visual': '#4C72B0', 'Auditory': '#55A868', 'Haptic': '#C44E52'}

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


def analyze_attention_redistribution(subjects_data_trials, experiment_logs_all, ax=None):
    """Calculates perception and motor metrics across difficulty levels to evaluate dual-task cognitive resource allocation.

    If `ax` is provided, the plot is drawn onto that Axes instead of creating
    a new figure, allowing this function to be embedded in a larger dashboard.
    """

    metrics_list = []

    for subject_id in subjects_data_trials.keys():
        trials_df = subjects_data_trials.get(subject_id)
        logs_df = experiment_logs_all.get(subject_id)

        if trials_df is None or trials_df.empty or logs_df is None or logs_df.empty:
            continue

        # Account for potential column name variations
        perc_angle_col = 'Angle perceived' if 'Angle perceived' in trials_df.columns else 'Perceived angle'
        perc_dist_col = 'Distance perceived' if 'Distance perceived' in trials_df.columns else 'Perceived distance'

        for difficulty in ['easy', 'medium', 'hard']:
            phase_trials = trials_df[trials_df['Difficulty level'] == difficulty].copy()
            phase_logs = logs_df[logs_df['Difficulty level'] == difficulty].copy()

            if phase_trials.empty or phase_logs.empty:
                continue

            # 1. Perception: Localization Accuracy
            valid_trials = phase_trials[(phase_trials[perc_angle_col] > 0) & (phase_trials[perc_dist_col] > 0)]
            if not valid_trials.empty:
                correct = ((valid_trials['Angle'] == valid_trials[perc_angle_col]) &
                           (valid_trials['Distance'] == valid_trials[perc_dist_col])).sum()
                accuracy = correct / len(phase_trials)
            else:
                accuracy = np.nan

            # 2. Perception: Reaction Speed (using Reaction Time)
            valid_rt = phase_trials[phase_trials['Response start'] > 0]
            avg_rt = (valid_rt['Response start'] - valid_rt['Phase timestamp']).mean() if not valid_rt.empty else np.nan

            # 3. Motor: Obstacle Avoidance (New collisions during this specific phase)
            collisions = phase_logs['Number of collision'].iloc[-1] - phase_logs['Number of collision'].iloc[0]

            # 4. Motor: Joystick Behavior (Control effort / variance)
            joystick_var = phase_logs['Thumbstick x'].var()

            # 5. Motor: Head Movement (Variance of X-axis head rotation)
            # Parses the "(x,y,z)" string format to extract the first float
            try:
                head_x = phase_logs['Head rotation'].str.strip('()').str.split(',', expand=True)[0].astype(float)
                head_var = head_x.var()
            except Exception:
                head_var = np.nan

            metrics_list.append({
                'Subject': subject_id,
                'Difficulty': difficulty,
                'Accuracy': accuracy,
                'Reaction Time': avg_rt,
                'Collisions': collisions,
                'Joystick Variance': joystick_var,
                'Head Variance': head_var
            })

    metrics_df = pd.DataFrame(metrics_list)

    # --- Normalization and Visualization ---
    cols_to_norm = ['Accuracy', 'Reaction Time', 'Collisions', 'Joystick Variance', 'Head Variance']
    norm_df = metrics_df.copy()

    # Z-score normalization for direct comparison of trends
    for col in cols_to_norm:
        norm_df[col] = (norm_df[col] - norm_df[col].mean()) / norm_df[col].std()

    avg_metrics = norm_df.groupby('Difficulty')[cols_to_norm].mean().reindex(['easy', 'medium', 'hard'])

    standalone = ax is None
    if standalone:
        fig, ax = plt.subplots(figsize=(10, 6))

    sns.lineplot(data=avg_metrics, markers=True, dashes=False, linewidth=2.5, ax=ax)

    ax.set_title('Shift in Attention Allocation Across Difficulty Levels (Z-Scored)', fontsize=14, pad=15)
    ax.set_ylabel('Normalized Metric Value (Z-Score)', fontsize=12)
    ax.set_xlabel('Task Difficulty (Workload)', fontsize=12)
    ax.legend(title='Variables', bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.grid(True, alpha=0.3)

    if standalone:
        plt.tight_layout()
        plt.show()

    return metrics_df


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


def plot_collision_vs_accuracy(perception_results_all, experiment_logs_all, ax=None):
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
    palette = {'Visual': '#4C72B0', 'Auditory': '#55A868', 'Haptic': '#C44E52'}

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


def test_mrt_interaction(subjects_data_trials, experiment_logs_all, axes=None):
    """
    Evaluates Multiple Resource Theory by plotting the Modality x Difficulty interaction
    for Reaction Time, Angular Error, and Cue-Window Collisions.

    If `axes` (an array-like of 3 Matplotlib Axes) is provided, the plots are
    drawn onto those axes instead of creating a new figure, allowing this
    function to be embedded in a larger dashboard.
    """
    interaction_data = []

    for subject_id in subjects_data_trials.keys():
        trials_df = subjects_data_trials.get(subject_id)
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

    palette = {'Visual': '#4C72B0', 'Auditory': '#55A868', 'Haptic': '#C44E52'}
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


def plot_accuracy_over_time_by_modality(subjects_data_trials):
    """Plots longitudinal accuracy trends by modality (auditory, haptic, visual) using the Set2 palette, excluding invalid/missed trials."""

    all_trials = []

    for subject_id, df in subjects_data_trials.items():
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

    # Extract Set2 colors and map them to the desired order
    set2_colors = sns.color_palette("Set2")
    palette = {
        'auditory': set2_colors[0],
        'haptic': set2_colors[1],
        'visual': set2_colors[2]
    }
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


def plot_longitudinal_performance(subjects_data_trials, experiment_logs_all):
    """
    Plots longitudinal trends of miss rate, angular accuracy, distance accuracy,
    and collisions from trial 1 to 216 without confidence interval shading.
    """
    all_trials = []

    for subject_id, df in subjects_data_trials.items():
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

    set2_colors = sns.color_palette("Set2")
    palette = {'auditory': set2_colors[0], 'haptic': set2_colors[1], 'visual': set2_colors[2]}
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
    axes[3].set_ylabel('Number of Collisions', fontweight='bold')
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


def plot_gender_differences_by_modality(perception_results_all, experiment_logs_all, demographics_path):
    """
        Calculates subject-level performance metrics broken down by modality,
        and plots them alongside the final total collisions for each gender.
        """

    # 1. Load demographics
    demo_df = pd.read_csv(demographics_path)
    demo_df['Folder_Name'] = list(perception_results_all.keys())

    # --- Part A: Extract Modality Metrics (Miss Rate & Accuracies) ---
    subject_metrics = []

    for subject_folder, df in perception_results_all.items():
        if df is None or df.empty:
            continue

        df_copy = df.copy()
        perc_angle_col = 'Angle perceived' if 'Angle perceived' in df_copy.columns else 'Perceived angle'
        perc_dist_col = 'Distance perceived' if 'Distance perceived' in df_copy.columns else 'Perceived distance'

        # Filter out hardware faults (-1)
        df_copy = df_copy[df_copy[perc_angle_col] >= 0].copy()
        df_copy['Modality'] = df_copy['Modality'].str.capitalize()

        for mod in ['Visual', 'Auditory', 'Haptic']:
            mod_df = df_copy[df_copy['Modality'] == mod]

            if mod_df.empty:
                continue

            miss_rate = (mod_df[perc_angle_col] == 0).mean()
            valid_trials = mod_df[(mod_df[perc_angle_col] > 0) & (mod_df[perc_dist_col] > 0)]

            if not valid_trials.empty:
                ang_acc = (valid_trials['Angle'] == valid_trials[perc_angle_col]).mean()
                dist_acc = (valid_trials['Distance'] == valid_trials[perc_dist_col]).mean()
            else:
                ang_acc = np.nan
                dist_acc = np.nan

            subject_metrics.append({
                'Folder_Name': subject_folder,
                'Modality': mod,
                'Miss Rate': miss_rate,
                'Angular Accuracy': ang_acc,
                'Distance Accuracy': dist_acc
            })

    metrics_df = pd.DataFrame(subject_metrics)
    merged_df = pd.merge(metrics_df, demo_df, on='Folder_Name', how='inner')
    merged_df = merged_df.dropna(subset=['Gender'])
    merged_df['Gender'] = merged_df['Gender'].str.capitalize()

    # Composite group for the X-axis (e.g., 'Visual\nMale')
    merged_df['Group'] = merged_df['Modality'] + '\n' + merged_df['Gender']

    # --- Part B: Extract Final Collisions Metric ---
    collision_metrics = []

    for subject_folder, logs_df in experiment_logs_all.items():
        if logs_df is None or logs_df.empty or 'Number of collision' not in logs_df.columns:
            final_col = np.nan
        else:
            # Drop trailing NaNs to ensure we get the last valid collision integer
            valid_logs = logs_df.dropna(subset=['Number of collision'])
            final_col = valid_logs['Number of collision'].iloc[-1] if not valid_logs.empty else np.nan

        collision_metrics.append({
            'Folder_Name': subject_folder,
            'Final Collisions': final_col
        })

    col_df = pd.DataFrame(collision_metrics)
    demo_col_df = pd.merge(col_df, demo_df, on='Folder_Name', how='inner')
    demo_col_df = demo_col_df.dropna(subset=['Gender'])
    demo_col_df['Gender'] = demo_col_df['Gender'].str.capitalize()

    # --- Plotting ---
    sns.set_theme(style="whitegrid", context="paper", font_scale=1.2)
    fig, axes = plt.subplots(1, 4, figsize=(24, 6))

    # Ordering and Palette for Modality Plots (Subplots 1-3)
    x_order_modality = [
        'Visual\nMale', 'Visual\nFemale',
        'Auditory\nMale', 'Auditory\nFemale',
        'Haptic\nMale', 'Haptic\nFemale'
    ]

    custom_palette = {
        'Visual\nMale': '#99DDFF', 'Visual\nFemale': '#99DDFF',
        'Auditory\nMale': '#BBCC33', 'Auditory\nFemale': '#BBCC33',
        'Haptic\nMale': '#EE8866', 'Haptic\nFemale': '#EE8866'
    }

    metrics_to_plot = ['Miss Rate', 'Angular Accuracy', 'Distance Accuracy']

    for i, metric in enumerate(metrics_to_plot):
        sns.boxplot(
            data=merged_df, x='Group', y=metric, order=x_order_modality,
            palette=custom_palette, ax=axes[i], showmeans=True,
            meanprops={"marker": "o", "markerfacecolor": "white", "markeredgecolor": "black", "markersize": "6"}
        )

        sns.stripplot(
            data=merged_df, x='Group', y=metric, order=x_order_modality,
            palette=custom_palette, ax=axes[i], alpha=0.6, jitter=True,
            edgecolor='gray', linewidth=0.5
        )

        axes[i].set_title(f'{metric} by Gender & Modality', fontweight='bold', fontsize=14)
        axes[i].set_xlabel('', fontweight='bold')
        axes[i].set_ylabel(f'Mean {metric}', fontweight='bold')
        axes[i].axvline(1.5, color='gray', linestyle=':', alpha=0.7)
        axes[i].axvline(3.5, color='gray', linestyle=':', alpha=0.7)

    # --- Subplot 4: Final Collisions ---
    # Distinct palette for overall Gender comparison
    gender_palette = {'Male': '#B0C4DE', 'Female': '#FFB6C1'}

    sns.boxplot(
        data=demo_col_df, x='Gender', y='Final Collisions', order=['Male', 'Female'],
        palette=gender_palette, ax=axes[3], showmeans=True, width=0.4,
        meanprops={"marker": "o", "markerfacecolor": "white", "markeredgecolor": "black", "markersize": "6"}
    )

    sns.stripplot(
        data=demo_col_df, x='Gender', y='Final Collisions', order=['Male', 'Female'],
        palette=gender_palette, ax=axes[3], alpha=0.6, jitter=True,
        edgecolor='gray', linewidth=0.5
    )

    axes[3].set_title('Final Total Collisions by Gender', fontweight='bold', fontsize=14)
    axes[3].set_xlabel('', fontweight='bold')
    axes[3].set_ylabel('Total Collisions', fontweight='bold')

    plt.tight_layout(pad=3.0)
    plt.show()

    return merged_df, demo_col_df

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





