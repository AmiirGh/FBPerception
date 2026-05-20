import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as mtick
import os
import scipy.stats as stats
import warnings
warnings.filterwarnings("ignore")
import time
from scipy.interpolate import make_interp_spline

def get_full_df_list():
    main_dir = './data'
    folders = os.listdir(main_dir)
    print(folders)
    filenames = []
    for folder in folders:
        path_to_files = os.path.join(main_dir, folder)
        files = os.listdir(path_to_files)
        csv_file = next(x for x in files if x.endswith(".csv"))
        filename = csv_file.split('.csv')[0]
        filename = filename.split('received_data')[1]
        filenames.append(os.path.join(path_to_files, csv_file))
    full_df = []
    for file in filenames:
        # print(file)
        subject_name = os.path.basename(file).split('received_data_')[1]
        # full_path = os.path.join(file_path, file)
        df = pd.read_csv(file)
        df["subject"] = subject_name
        full_df.append(df)
    return full_df


def extract_dynamic_obstacle_trials(df):
    """
    Detects rising edge in 'is_dynamic_obstacle_present' column and returns a DataFrame
    with only the valid perception rows (where the dynamic obstacle state rises from False to True).
    The feedback_modality is taken from the row immediately after the rise.
    """
    df = df.copy()

    # Ensure boolean
    df["is_dynamic_obstacle_present"] = df["is_dynamic_obstacle_present"].astype(bool)

    # Detect rising edge: FALSE → TRUE
    df["dynamic_rise"] = (
        df["is_dynamic_obstacle_present"]
        & ~df["is_dynamic_obstacle_present"].shift(1, fill_value=False)
    )

    # Set feedback_modality from the next row
    df.loc[df["dynamic_rise"], "feedback_modality"] = (
        df["feedback_modality"].shift(-1)
    )

    # Keep only valid perception rows
    trials = df[df["dynamic_rise"]].copy()
    return trials


def get_file_names(csv_files):
    filenames = []
    for csv_file in csv_files:
        filename = csv_file.split('.csv')[0]
        filename = filename.split('test128_')[1]
        filenames.append(filename)
    return filenames


def get_subjects_data_trials_df(subject_names, subjects_data_path):
    subjects_data_trials = {}
    for s_n in subject_names:
        trials_path = os.path.join(subjects_data_path, s_n, f"{s_n}_cleaned.xlsx")
        try:
            trials_data = pd.read_excel(trials_path)
        except: pass
        subjects_data_trials[s_n] = trials_data
    return subjects_data_trials


def get_subjects_data_full_df(subject_names, subjects_data_path):
    subjects_data_full = {}

    for s_n in subject_names:
        full_path = os.path.join(subjects_data_path, s_n, f"received_data_{s_n}.csv")
        full_data = pd.read_csv(full_path)
        subjects_data_full[s_n] = full_data
    return subjects_data_full



def get_df_list(csv_files, file_path):
    df_list = []
    for file in csv_files:
        subject_name = file.split('test128_')[1]
        # print(subject_name)
        full_path = os.path.join(file_path, file)
        df = pd.read_csv(full_path)
        df["subject"] = subject_name
        df_list.append(df)
    return df_list


def extract_collision_modality(df, trials_df, start_offset=24, end_offset=48):
    """
    Extract collisions in a time window AFTER rising edge,
    ignoring trials where the subject missed (degree_perceived == 0).
    """
    df = df.copy().reset_index(drop=True)

    df["is_dynamic_obstacle_present"] = df["is_dynamic_obstacle_present"].astype(bool)

    df["dynamic_rise"] = (
            df["is_dynamic_obstacle_present"] &
            ~df["is_dynamic_obstacle_present"].shift(1, fill_value=False)
    )

    df.loc[df["dynamic_rise"], "feedback_modality"] = (
        df["feedback_modality"].shift(-1)
    )

    trials = df[df["dynamic_rise"]].copy()

    collision_results = []

    for idx in trials.index:
        # 1. Identify which trial this is in the continuous data
        current_trial_num = df.loc[idx, "trial_number"]

        # 2. Look up this exact trial in the subjects_data_trials dataframe
        matching_trial = trials_df[trials_df["trial_number"] == current_trial_num]

        # 3. Check if the trial was missed
        if not matching_trial.empty:
            deg_perceived = matching_trial["degree_perceived"].iloc[0]
            if deg_perceived == 0 or deg_perceived == -1:
                continue
        else:
            # If for some reason the trial isn't in the trials_df, skip it to be safe
            continue

        # --- Proceed with collision calculation if not missed ---
        start_idx = idx + start_offset
        end_idx = min(idx + end_offset, len(df) - 1)

        if start_idx >= len(df):
            continue

        start_collision = df.loc[start_idx, "number_of_collision"]
        end_collision = df.loc[end_idx, "number_of_collision"]

        collisions_in_window = end_collision - start_collision

        collision_results.append({
            "feedback_modality": df.loc[idx, "feedback_modality"],
            "collisions": collisions_in_window
        })

    return pd.DataFrame(collision_results)



def get_all_miss_counts(subjects_data_trials):
    modalities = ['audio', 'haptic', 'visual']
    all_counts = []

    # Iterate through the dictionary (subject_name is the key, df is the dataframe)
    for subject_name, df in subjects_data_trials.items():
        # Safety check: skip if the DataFrame failed to load or is empty
        if df is None or df.empty:
            continue

        # Define a miss based on the data description (degree_perceived == 0)
        df_miss = df[df['degree_perceived'] == 0]

        counts = (df_miss['feedback_modality'].value_counts().reindex(modalities, fill_value=0).reset_index())

        counts.columns = ['feedback_modality', 'count']
        counts["subject"] = subject_name

        all_counts.append(counts)

    if all_counts: all_counts_df = pd.concat(all_counts, ignore_index=True)
    else: all_counts_df = pd.DataFrame(columns=['feedback_modality', 'count', 'subject'])

    return all_counts_df


def plot_all_miss_counts(all_miss_counts):
    fig, ax = plt.subplots(figsize=(8, 6))

    # Boxplot
    sns.boxplot(data=all_miss_counts, x='feedback_modality', y='count', palette="Set2", ax=ax)

    # Stripplot to show individual subject data points
    # sns.stripplot(data=all_miss_counts, x="feedback_modality", y="count", color="black", alpha=0.5, ax=ax)

    # Labels and Titles
    ax.set_xlabel('Feedback Modality')
    ax.set_ylabel('Miss Count')
    ax.yaxis.set_major_locator(mtick.MaxNLocator(integer=True))
    ax.set_title("Count of Missed Trials per Feedback Modality (All Subjects)")

    plt.tight_layout()
    plt.show()


# def is_normal(var):
#     statistic, p_value = stats.shapiro(audio)

'''
checks if the values in the variable are normal or not
'''
def is_normal(dist_values):
    statistic, p_value = stats.shapiro(dist_values)
    return True if p_value > 0.05 else False


def get_p_val_miss_counts(df):
    v_a_miss_counts_p_val = get_pairwise_p_value(df[df['feedback_modality'] == 'visual']['count'],
                                                 df[df['feedback_modality'] == 'audio']['count'])
    v_h_miss_counts_p_val = get_pairwise_p_value(df[df['feedback_modality'] == 'visual']['count'],
                                                 df[df['feedback_modality'] == 'haptic']['count'])
    return v_a_miss_counts_p_val, v_h_miss_counts_p_val



def get_pairwise_p_value(data1, data2):
    if is_normal(data1) and is_normal(data2):
        # stat, p_val = stats.ttest_ind(data1, data2)
        stat, p_val = stats.mannwhitneyu(data1, data2)
    else:
        stat, p_val = stats.mannwhitneyu(data1, data2)
    return p_val

def get_all_miss_counts_outliers(all_miss_counts, min_val):
    return all_miss_counts[all_miss_counts['count'] > min_val]


def get_miss_rates_by_generation_rate(subjects_data_trials):
    modalities = ['visual', 'haptic', 'audio']
    all_counts = []

    for subject_name, df in subjects_data_trials.items():
        if df is None or df.empty:
            continue

        df_miss = df[df['degree_perceived'] == 0]

        counts = (
            df_miss.groupby(['generation_rate', 'feedback_modality'])
            .size()
            .reset_index(name='count')
        )

        multi_index = pd.MultiIndex.from_product(
            [df['generation_rate'].unique(), modalities],
            names=['generation_rate', 'feedback_modality']
        )

        counts = (
            counts.set_index(['generation_rate', 'feedback_modality'])
            .reindex(multi_index, fill_value=0)
            .reset_index()
        )

        counts["subject"] = subject_name
        all_counts.append(counts)

    if all_counts:
        all_counts_df = pd.concat(all_counts, ignore_index=True)
        rates = sorted(all_counts_df["generation_rate"].unique())
    else:
        all_counts_df = pd.DataFrame(columns=['generation_rate', 'feedback_modality', 'count', 'subject'])
        rates = []
    return rates, all_counts_df


# Usage:
# gr, all_miss_counts_gr_df = get_miss_rates_by_generation_rate(subjects_data_trials)


def get_p_val_miss_counts_by_gr(df, gr):
    v_15 = df[(df['feedback_modality'] == 'visual') & (df['generation_rate'] == gr[0])]['count']
    v_20 = df[(df['feedback_modality'] == 'visual') & (df['generation_rate'] == gr[1])]['count']
    v_25 = df[(df['feedback_modality'] == 'visual') & (df['generation_rate'] == gr[2])]['count']

    a_15 = df[(df['feedback_modality'] == 'audio') & (df['generation_rate'] == gr[0])]['count']
    a_20 = df[(df['feedback_modality'] == 'audio') & (df['generation_rate'] == gr[1])]['count']
    a_25 = df[(df['feedback_modality'] == 'audio') & (df['generation_rate'] == gr[2])]['count']

    h_15 = df[(df['feedback_modality'] == 'haptic') & (df['generation_rate'] == gr[0])]['count']
    h_20 = df[(df['feedback_modality'] == 'haptic') & (df['generation_rate'] == gr[1])]['count']
    h_25 = df[(df['feedback_modality'] == 'haptic') & (df['generation_rate'] == gr[2])]['count']

    v_15_v_25_p_val = get_pairwise_p_value(v_15, v_25)
    v_15_v_20_p_val = get_pairwise_p_value(v_15, v_20)
    v_20_v_25_p_val = get_pairwise_p_value(v_20, v_25)

    return 20


def get_p_val_accuracy(accuracy_degree_all, accuracy_level_all, accuracy_full_all):
    v_deg = accuracy_degree_all[accuracy_degree_all['feedback_modality'] == 'visual']['accuracy_degree']
    v_lvl = accuracy_level_all[accuracy_level_all['feedback_modality'] == 'visual']['accuracy_level']
    v_full = accuracy_full_all[accuracy_full_all['feedback_modality'] == 'visual']['accuracy_full']

    a_deg = accuracy_degree_all[accuracy_degree_all['feedback_modality'] == 'audio']['accuracy_degree']
    a_lvl = accuracy_level_all[accuracy_level_all['feedback_modality'] == 'audio']['accuracy_level']
    a_full = accuracy_full_all[accuracy_full_all['feedback_modality'] == 'audio']['accuracy_full']

    h_deg = accuracy_degree_all[accuracy_degree_all['feedback_modality'] == 'haptic']['accuracy_degree']
    h_lvl = accuracy_level_all[accuracy_level_all['feedback_modality'] == 'haptic']['accuracy_level']
    h_full = accuracy_full_all[accuracy_full_all['feedback_modality'] == 'haptic']['accuracy_full']

    a_full_h_full_p_val = get_pairwise_p_value(a_full, h_full)
    a_deg_h_deg_p_val = get_pairwise_p_value(a_deg, h_deg)
    a_lvl_h_lvl_p_val = get_pairwise_p_value(a_lvl, h_lvl)

    return v_deg


def get_p_val_accuracy_by_gr(df_deg, df_lvl, df_full, gr):
    v_15_deg = df_deg[(df_deg['feedback_modality'] == 'visual') & (df_deg['generation_rate'] == gr[0])]['accuracy_degree']
    v_15_lvl = df_lvl[(df_lvl['feedback_modality'] == 'visual') & (df_lvl['generation_rate'] == gr[0])]['accuracy_level']
    v_15_ful = df_full[(df_full['feedback_modality'] == 'visual') & (df_full['generation_rate'] == gr[0])]['accuracy_full']

    v_20_deg = df_deg[(df_deg['feedback_modality'] == 'visual') & (df_deg['generation_rate'] == gr[1])]['accuracy_degree']
    v_20_lvl = df_lvl[(df_lvl['feedback_modality'] == 'visual') & (df_lvl['generation_rate'] == gr[1])]['accuracy_level']
    v_20_ful = df_full[(df_full['feedback_modality'] == 'visual') & (df_full['generation_rate'] == gr[1])]['accuracy_full']

    v_25_deg = df_deg[(df_deg['feedback_modality'] == 'visual') & (df_deg['generation_rate'] == gr[2])]['accuracy_degree']
    v_25_lvl = df_lvl[(df_lvl['feedback_modality'] == 'visual') & (df_lvl['generation_rate'] == gr[2])]['accuracy_level']
    v_25_ful = df_full[(df_full['feedback_modality'] == 'visual') & (df_full['generation_rate'] == gr[2])]['accuracy_full']
    #__________________________________
    a_15_deg = df_deg[(df_deg['feedback_modality'] == 'audio') & (df_deg['generation_rate'] == gr[0])]['accuracy_degree']
    a_15_lvl = df_lvl[(df_lvl['feedback_modality'] == 'audio') & (df_lvl['generation_rate'] == gr[0])]['accuracy_level']
    a_15_ful = df_full[(df_full['feedback_modality'] == 'audio') & (df_full['generation_rate'] == gr[0])]['accuracy_full']

    a_20_deg = df_deg[(df_deg['feedback_modality'] == 'audio') & (df_deg['generation_rate'] == gr[1])]['accuracy_degree']
    a_20_lvl = df_lvl[(df_lvl['feedback_modality'] == 'audio') & (df_lvl['generation_rate'] == gr[1])]['accuracy_level']
    a_20_ful = df_full[(df_full['feedback_modality'] == 'audio') & (df_full['generation_rate'] == gr[1])]['accuracy_full']

    a_25_deg = df_deg[(df_deg['feedback_modality'] == 'audio') & (df_deg['generation_rate'] == gr[2])]['accuracy_degree']
    a_25_lvl = df_lvl[(df_lvl['feedback_modality'] == 'audio') & (df_lvl['generation_rate'] == gr[2])]['accuracy_level']
    a_25_ful = df_full[(df_full['feedback_modality'] == 'audio') & (df_full['generation_rate'] == gr[2])]['accuracy_full']
    # __________________________________
    h_15_deg = df_deg[(df_deg['feedback_modality'] == 'haptic') & (df_deg['generation_rate'] == gr[0])]['accuracy_degree']
    h_15_lvl = df_lvl[(df_lvl['feedback_modality'] == 'haptic') & (df_lvl['generation_rate'] == gr[0])]['accuracy_level']
    h_15_ful = df_full[(df_full['feedback_modality'] == 'haptic') & (df_full['generation_rate'] == gr[0])]['accuracy_full']

    h_20_deg = df_deg[(df_deg['feedback_modality'] == 'haptic') & (df_deg['generation_rate'] == gr[1])]['accuracy_degree']
    h_20_lvl = df_lvl[(df_lvl['feedback_modality'] == 'haptic') & (df_lvl['generation_rate'] == gr[1])]['accuracy_level']
    h_20_ful = df_full[(df_full['feedback_modality'] == 'haptic') & (df_full['generation_rate'] == gr[1])]['accuracy_full']

    h_25_deg = df_deg[(df_deg['feedback_modality'] == 'haptic') & (df_deg['generation_rate'] == gr[2])]['accuracy_degree']
    h_25_lvl = df_lvl[(df_lvl['feedback_modality'] == 'haptic') & (df_lvl['generation_rate'] == gr[2])]['accuracy_level']
    h_25_ful = df_full[(df_full['feedback_modality'] == 'haptic') & (df_full['generation_rate'] == gr[2])]['accuracy_full']

    a_15_deg_h_15_deg_p_val = get_pairwise_p_value(a_15_deg, h_15_deg)
    a_15_lvl_h_15_lvl_p_val = get_pairwise_p_value(a_15_lvl, h_15_lvl)
    a_15_full_h_15_full_p_val = get_pairwise_p_value(a_15_ful, h_15_ful)

    a_20_deg_h_20_deg_p_val = get_pairwise_p_value(a_20_deg, h_20_deg)
    a_20_lvl_h_20_lvl_p_val = get_pairwise_p_value(a_20_lvl, h_20_lvl)
    a_20_full_h_20_full_p_val = get_pairwise_p_value(a_20_ful, h_20_ful)

    a_25_deg_h_25_deg_p_val = get_pairwise_p_value(a_25_deg, h_25_deg)
    a_25_lvl_h_25_lvl_p_val = get_pairwise_p_value(a_25_lvl, h_25_lvl)
    a_25_full_h_25_full_p_val = get_pairwise_p_value(a_25_ful, h_25_ful)


    return 20


def plot_all_miss_counts_by_generation_rate(miss_rates_by_gr, all_miss_counts_df):
    if not miss_rates_by_gr or all_miss_counts_df.empty:
        print("No data available to plot.")
        return

    fig, axes = plt.subplots(1, len(miss_rates_by_gr), figsize=(15, 5), sharey=True)
    if len(miss_rates_by_gr) == 1:
        axes = [axes]

    modality_order = ['audio', 'haptic', 'visual']
    m=0
    for i, (ax, rate) in enumerate(zip(axes, miss_rates_by_gr)):
        df_rate = all_miss_counts_df[all_miss_counts_df["generation_rate"] == rate]
        m+=1
        sns.boxplot(
            data=df_rate,
            x='feedback_modality',
            y='count',
            order=modality_order,
            palette="Set2",
            ax=ax,
            showfliers=False
        )

        # sns.stripplot(
        #     data=df_rate,
        #     x='feedback_modality',
        #     y='count',
        #     order=modality_order,
        #     color='black',
        #     alpha=0.5,
        #     ax=ax,
        # )

        # Titles and Labels
        if rate == 15: difficulty = 'easy'
        elif rate == 20: difficulty = 'medium'
        else:            difficulty = 'hard'
        ax.set_title(f"Difficulty: {difficulty}")
        ax.set_xlabel('Feedback Modality')
        ax.yaxis.set_major_locator(mtick.MaxNLocator(integer=True))

        if i == 0:
            ax.set_ylabel('Miss Count')
        else:
            ax.set_ylabel('')

    plt.suptitle("Count of Missed Trials by Generation Rate and Modality", fontsize=14, y=1.05)

    plt.tight_layout()
    plt.show()


def is_accuracy_degree(row):
    perceived = row["degree_perceived"]
    try:
        return int(perceived) == row["degree"]
    except:
        return False


def is_accuracy_level(row):
    level = row["level"]
    perceived = row["level_perceived"]

    try:
        return int(perceived) == int(level)
    except:
        return False


def get_accuracy_rates(subjects_data_trials):
    all_accuracy_degree = []
    all_accuracy_level = []
    all_accuracy_full = []

    for subject_name, df in subjects_data_trials.items():
        if df is None or df.empty:
            continue

        trials = df.copy()

        # --- NEW CODE: Filter out invalid data ---
        # Convert to numeric safely to catch both int 0 and string "0", then filter
        numeric_perceived = pd.to_numeric(trials["degree_perceived"], errors="coerce")
        trials = trials[~numeric_perceived.isin([0, -1])]

        # If the dataframe is empty after filtering out 0s, skip to the next subject
        if trials.empty:
            continue
        # -----------------------------------------

        trials["accuracy_degree"] = trials.apply(is_accuracy_degree, axis=1)
        trials["accuracy_level"] = trials.apply(is_accuracy_level, axis=1)
        trials["accuracy_full"] = trials["accuracy_degree"] & trials["accuracy_level"]

        sr = (trials.groupby("feedback_modality")["accuracy_degree"].mean().reset_index())
        sr["accuracy_degree"] *= 100
        sr["subject"] = subject_name
        all_accuracy_degree.append(sr)

        sl = (trials.groupby("feedback_modality")["accuracy_level"].mean().reset_index())
        sl["accuracy_level"] *= 100
        sl["subject"] = subject_name
        all_accuracy_level.append(sl)

        sf = (trials.groupby("feedback_modality")["accuracy_full"].mean().reset_index())
        sf["accuracy_full"] *= 100
        sf["subject"] = subject_name
        all_accuracy_full.append(sf)

    if all_accuracy_degree:
        accuracy_degree_all = pd.concat(all_accuracy_degree, ignore_index=True)
        accuracy_level_all = pd.concat(all_accuracy_level, ignore_index=True)
        accuracy_full_all = pd.concat(all_accuracy_full, ignore_index=True)
    else:
        accuracy_degree_all = pd.DataFrame(columns=["feedback_modality", "accuracy_degree", "subject"])
        accuracy_level_all = pd.DataFrame(columns=["feedback_modality", "accuracy_level", "subject"])
        accuracy_full_all = pd.DataFrame(columns=["feedback_modality", "accuracy_full", "subject"])

    return accuracy_degree_all, accuracy_level_all, accuracy_full_all


def plot_all_accuracy_rates(datasets):
    # Safety check
    if not datasets:
        print("No datasets available to plot.")
        return

    sns.set_theme(style="whitegrid")

    # Create subplots
    fig, axes = plt.subplots(1, 3, figsize=(18, 6), sharey=True)

    # Enforce a consistent order across all subplots so the bars don't jump around
    modality_order = ['audio', 'haptic', 'visual']

    for i, (ax, (data, y_col, y_title)) in enumerate(zip(axes, datasets)):
        # Check if the specific dataset is empty
        if data is None or data.empty:
            ax.set_title(f"{y_title}\n(No Data)")
            continue

        # Boxplot
        sns.boxplot(
            data=data,
            x="feedback_modality",
            y=y_col,
            order=modality_order,
            palette="Set2",
            ax=ax,
            showfliers=False
        )


        ax.set_title(y_title)
        ax.set_xlabel("Feedback Modality")

        ax.set_ylim(0, 105)

        # Clean up the Y-axis labels since they are shared
        if i == 0:
            ax.set_ylabel("Accuracy (%)")
        else:
            ax.set_ylabel("")  # Remove redundant labels on the 2nd and 3rd plots

    # Add overarching figure title
    fig.suptitle("Success Rates by Feedback Modality (All Subjects)", fontsize=14, y=1.05)

    plt.tight_layout()
    plt.show()


def get_accuracy_rates_by_generation_rate(subjects_data_trials):
    # Fixed variable names to be consistent with your return statement
    all_accuracy_degree = []
    all_accuracy_level = []
    all_accuracy_full = []

    # Iterate through the dictionary unpacking the subject name and their dataframe
    for subject_name, df in subjects_data_trials.items():
        # Safety check to skip empty or failed data loads
        if df is None or df.empty:
            continue

        # Use .copy() to avoid SettingWithCopyWarning
        trials = df.copy()

        # Apply your external functions to calculate accuracy
        trials["accuracy_degree"] = trials.apply(is_accuracy_degree, axis=1)
        trials["accuracy_level"] = trials.apply(is_accuracy_level, axis=1)
        trials["accuracy_full"] = trials["accuracy_degree"] & trials["accuracy_level"]

        # Calculate mean for degree accuracy grouped by generation rate and modality
        sr = (
            trials
            .groupby(["generation_rate", "feedback_modality"])["accuracy_degree"]
            .mean()
            .reset_index()
        )
        sr["accuracy_degree"] *= 100
        sr["subject"] = subject_name
        all_accuracy_degree.append(sr)

        # Calculate mean for level accuracy grouped by generation rate and modality
        sl = (
            trials
            .groupby(["generation_rate", "feedback_modality"])["accuracy_level"]
            .mean()
            .reset_index()
        )
        sl["accuracy_level"] *= 100
        sl["subject"] = subject_name
        all_accuracy_level.append(sl)

        # Calculate mean for full accuracy grouped by generation rate and modality
        sf = (
            trials
            .groupby(["generation_rate", "feedback_modality"])["accuracy_full"]
            .mean()
            .reset_index()
        )
        sf["accuracy_full"] *= 100
        sf["subject"] = subject_name
        all_accuracy_full.append(sf)

    # Combine everything into final DataFrames
    if all_accuracy_degree:
        accuracy_degree_all = pd.concat(all_accuracy_degree, ignore_index=True)
        accuracy_level_all = pd.concat(all_accuracy_level, ignore_index=True)
        accuracy_full_all = pd.concat(all_accuracy_full, ignore_index=True)
    else:
        # Fallback empty DataFrames if the dictionary was totally empty
        accuracy_degree_all = pd.DataFrame(columns=["generation_rate", "feedback_modality", "accuracy_degree", "subject"])
        accuracy_level_all = pd.DataFrame(columns=["generation_rate", "feedback_modality", "accuracy_level", "subject"])
        accuracy_full_all = pd.DataFrame(columns=["generation_rate", "feedback_modality", "accuracy_full", "subject"])

    return accuracy_degree_all, accuracy_level_all, accuracy_full_all


def plot_accuracy_rates_by_generation_rate(datasets):
    # Safety check: prevent crashing if nothing was passed
    if not datasets or datasets[0][0] is None or datasets[0][0].empty:
        print("No datasets available to plot.")
        return

    sns.set_theme(style="whitegrid")

    # Enforce consistent order across all subplots
    modality_order = ['audio', 'haptic', 'visual']

    # Extract and sort unique generation rates from the first dataset
    generation_rates = sorted(datasets[0][0]["generation_rate"].unique())

    # Create a separate figure for each generation rate
    for gr in generation_rates:
        fig, axes = plt.subplots(1, 3, figsize=(18, 5), sharey=True)

        for i, (ax, (data, y_col, y_title)) in enumerate(zip(axes, datasets)):

            # Catch empty data entirely
            if data is None or data.empty:
                ax.set_title(f"{y_title}\n(No Data)")
                continue

            # Filter data for the specific generation rate
            data_gr = data[data["generation_rate"] == gr]

            # Catch if a specific generation rate is missing for this subset
            if data_gr.empty:
                ax.set_title(f"{y_title}\n(No Data for GR={gr})")
                continue

            # Boxplot
            sns.boxplot(
                data=data_gr,
                x="feedback_modality",
                y=y_col,
                order=modality_order,
                palette="Set2",
                ax=ax,
            )

            # Overlay individual data points for transparency
            # sns.stripplot(
            #     data=data_gr,
            #     x="feedback_modality",
            #     y=y_col,
            #     order=modality_order,
            #     color="black",
            #     alpha=0.5,
            #     ax=ax
            # )

            # Titles and limits
            ax.set_title(y_title)
            ax.set_xlabel("Feedback Modality")

            # Set upper limit slightly above 100 to prevent dot clipping
            ax.set_ylim(0, 105)

            # Clean up the Y-axis labels since they share the Y-axis
            if i == 0:
                ax.set_ylabel("Accuracy (%)")
            else:
                ax.set_ylabel("")  # Remove redundant labels on 2nd and 3rd plots

        # Add overarching figure title
        fig.suptitle(f"Success Rates by Feedback Modality (Generation Rate: {gr})", fontsize=14, y=1.05)

        plt.tight_layout()
        plt.show()


def plot_collisions_all(subjects_data_full):
    all_time_data = []

    for subject_name, df in subjects_data_full.items():
        subject = subject_name
        df_sorted = df.sort_values("timestamp").reset_index(drop=True)
        # df_sorted = df
        temp = df_sorted[["timestamp", "number_of_collision"]].copy()
        temp["time_step"] = temp.index
        temp["subject"] = subject

        all_time_data.append(temp)
        pass
    all_time_df = pd.concat(all_time_data, ignore_index=True)

    plt.figure(figsize=(10, 4))

    sns.lineplot(data=all_time_df, x="time_step", y="number_of_collision", errorbar="ci")

    plt.xlabel("Time step")
    plt.ylabel("Cumulative Number of Collisions")
    plt.title("Cumulative Collisions Over Time (All Subjects)")
    plt.grid(True)

    plt.show()


def plot_collisions_over_time_by_difficulty(subjects_data_full):
    records = []

    diff_map = {15: 'Easy (Rate: 15)', 20: 'Medium (Rate: 20)', 25: 'Hard (Rate: 25)'}

    for subject, df in subjects_data_full.items():
        if df is None or df.empty:
            continue

        for rate, label in diff_map.items():
            block_df = df[df['generation_rate'] == rate].copy()

            if block_df.empty:
                continue

            # Normalize time to start at 0
            start_time = block_df['timestamp'].iloc[0]
            block_df['relative_time_sec'] = block_df['timestamp'] - start_time

            # Keep only the first 720 seconds
            block_df = block_df[block_df['relative_time_sec'] <= 720]

            # --- Normalize Collisions to start at 0 ---
            start_collision = block_df['number_of_collision'].iloc[0]
            block_df['phase_cum_collisions'] = block_df['number_of_collision'] - start_collision

            # Round time to nearest integer
            block_df['time_rounded'] = block_df['relative_time_sec'].round().astype(int)

            # Group by the rounded second, taking the maximum cumulative value reached in that second
            grouped = block_df.groupby('time_rounded')['phase_cum_collisions'].max().to_dict()

            for t_sec, cum_val in grouped.items():
                records.append({
                    'Subject': subject,
                    'Difficulty': label,
                    'Time (s)': t_sec,
                    'Cumulative Collisions': cum_val
                })

    df_plot = pd.DataFrame(records)
    if df_plot.empty:
        return

    plt.figure(figsize=(12, 7))

    order = ['Easy (Rate: 15)', 'Medium (Rate: 20)', 'Hard (Rate: 25)']
    custom_palette = ["green", "blue", "red"]

    sns.lineplot(
        data=df_plot,
        x='Time (s)',
        y='Cumulative Collisions',
        hue='Difficulty',
        hue_order=order,
        palette=custom_palette,
        linewidth=2.5
    )

    plt.title('Cumulative Collisions Over Time by Difficulty (Max 720s)', fontsize=15, fontweight='bold')
    plt.xlabel('Time Spent in Difficulty Phase (Seconds)', fontsize=13)
    plt.ylabel('Cumulative Number of Collisions', fontsize=13)

    plt.xlim(0, 720)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend(title='Difficulty Level', fontsize=11, title_fontsize=12, loc='upper left')

    plt.tight_layout()
    plt.show()


# Mock data test
np.random.seed(42)
mock_dict = {}
for i in range(15):  # 15 mock subjects
    df_list = []
    current_collisions = np.random.randint(0, 50)  # Some random starting point from previous phases

    for rate, duration in zip([15, 20, 25], [600, 750, 700]):
        time_array = np.arange(0, duration, 0.5) + np.random.uniform(0, 1000)

        # Determine accumulation rate based on difficulty
        rate_lambda = 0.02 if rate == 15 else (0.05 if rate == 20 else 0.1)
        increments = np.random.poisson(rate_lambda, len(time_array))

        collisions = current_collisions + increments.cumsum()
        current_collisions = collisions[-1]

        phase_df = pd.DataFrame({
            'timestamp': time_array,
            'generation_rate': rate,
            'number_of_collision': collisions
        })
        df_list.append(phase_df)

    mock_dict[f'Sub_{i}'] = pd.concat(df_list, ignore_index=True)


def plot_collisions_by_difficulty(subjects_data_full):
    records = []

    # Map the generation rate to your difficulty labels
    diff_map = {15: 'Easy (Rate: 15)', 20: 'Medium (Rate: 20)', 25: 'Hard (Rate: 25)'}

    for subject, df in subjects_data_full.items():
        if df is None or df.empty:
            continue

        df_copy = df.copy()

        # Calculate the exact number of collisions that happened per row
        # (Taking the difference of the cumulative count tells us when a new collision occurred)
        df_copy['collision_inc'] = df_copy['number_of_collision'].diff().fillna(0)

        # Filter to only positive increments (in case of game resets)
        df_copy['collision_inc'] = df_copy['collision_inc'].apply(lambda x: x if x > 0 else 0)

        # Sum these increments grouped by the generation rate
        grouped = df_copy.groupby('generation_rate')['collision_inc'].sum().to_dict()

        # Append to our plotting records
        for rate, label in diff_map.items():
            if rate in grouped:
                records.append({
                    'Subject': subject,
                    'Difficulty': label,
                    'Collisions': grouped[rate]
                })

    df_plot = pd.DataFrame(records)
    if df_plot.empty:
        print("No valid data available to plot.")
        return

    plt.figure(figsize=(9, 6))

    # 1. Define order and your custom palette
    order = ['Easy (Rate: 15)', 'Medium (Rate: 20)', 'Hard (Rate: 25)']
    custom_palette = ["green", "blue", "red"]

    # 2. Draw the Boxplot
    sns.boxplot(
        data=df_plot,
        x='Difficulty',
        y='Collisions',
        order=order,
        palette=custom_palette,
        width=0.5,
        showfliers=False  # We hide outliers here so the stripplot can handle them clearly
    )

    # 3. Overlay the individual subjects' data points (optional but highly recommended!)
    # This allows you to see the exact spread of your 50+ subjects
    sns.stripplot(
        data=df_plot,
        x='Difficulty',
        y='Collisions',
        order=order,
        color='black',
        alpha=0.6,
        jitter=True,
        size=5
    )

    # 4. Customize Aesthetics
    plt.title('Total Collisions by Difficulty Level', fontsize=14, fontweight='bold')
    plt.xlabel('Difficulty (Generation Rate)', fontsize=12)
    plt.ylabel('Total Number of Collisions', fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    plt.tight_layout()
    plt.show()
def calc_no_collisions_by_fbmod_for_time_window(subjects_data_full, subjects_data_trials, start_sec, end_sec):
    all_results = []

    for subject_name, df in subjects_data_full.items():
        # Safety check: Ensure we have the trial data for this subject
        if subject_name not in subjects_data_trials or subjects_data_trials[subject_name] is None:
            continue

        trials_df = subjects_data_trials[subject_name]

        start_offset = int(start_sec * 12)
        end_offset = int(end_sec * 12)

        # Pass the trials_df down to the extraction function
        results = extract_collision_modality(df, trials_df, start_offset=start_offset, end_offset=end_offset)

        # If the results are empty (e.g., all trials were missed), skip
        if results.empty:
            continue

        summary = (results.groupby("feedback_modality")["collisions"].sum().reset_index())
        summary["subject"] = subject_name
        all_results.append(summary)

    if not all_results:
        return pd.DataFrame()  # Return empty df if nothing matched

    all_summary = pd.concat(all_results, ignore_index=True)
    return all_summary


def plot_collision_time_windows(all_summary_0_2, all_summary_2_4, window_1, window_2):
    """
    Plots sequential box plots for Audio, Haptic, and Visual collisions
    across 0-2s and 2-4s, grouped by Modality color (Set2).
    """
    # 1. Make copies and label the time windows
    df1 = all_summary_0_2.copy()
    df2 = all_summary_2_4.copy()

    df1['Time Window'] = f'{window_1[0]}-{window_1[1]}s'
    df2['Time Window'] = f'{window_2[0]}-{window_2[1]}s'

    # 2. Combine the dataframes
    combined_df = pd.concat([df1, df2], ignore_index=True)

    # 3. Create a unified X-axis category combining Modality and Time
    # This allows us to map the color strictly to Modality while keeping all 6 boxes separate
    combined_df['Category'] = combined_df['feedback_modality'] + '\n' + combined_df['Time Window']

    # 4. Define the exact sequential order you requested
    order = [
        f'audio\n{window_1[0]}-{window_1[1]}s', f'audio\n{window_2[0]}-{window_2[1]}s',
        f'haptic\n{window_1[0]}-{window_1[1]}s', f'haptic\n{window_2[0]}-{window_2[1]}s',
        f'visual\n{window_1[0]}-{window_1[1]}s', f'visual\n{window_2[0]}-{window_2[1]}s'
    ]

    # 5. Create the Plot
    plt.figure(figsize=(10, 6))

    sns.boxplot(
        data=combined_df,
        x='Category',
        y='collisions',
        hue='feedback_modality',  # Forces the color to be tied to the modality
        order=order,
        palette='Set2',  # Applying the Set2 palette
        dodge=False,  # No dodging needed since each X-tick only has 1 box
        width=0.6,
        showfliers=False
    )

    # 6. Customize Aesthetics
    plt.title(f'Collisions by Feedback Modality ({window_1[0]}-{window_1[1]}s vs {window_2[0]}-{window_2[1]}ss)', fontsize=14)
    plt.xlabel('Feedback Modality & Time Window', fontsize=12)
    plt.ylabel('Number of Collisions', fontsize=12)
    plt.legend(title='Feedback Modality', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    plt.tight_layout()
    plt.show()


def plot_multiple_collision_time_windows(windows_list, subjects_data_full, subjects_data_trials):
    """
    Plots stacked box plots (3 rows, 1 column) for Audio, Haptic, and Visual
    collisions across time windows, with smooth mean curves overlaid.
    """
    # 2. Run the calculation in a loop and combine the results
    window_summaries = []
    for w in windows_list:
        # Calculate for the specific window
        summary_df = calc_no_collisions_by_fbmod_for_time_window(
            subjects_data_full,
            subjects_data_trials,
            start_sec=w[0],
            end_sec=w[1]
        )

        # Tag the dataframe with its specific time window
        summary_df['Time Window'] = f'{w[0]}-{w[1]}s'
        window_summaries.append(summary_df)

    # Combine all 5 windows into one large dataframe
    combined_all_windows = pd.concat(window_summaries, ignore_index=True)

    # 1. Define the exact order of time windows
    time_order = [f"{w[0]}-{w[1]}s" for w in windows_list]
    modalities = ['audio', 'haptic', 'visual']

    # 2. Extract colors from Set2 to match your previous styling
    palette = sns.color_palette('Set2')
    color_map = {'audio': palette[0], 'haptic': palette[1], 'visual': palette[2]}

    # 3. Create a vertically stacked grid (3 rows, 1 col)
    # sharex and sharey ensure the scales match perfectly across all 3 modalities
    fig, axes = plt.subplots(3, 1, figsize=(14, 12), sharex=True, sharey=True)

    for i, mod in enumerate(modalities):
        ax = axes[i]

        # Isolate the data for the current modality
        mod_data = combined_all_windows[combined_all_windows['feedback_modality'] == mod]

        # 4. Plot Boxplot on the specific axis (ax)
        sns.boxplot(
            data=mod_data,
            x='Time Window',
            y='collisions',
            order=time_order,
            color=color_map[mod],
            width=0.4,
            showfliers=False,
            boxprops={'alpha': 0.4},  # Transparency for the line
            ax=ax
        )

        # 5. Calculate and align the Means
        means = mod_data.groupby('Time Window')['collisions'].mean().reset_index()
        x_map = {cat: idx for idx, cat in enumerate(time_order)}
        means['x'] = means['Time Window'].map(x_map)
        means = means.sort_values('x')

        x = means['x'].values
        y = means['collisions'].values

        # Scatter the exact mean points
        ax.scatter(x, y, color=color_map[mod], s=70, edgecolor='black', zorder=5)

        # 6. Generate a smooth curve using a Cubic Spline
        if len(x) >= 4:
            x_smooth = np.linspace(x.min(), x.max(), 300)
            spline = make_interp_spline(x, y, k=3)
            y_smooth = spline(x_smooth)
        else:
            x_smooth, y_smooth = x, y

        ax.plot(x_smooth, y_smooth, color=color_map[mod], linewidth=3.5, zorder=4)

        # 7. Customize each subplot's aesthetics
        ax.set_title(f'{mod.capitalize()} Modality', fontsize=13, fontweight='bold')
        ax.set_ylabel('Collisions', fontsize=11)
        ax.grid(axis='y', linestyle='--', alpha=0.7)

        # Only show the X-axis label on the very bottom plot
        if i == 2:
            ax.set_xlabel('Time Window (seconds)', fontsize=12)
        else:
            ax.set_xlabel('')

    # 8. Final Layout Adjustments
    fig.suptitle('Collisions Over Time by Modality (0s to 5s)', fontsize=16, y=0.98)
    plt.tight_layout()
    plt.show()


def compare_time_windows_significance(all_summary_0_2, all_summary_2_4):
    """
    Calculates the p-value for the difference in collisions between
    the 0-2s and 2-4s time windows for each feedback modality.
    """
    modalities = ['audio', 'haptic', 'visual']
    p_values = {}

    print("=" * 45)
    print(" STATISTICAL SIGNIFICANCE (0-2s vs 2-4s)")
    print("=" * 45)

    for mod in modalities:
        # 1. Extract the collision counts for the current modality in the 0-2s window
        data_0_2 = all_summary_0_2[all_summary_0_2['feedback_modality'] == mod]['collisions']

        # 2. Extract the collision counts for the current modality in the 2-4s window
        data_2_4 = all_summary_2_4[all_summary_2_4['feedback_modality'] == mod]['collisions']

        # 3. Use your custom function to calculate the p-value
        p_val = get_pairwise_p_value(data_0_2, data_2_4)

        # 4. Store the result
        p_values[mod] = p_val

        # 5. Format a nice print output with significance stars
        if p_val < 0.001:
            sig = "*** (Highly Significant)"
        elif p_val < 0.01:
            sig = "** (Very Significant)"
        elif p_val < 0.05:
            sig = "* (Significant)"
        else:
            sig = "ns (Not Significant)"

        print(f"{mod.upper():<8} Modality | p-value: {p_val:.4f} {sig}")

    print("=" * 45)
    return p_values


def plot_no_collisions_by_fbmod_for_time_window(all_summary, start_sec, end_sec):


    fig, ax = plt.subplots()

    sns.boxplot(data=all_summary, x="feedback_modality", y="collisions", hue="feedback_modality", palette="Set2",
        legend=False, ax=ax)

    ax.set_xlabel("Feedback Modality")
    ax.set_ylabel(f"Collisions in [{start_sec}-{end_sec}] seconds")
    ax.set_title(f"Collisions per Feedback Modality (window={start_sec}-{end_sec}s)")
    ax.grid()
    plt.show()


def no_col_by_fbmod_p_val_df(df):
    v = df[df["feedback_modality"] == "visual"]['collisions']
    a = df[df["feedback_modality"] == "audio"]['collisions']
    h = df[df["feedback_modality"] == "haptic"]['collisions']
    v_a_p_val = get_pairwise_p_value(v, a)
    v_h_p_val = get_pairwise_p_value(v, h)
    a_h_p_val = get_pairwise_p_value(a, h)
    pass

def plot_mean_head_position_heatmap(subjects_data_trials, bins=50):
    """
    Creates a 2D heatmap of mean head position density (x, y) across all subjects.

    Parameters:
        df_list (list of pd.DataFrame): list of dataframes containing 'head_position'
        bins (int): resolution of the heatmap
    """

    all_x = []
    all_y = []

    for subject_name, df in subjects_data_trials.items():
        # Drop NaNs just in case
        valid_positions = df["head_position"].dropna()

        for pos in valid_positions:
            try:
                # Remove parentheses and split
                x, y, z = pos.strip("()").split(",")
                all_x.append(float(x))
                all_y.append(float(y))
            except Exception:
                continue  # skip malformed rows

    all_x = np.array(all_x)
    all_y = np.array(all_y)

    # Create 2D histogram (density)
    heatmap, xedges, yedges = np.histogram2d(all_x, all_y, bins=bins)

    # Normalize to get "mean presence"
    heatmap = heatmap / np.sum(heatmap)

    # Plot
    plt.figure()
    plt.imshow(
        heatmap.T,
        origin='lower',
        aspect='auto',
        extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]]
    )
    plt.colorbar(label="Normalized Density")
    plt.xlabel("X Position")
    plt.ylabel("Y Position")
    plt.title("Mean Head Position Heatmap (All Subjects)")
    plt.show()


def plot_thumbstick_heatmap(subjects_data_trials, bins=50):
    all_x = []
    all_y = []

    for subject_name, df in subjects_data_trials.items():
        x = df["right_thumbstick_x"].dropna().values
        y = df["right_thumbstick_y"].dropna().values

        all_x.extend(x)
        all_y.extend(y)

    all_x = np.array(all_x)
    all_y = np.array(all_y)

    heatmap, xedges, yedges = np.histogram2d(all_x, all_y, bins=bins)
    heatmap = heatmap / np.sum(heatmap)

    plt.figure()
    plt.imshow(heatmap.T, origin='lower', extent=[-1, 1, -1, 1], aspect='auto')
    plt.colorbar(label="Normalized Density")
    plt.xlabel("Thumbstick X")
    plt.ylabel("Thumbstick Y")
    plt.title("Thumbstick Usage Heatmap")
    plt.show()


def get_final_collision_by_gr(subjects_data_full):

    difficulty_map = {15: "Easy", 20: "Medium", 25: "Hard"}
    results = {"Easy": [], "Medium": [], "Hard": []}

    for subject_name, df in subjects_data_full.items():
        df = df.sort_index().reset_index(drop=True)

        # Identify blocks where difficulty changes
        df["block"] = (df["generation_rate"] != df["generation_rate"].shift()).cumsum()

        for _, block_df in df.groupby("block"):
            rate = block_df["generation_rate"].iloc[0]

            if rate not in difficulty_map:
                continue
            last_collision = block_df["number_of_collision"].iloc[-1]
            start_idx = block_df.index[0]
            if start_idx == 0:
                prev_collision = 0
            else:
                prev_collision = df.loc[start_idx - 1, "number_of_collision"]

            delta = last_collision - prev_collision

            results[difficulty_map[rate]].append(delta)

    data = [results["Easy"], results["Medium"], results["Hard"]]
    return data


def plot_final_collisions_by_gr(data):
    plt.figure()
    plt.boxplot(data, labels=["Easy", "Medium", "Hard"])
    plt.grid()
    plt.ylabel("Number of Collisions (per block)")
    plt.title("Collisions per Difficulty Level (Randomized Order)")
    plt.show()


def final_coll_by_gr_p_val_df(final_collision_by_gr):
    e = final_collision_by_gr[0]
    m = final_collision_by_gr[1]
    h = final_collision_by_gr[2]
    e_m_p_val = get_pairwise_p_value(e, m)
    e_h_p_val = get_pairwise_p_value(e, h)
    m_h_p_val = get_pairwise_p_value(m, h)
    pass


def plot_spatial_perception(subjects_data_trials, fbmod="visual"):
    # Cleaner dictionary mapping instead of long if/elif chain
    def degree_to_angle(d):
        mapping = {
            1: 2 * np.pi / 4,
            2: np.pi / 4,
            3: 0,
            4: 7 * np.pi / 4,
            5: 6 * np.pi / 4,
            6: 5 * np.pi / 4,
            7: 4 * np.pi / 4,
            8: 3 * np.pi / 4
        }
        return mapping.get(d, 0)

    level_to_radius = lambda l: l

    all_data = []
    palette = sns.color_palette('Set2')
    color_map = {
        'audio': palette[0],
        'haptic': palette[1],
        'visual': palette[2]
    }

    # Get the specific color for the current modality (with a fallback just in case)
    mod_color = color_map.get(fbmod, 'tab:blue')

    # -------- aggregate all subjects --------
    for subject_name, df in subjects_data_trials.items():
        if df is None or df.empty:
            continue

        # Filter by requested modality
        df_mod = df[df["feedback_modality"] == fbmod].copy()

        # Remove misses (0) and setup misses (-1)
        # since they have no physical coordinates to plot
        df_mod = df_mod[df_mod["degree_perceived"] > 0]

        # Verify columns exist before appending
        cols = ["degree", "level", "degree_perceived", "level_perceived"]
        if all(c in df_mod.columns for c in cols):
            all_data.append(df_mod[cols])

    # Safety check if modality data is missing entirely
    if not all_data:
        print(f"No valid spatial data found for modality: {fbmod}")
        return

    data = pd.concat(all_data, ignore_index=True)

    # -------- plotting --------
    fig, axes = plt.subplots(
        3, 8,
        subplot_kw={'projection': 'polar'},
        figsize=(20, 10)
    )

    for l in range(1, 4):
        for d in range(1, 9):

            ax = axes[l - 1, d - 1]

            subset = data[(data["degree"] == d) & (data["level"] == l)]

            R = level_to_radius(l)

            # --- radial reference circles ---
            theta_full = np.linspace(0, 2 * np.pi, 200)

            # Cleaned up reference circles to map exactly to levels 1, 2, and 3
            ax.plot(theta_full, np.full_like(theta_full, 1), alpha=0.2, color='gray')
            ax.plot(theta_full, np.full_like(theta_full, 2), alpha=0.2, color='gray')
            ax.plot(theta_full, np.full_like(theta_full, 3), alpha=0.2, color='gray')

            # --- true stimulus arrow ---
            ax.arrow(
                degree_to_angle(d), 0,
                0, R,
                width=0.09,
                alpha=0.9,
                color='red',
                length_includes_head=True  # Prevents arrowheads from extending past the level
            )

            # --- aggregated perceived responses ---
            if len(subset) > 0:
                grouped = subset.groupby(["degree_perceived", "level_perceived"]).size().reset_index(name="count")

                angles = grouped["degree_perceived"].apply(degree_to_angle)
                radii = grouped["level_perceived"].apply(level_to_radius)

                sizes = grouped["count"] * 20  # tweak if needed

                ax.scatter(
                    angles,
                    radii,
                    s=sizes,
                    alpha=0.6,
                    color=mod_color,  # Uses the mapped Set2 color!
                    zorder=3  # Ensures the dots plot above the gray radial gridlines
                )

            ax.set_ylim(0, 3.5)
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_title(f"D{d} L{l}", fontsize=19)

    plt.suptitle(f"Spatial Perception ({fbmod.capitalize()} Modality)", fontsize=25)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.show()


def compute_error_by_modality(subjects_data_trials):
    all_results = []

    # Iterate through the dictionary unpacking the subject name and their dataframe
    for subject_name, df in subjects_data_trials.items():
        if df is None or df.empty:
            continue

        df = df.copy()

        # Remove invalid perceived values (0 = miss, -1 = setup miss)
        df = df[(df['degree_perceived'] != 0) & (df['degree_perceived'] != -1)]

        # If a dataframe becomes empty after filtering, skip it
        if df.empty:
            continue

        # Degree error (circular: max distance on an 8-point circle is 4)
        diff = np.abs(df['degree'] - df['degree_perceived'])
        df['deg_error'] = np.minimum(diff, 8 - diff)

        # Level error (linear)
        df['lvl_error'] = np.abs(df['level'] - df['level_perceived'])

        # Record the subject ID directly from the dictionary key
        df['subject_id'] = subject_name

        all_results.append(df[['subject_id', 'feedback_modality', 'deg_error', 'lvl_error']])

    # Safety check if no valid data remains
    if not all_results:
        print("No valid error data found after filtering.")
        return pd.DataFrame(), pd.DataFrame()

    combined = pd.concat(all_results, ignore_index=True)

    # =====================================================================
    # --- A. PER-SUBJECT DISTRIBUTIONS ---
    # =====================================================================

    # Group by BOTH modality and subject_id
    deg_counts_dist = (
        combined.groupby(['feedback_modality', 'subject_id'])['deg_error']
        .value_counts()
        .unstack(fill_value=0)
        .reindex(columns=range(5), fill_value=0)
    )
    deg_counts_dist.columns = [f"deg_err_{i}" for i in deg_counts_dist.columns]

    lvl_counts_dist = (
        combined.groupby(['feedback_modality', 'subject_id'])['lvl_error']
        .value_counts()
        .unstack(fill_value=0)
        .reindex(columns=range(3), fill_value=0)
    )
    lvl_counts_dist.columns = [f"lvl_err_{i}" for i in lvl_counts_dist.columns]

    # Combine into the distribution dataframe
    subject_distributions = deg_counts_dist.join(lvl_counts_dist).reset_index()

    # =====================================================================
    # --- B. OVERALL AGGREGATE ---
    # =====================================================================

    # We can efficiently get the overall sums by grouping the subject distributions
    overall_results = (
        subject_distributions
        .drop(columns=['subject_id'])
        .groupby('feedback_modality')
        .sum()
        .reset_index()
    )

    # Weighted mean degree error
    deg_cols = [f"deg_err_{i}" for i in range(5)]
    deg_weights = np.array(range(5))

    overall_results['weighted_mean_deg_err'] = ((overall_results[deg_cols].values @ deg_weights)
                                                / overall_results[deg_cols].sum(axis=1))

    # Weighted mean level error
    lvl_cols = [f"lvl_err_{i}" for i in range(3)]
    lvl_weights = np.array(range(3))

    overall_results['weighted_mean_lvl_err'] = (
                                                       overall_results[lvl_cols].values @ lvl_weights
                                               ) / overall_results[lvl_cols].sum(axis=1)

    return overall_results, subject_distributions


def get_lvl_err_1_p_value(error_distribution):
    # Extract audio and haptic data
    audio = error_distribution[error_distribution['feedback_modality'] == 'audio'][['subject_id', 'lvl_err_1']]
    haptic = error_distribution[error_distribution['feedback_modality'] == 'haptic'][['subject_id', 'lvl_err_1']]

    # Merge on subject_id to ensure the pairs match up correctly
    merged = pd.merge(audio, haptic, on='subject_id', suffixes=('_audio', '_haptic'))

    lvl_err_1_a_h = get_pairwise_p_value(merged['lvl_err_1_audio'], merged['lvl_err_1_haptic'])

    return lvl_err_1_a_h



def evaluate_outliers_performance(outlier_names, subject_distributions):
    """
    Compares the audio and haptic performance of specific outlier subjects
    against the rest of the population.
    """
    # 1. Filter for only audio and haptic modalities
    df_filtered = subject_distributions[
        subject_distributions['feedback_modality'].isin(['audio', 'haptic'])
    ].copy()

    # 2. Assign subjects to either 'Outliers' or 'Population'
    df_filtered['Group'] = np.where(
        df_filtered['subject_id'].isin(outlier_names),
        'Outliers',
        'Population'
    )

    # 3. Aggregate the error counts for both groups
    # Drop subject_id so we just sum up the error counts per Group and Modality
    group_sums = df_filtered.drop(columns=['subject_id']).groupby(['Group', 'feedback_modality']).sum().reset_index()

    # 4. Calculate weighted mean degree error
    deg_cols = [f"deg_err_{i}" for i in range(5)]
    deg_weights = np.array(range(5))

    # Avoid division by zero if a group has no data
    deg_totals = group_sums[deg_cols].sum(axis=1)
    group_sums['mean_deg_err'] = np.where(
        deg_totals > 0,
        (group_sums[deg_cols].values @ deg_weights) / deg_totals,
        np.nan
    )

    # 5. Calculate weighted mean level error
    lvl_cols = [f"lvl_err_{i}" for i in range(3)]
    lvl_weights = np.array(range(3))

    lvl_totals = group_sums[lvl_cols].sum(axis=1)
    group_sums['mean_lvl_err'] = np.where(
        lvl_totals > 0,
        (group_sums[lvl_cols].values @ lvl_weights) / lvl_totals,
        np.nan
    )

    results = group_sums[['Group', 'feedback_modality', 'mean_deg_err', 'mean_lvl_err']]

    # 6. Print the Comparison
    print("=" * 60)
    print(" OUTLIERS VS POPULATION PERFORMANCE (AUDIO & HAPTIC)")
    print("=" * 60)

    for mod in ['audio', 'haptic']:
        print(f"\n--- {mod.upper()} MODALITY ---")

        # Safely extract values
        try:
            outlier_deg = \
            results[(results['Group'] == 'Outliers') & (results['feedback_modality'] == mod)]['mean_deg_err'].values[0]
            pop_deg = \
            results[(results['Group'] == 'Population') & (results['feedback_modality'] == mod)]['mean_deg_err'].values[
                0]

            outlier_lvl = \
            results[(results['Group'] == 'Outliers') & (results['feedback_modality'] == mod)]['mean_lvl_err'].values[0]
            pop_lvl = \
            results[(results['Group'] == 'Population') & (results['feedback_modality'] == mod)]['mean_lvl_err'].values[
                0]

            # Print Degree Error Comparison
            deg_status = "BETTER (Less Error)" if outlier_deg < pop_deg else "WORSE (More Error)"
            print(
                f"Degree Error : Outliers = {outlier_deg:.3f} | Population = {pop_deg:.3f}  --> Outliers are {deg_status}")

            # Print Level Error Comparison
            lvl_status = "BETTER (Less Error)" if outlier_lvl < pop_lvl else "WORSE (More Error)"
            print(
                f"Level Error  : Outliers = {outlier_lvl:.3f} | Population = {pop_lvl:.3f}  --> Outliers are {lvl_status}")

        except IndexError:
            print("Not enough data to compare for this modality.")

    print("\n" + "=" * 60)
    return results



def plot_error_bars(results):
    # Safety check
    if results is None or results.empty:
        print("No error results available to plot.")
        return

    sns.set_theme(style="whitegrid")

    # --- Select columns (exclude *_0) ---
    deg_cols = [col for col in results.columns if col.startswith('deg_err_') and col != 'deg_err_0']
    lvl_cols = [col for col in results.columns if col.startswith('lvl_err_') and col != 'lvl_err_0']
    all_cols = deg_cols + lvl_cols

    # Melt the dataframe: converts it from wide format to long format
    # which Seaborn handles perfectly for grouped bar charts
    df_melted = results.melt(
        id_vars=['feedback_modality'],
        value_vars=all_cols,
        var_name='error_type',
        value_name='count'
    )

    # Clean up the X-axis labels (e.g., 'deg_err_1' -> 'Degree Err 1')
    label_mapping = {
        col: col.replace('deg_err_', 'Degree Err ').replace('lvl_err_', 'Level Err ')
        for col in all_cols
    }
    df_melted['error_type'] = df_melted['error_type'].map(label_mapping)

    # Enforce consistent order across all your visualizations
    modality_order = ['audio', 'haptic', 'visual']

    # --- Plotting ---
    fig, ax = plt.subplots(figsize=(12, 6))

    # Seaborn automatically handles the grouped bar offsets
    sns.barplot(
        data=df_melted,
        x='error_type',
        y='count',
        hue='feedback_modality',
        hue_order=modality_order,
        palette="Set2",
        ax=ax,
        edgecolor='black',  # Adds a subtle border to separate the bars cleanly
        linewidth=0.5
    )

    # --- Labels & Formatting ---
    ax.set_xlabel("Error Type and Magnitude")
    ax.set_ylabel("Total Count")
    ax.set_title("Degree and Level Error Distribution by Modality", fontsize=14, pad=15)

    # Force the Y-axis to only show integer ticks (you can't have half an error count)
    ax.yaxis.set_major_locator(mtick.MaxNLocator(integer=True))

    # Clean up the legend title
    ax.legend(title="Feedback Modality")

    plt.tight_layout()
    plt.show()


def amount_of_err_p_val_df(df):
    v_deg_0 = df[df['feedback_modality'] == 'visual']['deg_err_0']
    v_deg_1 = df[df['feedback_modality'] == 'visual']['deg_err_1']
    v_deg_2 = df[df['feedback_modality'] == 'visual']['deg_err_2']
    v_deg_3 = df[df['feedback_modality'] == 'visual']['deg_err_3']
    v_deg_4 = df[df['feedback_modality'] == 'visual']['deg_err_4']

    a_deg_0 = df[df['feedback_modality'] == 'audio']['deg_err_0']
    a_deg_1 = df[df['feedback_modality'] == 'audio']['deg_err_1']
    a_deg_2 = df[df['feedback_modality'] == 'audio']['deg_err_2']
    a_deg_3 = df[df['feedback_modality'] == 'audio']['deg_err_3']
    a_deg_4 = df[df['feedback_modality'] == 'audio']['deg_err_4']

    h_deg_0 = df[df['feedback_modality'] == 'haptic']['deg_err_0']
    h_deg_1 = df[df['feedback_modality'] == 'haptic']['deg_err_1']
    h_deg_2 = df[df['feedback_modality'] == 'haptic']['deg_err_2']
    h_deg_3 = df[df['feedback_modality'] == 'haptic']['deg_err_3']
    h_deg_4 = df[df['feedback_modality'] == 'haptic']['deg_err_4']

    v_lvl_0 = df[df['feedback_modality'] == 'visual']['lvl_err_0']
    v_lvl_1 = df[df['feedback_modality'] == 'visual']['lvl_err_1']
    v_lvl_2 = df[df['feedback_modality'] == 'visual']['lvl_err_2']

    a_lvl_0 = df[df['feedback_modality'] == 'audio']['lvl_err_0']
    a_lvl_1 = df[df['feedback_modality'] == 'audio']['lvl_err_1']
    a_lvl_2 = df[df['feedback_modality'] == 'audio']['lvl_err_2']

    h_lvl_0 = df[df['feedback_modality'] == 'haptic']['lvl_err_0']
    h_lvl_1 = df[df['feedback_modality'] == 'haptic']['lvl_err_1']
    h_lvl_2 = df[df['feedback_modality'] == 'haptic']['lvl_err_2']

    a_h_deg_1_p_val = get_pairwise_p_value(a_deg_1, h_deg_1)
    a_h_deg_2_p_val = get_pairwise_p_value(a_deg_2, h_deg_2)

    a_h_lvl_1_p_val = get_pairwise_p_value(a_lvl_1, h_lvl_1)

    pass


def plot_error_boxplots(error_distribution):
    # Safety check
    if error_distribution is None or error_distribution.empty:
        print("No error distribution data available to plot.")
        return

    sns.set_theme(style="whitegrid")

    # --- Select columns (exclude *_0) ---
    deg_cols = [col for col in error_distribution.columns if col.startswith('deg_err_') and col != 'deg_err_0']
    lvl_cols = [col for col in error_distribution.columns if col.startswith('lvl_err_') and col != 'lvl_err_0']
    all_cols = deg_cols + lvl_cols

    # --- Reshape data to "long" format for Seaborn ---
    melted_df = error_distribution.melt(
        id_vars=['subject_id', 'feedback_modality'],
        value_vars=all_cols,
        var_name='error_type',
        value_name='count'
    )

    # Clean up the X-axis labels (e.g., 'deg_err_1' -> 'Degree Err 1')
    label_mapping = {
        col: col.replace('deg_err_', 'Degree Err ').replace('lvl_err_', 'Level Err ')
        for col in all_cols
    }
    melted_df['error_type'] = melted_df['error_type'].map(label_mapping)

    # Enforce consistent order across all your visualizations
    modality_order = ['audio', 'haptic', 'visual']

    # --- Create the plot ---
    fig, ax = plt.subplots(figsize=(12, 6))

    # Boxplot with enforced hue order
    sns.boxplot(
        data=melted_df,
        x='error_type',
        y='count',
        hue='feedback_modality',
        hue_order=modality_order,
        palette="Set2",
        ax=ax
    )

    ax.set_xlabel("Error Type and Magnitude")
    ax.set_ylabel("Error Count (per subject)")
    ax.set_title("Distribution of Errors by Modality Across Subjects", fontsize=14, pad=15)

    # Force the Y-axis to only show integer ticks
    ax.yaxis.set_major_locator(mtick.MaxNLocator(integer=True))

    # Rotate X-axis labels to prevent overlap
    plt.xticks(rotation=45)

    # Move the legend outside the plot, so it doesn't overlap the boxes
    ax.legend(title='Modality', bbox_to_anchor=(1.05, 1), loc='upper left')

    plt.tight_layout()
    plt.show()


def plot_weighted_error_means(error_results):
    # Safety check: Prevent crashing if data is missing
    if error_results is None or error_results.empty:
        print("No overall error results available to plot.")
        return

    sns.set_theme(style="whitegrid")

    # --- Reshape data to "long" format ---
    melted_means = error_results.melt(
        id_vars='feedback_modality',
        value_vars=['weighted_mean_deg_err', 'weighted_mean_lvl_err'],
        var_name='error_type',
        value_name='weighted_mean'
    )

    # Clean up the error type names so the legend looks professional
    melted_means['error_type'] = melted_means['error_type'].map({
        'weighted_mean_deg_err': 'Degree Error',
        'weighted_mean_lvl_err': 'Level Error'
    })

    # Enforce consistent order across all your visualizations
    modality_order = ['audio', 'haptic', 'visual']

    # --- Create the plot ---
    fig, ax = plt.subplots(figsize=(10, 6))

    # Seaborn automatically groups the bars side-by-side using 'hue'
    sns.barplot(
        data=melted_means,
        x='feedback_modality',
        y='weighted_mean',
        hue='error_type',
        order=modality_order, # Locks the X-axis to your standard order
        palette='Set2',
        edgecolor='black',    # Adds a crisp border to the bars
        linewidth=0.5,
        ax=ax
    )

    # --- Labels and Formatting ---
    ax.set_xlabel("Feedback Modality")
    ax.set_ylabel("Weighted Mean Error Magnitude")
    ax.set_title("Weighted Mean Degree and Level Errors by Modality", fontsize=14, pad=15)

    # Place the legend neatly outside the plot so it doesn't cover the bars
    ax.legend(title="Error Metric", bbox_to_anchor=(1.05, 1), loc='upper left')

    plt.tight_layout()
    plt.show()



def plot_answer_duration(subjects_data_trials):
    all_durations = []

    # Iterate through the dictionary
    for subject_name, df in subjects_data_trials.items():
        if df is None or df.empty:
            continue

        df = df.copy()

        # Capture the original row index as the trial number (1-based index)
        # If your data already has a specific 'trial' column, you can replace this line with df['trial']
        df['trial_number'] = df.index + 1

        # Filter out missed/invalid trials where voice_start is 0
        df = df[df['voice_start'] != 0]

        if df.empty:
            continue

        # Calculate the duration of the answer
        df['answer_duration'] = df['voice_end'] - df['voice_start']
        df['subject_id'] = subject_name

        # Keep the new trial_number column when appending
        all_durations.append(df[['subject_id', 'trial_number', 'feedback_modality', 'answer_duration']])

    # Safety check
    if not all_durations:
        print("No valid duration data found after filtering.")
        return

    # Combine everything into a single DataFrame
    combined_df = pd.concat(all_durations, ignore_index=True)

    # =========================================================
    # --- Print trials taking longer than 5 seconds ---
    # =========================================================
    long_answers = combined_df[combined_df['answer_duration'] > 9]

    if not long_answers.empty:
        print(f"\n--- Alert: Found {len(long_answers)} trial(s) exceeding 5 seconds ---")
        for _, row in long_answers.iterrows():
            # Added Trial Number to the print statement
            print(
                f"Subject: {row['subject_id']:<12} | Trial: {row['trial_number']:<4} | Modality: {row['feedback_modality']:<8} | Duration: {row['answer_duration']:.2f}s")
        print("-" * 75 + "\n")

    # =========================================================
    # --- Plotting ---
    # =========================================================
    sns.set_theme(style="whitegrid")
    modality_order = ['audio', 'haptic', 'visual']

    fig, ax = plt.subplots(figsize=(5, 5))

    # Boxplot using Set2 palette
    sns.boxplot(
        data=combined_df,
        x='feedback_modality',
        y='answer_duration',
        order=modality_order,
        palette="Set2",
        ax=ax,
        showfliers=False
    )

    # Labels and Formatting
    ax.set_xlabel("Feedback Modality")
    ax.set_ylabel("Answer Duration (Seconds)")
    ax.set_title("Distribution of Answer Durations by Modality", fontsize=14, pad=15)

    plt.tight_layout()
    plt.show()


def get_duration_p_value(subjects_data_trials):
    audio_durations = []
    haptic_durations = []

    # Iterate through the dictionary to extract durations
    for subject_name, df in subjects_data_trials.items():

        df = df.copy()

        df = df[df['voice_start'] != 0]

        df['answer_duration'] = df['voice_end'] - df['voice_start']

        audio_vals = df[df['feedback_modality'] == 'audio']['answer_duration'].tolist()
        haptic_vals = df[df['feedback_modality'] == 'haptic']['answer_duration'].tolist()

        audio_durations.extend(audio_vals)
        haptic_durations.extend(haptic_vals)


    # Calculate and return the p-value using your custom function
    p_val = get_pairwise_p_value(audio_durations, haptic_durations)

    return p_val


def plot_reaction_time(subjects_data_trials):
    all_reaction_times = []

    # Iterate through the dictionary
    for subject_name, df in subjects_data_trials.items():
        if df is None or df.empty:
            continue

        df = df.copy()

        # Capture the original row index as the trial number (1-based index)
        df['trial_number'] = df.index + 1

        # Filter out missed/invalid trials where voice_start is 0
        df = df[df['voice_start'] != 0]

        if df.empty:
            continue

        # Calculate Reaction Time: Voice Start minus Cue Presentation (Relative Timestamp)
        df['reaction_time'] = df['voice_start'] - df['relative_timestamp']

        df['subject_id'] = subject_name

        # Keep the necessary columns
        all_reaction_times.append(df[['subject_id', 'trial_number', 'feedback_modality', 'reaction_time']])

    # Safety check
    if not all_reaction_times:
        print("No valid reaction time data found after filtering.")
        return

    # Combine everything into a single DataFrame
    combined_df = pd.concat(all_reaction_times, ignore_index=True)

    # =========================================================
    # --- Print trials with unusually long reaction times ---
    # =========================================================
    # You can adjust this 5-second threshold depending on what
    # is considered "normal" for your specific experimental cue
    long_reactions = combined_df[combined_df['reaction_time'] > 9.0]

    if not long_reactions.empty:
        print(f"\n--- Alert: Found {len(long_reactions)} trial(s) with reaction time > 5 seconds ---")
        for _, row in long_reactions.iterrows():
            print(
                f"Subject: {row['subject_id']:<12} | Trial: {row['trial_number']:<4} | Modality: {row['feedback_modality']:<8} | Reaction Time: {row['reaction_time']:.2f}s")
        print("-" * 75 + "\n")

    early = combined_df[combined_df['reaction_time'] < 0]

    if not early.empty:
        print(f"\n--- Alert: Found {len(early)} Audio trial(s) with reaction time < -2.3 seconds ---")
        for _, row in early.iterrows():
            print(
                f"Subject: {row['subject_id']:<12} | Trial: {row['trial_number']:<4} | Reaction Time: {row['reaction_time']:.2f}s")
        print("-" * 75 + "\n")
    # =========================================================
    # --- Plotting ---
    # =========================================================
    sns.set_theme(style="whitegrid")
    modality_order = ['audio', 'haptic', 'visual']

    fig, ax = plt.subplots(figsize=(5, 5))

    # Boxplot using Set2 palette (no scattered data points per your request)
    sns.boxplot(
        data=combined_df,
        x='feedback_modality',
        y='reaction_time',
        order=modality_order,
        palette="Set2",
        ax=ax,
        showfliers=False
    )

    # Labels and Formatting
    ax.set_xlabel("Feedback Modality")

    # Assuming your timestamps are in seconds. Change to milliseconds if needed.
    ax.set_ylabel("Reaction Time (Seconds)")
    ax.set_title("Distribution of Reaction Times by Modality", fontsize=14, pad=15)

    plt.tight_layout()
    plt.show()


def get_reaction_time_p_value(subjects_data_trials):
    audio_rts = []
    haptic_rts = []

    # Iterate through the dictionary to extract reaction times
    for subject_name, df in subjects_data_trials.items():
        if df is None or df.empty:
            continue

        df = df.copy()

        # Filter out missed/invalid trials where voice_start is 0
        df = df[df['voice_start'] != 0]

        if df.empty:
            continue

        # Calculate Reaction Time: Voice Start minus Cue Presentation
        df['reaction_time'] = df['voice_start'] - df['relative_timestamp']

        # Extract values for audio and haptic
        audio_vals = df[df['feedback_modality'] == 'audio']['reaction_time'].tolist()
        haptic_vals = df[df['feedback_modality'] == 'haptic']['reaction_time'].tolist()

        audio_rts.extend(audio_vals)
        haptic_rts.extend(haptic_vals)

    # Safety check to ensure we have data for both modalities
    if not audio_rts or not haptic_rts:
        print("Not enough valid reaction time data to compare audio and haptic.")
        return None

    # Calculate and return the p-value using your custom function
    p_val = get_pairwise_p_value(audio_rts, haptic_rts)

    return p_val


def apply_audio_delays(subjects_data_trials, delays_df):
    shifted_data = {}

    # Clean whitespace from subject names to ensure perfect matching
    delays_df['Subject'] = delays_df['Subject'].astype(str).str.strip()

    for subject_name, df in subjects_data_trials.items():
        if df is None or df.empty:
            shifted_data[subject_name] = df
            continue

        df = df.copy()

        # Ensure trial_number exists for phase splitting
        if 'trial_number' not in df.columns:
            df['trial_number'] = df.index + 1

        # Find the delays for this specific subject
        delay_row = delays_df[delays_df['Subject'] == str(subject_name).strip()]

        if not delay_row.empty:
            p1_delay = delay_row['p1'].values[0]
            p2_delay = delay_row['p2'].values[0]
            p3_delay = delay_row['p3'].values[0]

            # CRITICAL: Only shift valid trials so 0s don't become valid numbers
            valid = df['voice_start'] != 0

            # Phase 1: trial_number < 73
            m1 = (df['trial_number'] < 73) & valid
            df.loc[m1, 'voice_start'] += p1_delay
            df.loc[m1, 'voice_end'] += p1_delay

            # Phase 2: 73 <= trial_number < 145
            m2 = (df['trial_number'] >= 73) & (df['trial_number'] < 145) & valid
            df.loc[m2, 'voice_start'] += p2_delay
            df.loc[m2, 'voice_end'] += p2_delay

            # Phase 3: trial_number >= 145
            m3 = (df['trial_number'] >= 145) & valid
            df.loc[m3, 'voice_start'] += p3_delay
            df.loc[m3, 'voice_end'] += p3_delay

        shifted_data[subject_name] = df

    return shifted_data


def plot_error_collision_tradeoff(subjects_data_trials, subjects_data_full):
    stats_list = []

    for subject_name, df in subjects_data_trials.items():
        # Skip empty dataframes if any
        if df is None or df.empty:
            continue

        # 1. Filter out trials where perceived values are -1 (should not be counted)
        df_filtered = df[(df['degree_perceived'] != -1) & (df['level_perceived'] != -1)]

        # 2. Count errors (where actual degree/level does not match perceived degree/level)
        # Note: perceived values of 0 (missed) naturally count as errors here
        errors = ((df_filtered['degree'] != df_filtered['degree_perceived']) |
                  (df_filtered['level'] != df_filtered['level_perceived'])).sum()

        # 3. Get the last recorded number of collisions for the subject
        last_collisions = df['number_of_collision'].iloc[-1]
        # subjcet_df_full = subjects_data_full[subject_name]
        # last_collisions = subjcet_df_full['number_of_collision'].iloc[-1]
        # Append the metrics for this subject
        stats_list.append({
            'Subject': subject_name,
            'Total Errors': errors,
            'Total Collisions': last_collisions
        })

    # Convert summary to a DataFrame
    df_summary = pd.DataFrame(stats_list)

    if df_summary.empty:
        print("No valid subject data available to plot.")
        return

    # 4. Plot the Scatter Plot with a Regression Line
    plt.figure(figsize=(8, 6))

    sns.regplot(
        data=df_summary,
        x='Total Errors',
        y='Total Collisions',
        scatter_kws={'s': 60, 'alpha': 0.8, 'color': '#1f77b4'},  # Customize dots
        line_kws={'color': '#d62728', 'linewidth': 2}  # Customize regression line
    )

    # 5. Labels and Layout
    plt.title('Dual-Task Trade-off: Perception Errors vs. Total Collisions', fontsize=14)
    plt.xlabel('Total Errors (Degree or Level Misperceptions)', fontsize=12)
    plt.ylabel('Total Collisions (Final Count)', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.show()


def plot_misses_collision_tradeoff(subjects_data_trials):
    stats_list = []

    for subject_name, df in subjects_data_trials.items():
        # Skip empty dataframes if any
        if df is None or df.empty:
            continue

        # 1. Filter out trials where perceived values are -1 (invalid/should not be counted)
        df_filtered = df[(df['degree_perceived'] != -1) & (df['level_perceived'] != -1)]

        # 2. Count ONLY the "misses" (where perceived value is exactly 0)
        misses = ((df_filtered['degree_perceived'] == 0) |
                  (df_filtered['level_perceived'] == 0)).sum()

        # 3. Get the last recorded number of collisions for the subject
        last_collisions = df['number_of_collision'].iloc[-1]

        # Append the metrics for this subject
        stats_list.append({
            'Subject': subject_name,
            'Total Misses': misses,
            'Total Collisions': last_collisions
        })

    # Convert summary to a DataFrame
    df_summary = pd.DataFrame(stats_list)

    if df_summary.empty:
        print("No valid subject data available to plot.")
        return

    # 4. Plot the Scatter Plot with a Regression Line
    plt.figure(figsize=(8, 6))

    sns.regplot(
        data=df_summary,
        x='Total Misses',
        y='Total Collisions',
        scatter_kws={'s': 60, 'alpha': 0.8, 'color': '#2ca02c'},  # Greenish dots to distinguish from the previous plot
        line_kws={'color': '#d62728', 'linewidth': 2}  # Red regression line
    )

    # 5. Labels and Layout
    plt.title('Dual-Task Trade-off: Perception Misses vs. Total Collisions', fontsize=14)
    plt.xlabel('Total Misses (Perceived == 0)', fontsize=12)
    plt.ylabel('Total Collisions (Final Count)', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.show()


def plot_tradeoff_groups_error(subjects_data_trials):
    stats_list = []

    # 1. Process each subject
    for subject_name, df in subjects_data_trials.items():
        if df is None or df.empty:
            continue

        # Filter valid trials
        df_filtered = df[(df['degree_perceived'] != -1) & (df['level_perceived'] != -1)]

        # Calculate errors
        errors = ((df_filtered['degree'] != df_filtered['degree_perceived']) |
                  (df_filtered['level'] != df_filtered['level_perceived'])).sum()

        # Calculate final collisions
        last_collisions = df['number_of_collision'].iloc[-1]

        stats_list.append({
            'Subject': subject_name,
            'Errors': errors,
            'Collisions': last_collisions
        })

    df_summary = pd.DataFrame(stats_list)

    if df_summary.empty:
        print("No valid data available.")
        return

    # 2. Find the mean collisions across all subjects
    mean_collisions = df_summary['Collisions'].mean()
    group1_label = 'Low Collisions (< Mean)'
    group2_label = 'High Collisions (>= Mean)'

    # 3. Categorize subjects into two groups
    df_summary['Group'] = np.where(
        df_summary['Collisions'] < mean_collisions,
        group1_label,
        group2_label
    )

    errors_group1 = df_summary[df_summary['Group'] == group1_label]['Errors']
    errors_group2 = df_summary[df_summary['Group'] == group2_label]['Errors']
    p_val = get_pairwise_p_value(errors_group1, errors_group2)

    # 4. Reshape data (melt) so seaborn can plot 4 distinct bars (2 groups x 2 metrics)
    df_melted = df_summary.melt(
        id_vars=['Subject', 'Group'],
        value_vars=['Collisions', 'Errors'],
        var_name='Metric',
        value_name='Count'
    )

    # 5. Create the grouped bar chart
    plt.figure(figsize=(10, 6))

    # Seaborn barplot automatically computes the average for the group
    # and adds confidence interval error bars.
    sns.barplot(
        data=df_melted,
        x='Group',
        y='Count',
        hue='Metric',
        palette='Set2',
        capsize=0.1  # Adds the "T" caps to the confidence bounds
    )

    # 6. Customize aesthetics
    plt.title('Dual-Task Trade-off: Performance by Collision Groups', fontsize=14)
    plt.xlabel(f'Subject Group (Mean Collisions = {mean_collisions:.1f})', fontsize=12)
    plt.ylabel('Average Count', fontsize=12)
    plt.legend(title='Metric', bbox_to_anchor=(1.05, 1), loc='upper left')

    plt.tight_layout()
    plt.show()


def plot_tradeoff_groups_misses(subjects_data_trials):
    stats_list = []

    # 1. Process each subject
    for subject_name, df in subjects_data_trials.items():
        if df is None or df.empty:
            continue

        # Filter valid trials (ignore -1)
        df_filtered = df[(df['degree_perceived'] != -1) & (df['level_perceived'] != -1)]

        # Calculate Misses (where degree or level is exactly 0)
        misses = ((df_filtered['degree_perceived'] == 0) |
                  (df_filtered['level_perceived'] == 0)).sum()

        # Calculate final collisions
        last_collisions = df['number_of_collision'].iloc[-1]

        stats_list.append({
            'Subject': subject_name,
            'Misses': misses,
            'Collisions': last_collisions
        })

    df_summary = pd.DataFrame(stats_list)

    if df_summary.empty:
        print("No valid data available.")
        return

    # 2. Find the mean collisions across all subjects
    mean_collisions = df_summary['Collisions'].mean()
    group1_label = 'Low Collisions (< Mean)'
    group2_label = 'High Collisions (>= Mean)'

    # 3. Categorize subjects into two groups
    df_summary['Group'] = np.where(
        df_summary['Collisions'] < mean_collisions,
        group1_label,
        group2_label
    )

    misses_group1 = df_summary[df_summary['Group'] == group1_label]['Misses']
    misses_group2 = df_summary[df_summary['Group'] == group2_label]['Misses']
    p_val = get_pairwise_p_value(misses_group1, misses_group2)

    # 4. Reshape data (melt) to plot 4 bars (2 groups x 2 metrics: Collisions and Misses)
    df_melted = df_summary.melt(
        id_vars=['Subject', 'Group'],
        value_vars=['Collisions', 'Misses'],  # Changed 'Errors' to 'Misses'
        var_name='Metric',
        value_name='Count'
    )

    # 5. Create the grouped bar chart
    plt.figure(figsize=(10, 6))

    sns.barplot(
        data=df_melted,
        x='Group',
        y='Count',
        hue='Metric',
        palette='Set2',
        capsize=0.1  # Adds the "T" caps to the confidence bounds
    )

    # 6. Customize aesthetics
    plt.title('Dual-Task Trade-off: Performance (Misses) by Collision Groups', fontsize=14)
    plt.xlabel(f'Subject Group (Mean Collisions = {mean_collisions:.1f})', fontsize=12)
    plt.ylabel('Average Count', fontsize=12)
    plt.legend(title='Metric', bbox_to_anchor=(1.05, 1), loc='upper left')

    plt.tight_layout()
    plt.show()


def plot_deg_lvl_position_misses_boxplot(subjects_data_trials, fb_mod):
    records = []

    # 1. Iterate through every subject
    for subject_name, df in subjects_data_trials.items():
        if df is None or df.empty:
            continue

        # 2. Filter for purely visual feedback and exclude invalid (-1) responses
        df_vis = df[(df['feedback_modality'] == fb_mod) &
                    (df['degree_perceived'] != -1) &
                    (df['level_perceived'] != -1)].copy()

        # 3. Create a boolean mask for misses (0 in degree or level)
        df_vis['is_miss'] = (df_vis['degree_perceived'] == 0) | (df_vis['level_perceived'] == 0)
        t = df_vis['is_miss'].sum()
        # 4. Group and sum the misses by degree and level for this specific subject
        deg_misses = df_vis.groupby('degree')['is_miss'].sum().to_dict()
        lvl_misses = df_vis.groupby('level')['is_miss'].sum().to_dict()

        # 5. Store the 8 Degree counts (ensuring 0 is recorded if they had no misses)
        for d in range(1, 9):
            records.append({
                'Subject': subject_name,
                'Type': 'Degree',
                'Factor': f'Deg {d}',
                'Misses': deg_misses.get(d, 0)
            })

        # 6. Store the 3 Level counts
        for l in range(1, 4):
            records.append({
                'Subject': subject_name,
                'Type': 'Level',
                'Factor': f'Lev {l}',
                'Misses': lvl_misses.get(l, 0)
            })

    df_plot = pd.DataFrame(records)

    plt.figure(figsize=(12, 6))

    order = [f'Deg {d}' for d in range(1, 9)] + [f'Lev {l}' for l in range(1, 4)]

    # Generate the 11 Box Plots
    sns.boxplot(
        data=df_plot,
        x='Factor',
        y='Misses',
        hue='Type',
        order=order,
        dodge=False,  # Prevents the boxes from offsetting horizontally
        palette='Paired',  # Uses your preferred palette style
        width=0.6  # Adjust box width for clarity
    )

    # 8. Customize Aesthetics
    plt.title(f'Distribution of {fb_mod} Misses across Degrees (1-8) and Levels (1-3)', fontsize=14)
    plt.xlabel('Spatial Factors (Degrees & Levels)', fontsize=12)
    plt.ylabel(f'Number of {fb_mod} Misses per Subject', fontsize=12)
    plt.legend(title='Factor Type', loc='upper right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    plt.tight_layout()
    plt.show()


def print_subjects_with_high_specific_mod_misses(subjects_data_trials, fb_mod):
    print(f"Subjects with >3 {fb_mod} Misses at Degree 3:")
    print("-" * 45)


    for subject_name, df in subjects_data_trials.items():

        df_filtered = df[(df['feedback_modality'] == {fb_mod}) &
                         (df['degree'] == 3) &
                         (df['degree_perceived'] != -1) &
                         (df['level_perceived'] != -1)]

        # 2. Count the misses (where perceived degree or level is 0)
        miss_count = ((df_filtered['degree_perceived'] == 0) |
                      (df_filtered['level_perceived'] == 0)).sum()

        if miss_count > 3:
            print(f"• {subject_name} (Total misses: {miss_count})")
            found_any = True


