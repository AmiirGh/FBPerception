from pathlib import Path
from utils import *


def check_folder_contents(base_dir):
    base_path = Path(base_dir)

    # print(f"Scanning folders in: {base_path.resolve()}\n{'-' * 50}")

    for item in base_path.iterdir():
        # We only care about directories (folders), skip standalone files
        if item.is_dir():
            folder_name = item.name

            # Define the exact paths for the three files we expect to see
            file1_csv = item / f"received_data_{folder_name}.csv"
            file2_xlsx = item / f"{folder_name}_cleaned.xlsx"
            file3_info = item / "subject_info.xlsx"

            # Check which files are missing
            missing_files = []
            if not file1_csv.exists():
                missing_files.append(f"received_data_{folder_name}.csv")
            if not file2_xlsx.exists():
                missing_files.append(f"{folder_name}_cleaned.xlsx")
            if not file3_info.exists():
                missing_files.append("subject_info.xlsx")

            # Print the results for this folder
            if not missing_files:
                print(f"✅ [{folder_name}] - All files present.")
            else:
                print(f"❌ [{folder_name}] - Missing: {', '.join(missing_files)}")


def number_of_subjects_info(base_dir, info='ticklish', value='yes'):
    base_path = Path(base_dir)
    subject_count = 0
    for item in base_path.iterdir():
        if item.is_dir():
            excel_path = item / "subject_info.xlsx"
            if excel_path.exists():
                df = pd.read_excel(excel_path)
                    # Filter rows where Info and Value match (ignoring case and whitespace)
                matching_rows = df[
                    (df['Subject_Info'].astype(str).str.strip().str.lower() == info.lower()) &
                    (df['Value'].astype(str).str.strip().str.lower() == value.lower())
                    ]
                if not matching_rows.empty:
                    subject_count += 1
                    # print(item)
    print(f"Number of subjects with '{info} {value}' is: {subject_count}")


    return subject_count



def plot_tiredness_performance_correlations(demographics, perception_results_all, experiment_logs_all, color_palette):
    """
    Plot:
        1. Tiredness versus total localization accuracy across all modalities.
        2. Tiredness versus final number of collisions.

    Trials with Perceived angle equal to 0 or -1 are excluded from the
    accuracy calculation.

    Returns:
        correlation_df
        participant_results_df
        fig
        axes
    """

    required_demographic_columns = {"Participant ID", "Tiredness"}
    missing_demographic_columns = required_demographic_columns - set(demographics.columns)

    if missing_demographic_columns:
        raise ValueError(f"Missing demographics columns: {sorted(missing_demographic_columns)}")

    participant_names = list(perception_results_all.keys())
    experiment_participant_names = list(experiment_logs_all.keys())
    demographics = demographics.reset_index(drop=True).copy()

    if len(participant_names) != len(demographics):
        raise ValueError(f"The number of perception participants ({len(participant_names)}) does not match the number of demographics rows ({len(demographics)}).")

    if len(experiment_participant_names) != len(demographics):
        raise ValueError(f"The number of experiment-log participants ({len(experiment_participant_names)}) does not match the number of demographics rows ({len(demographics)}).")

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

        participant_id = demographics.loc[participant_index, "Participant ID"]
        tiredness = pd.to_numeric(pd.Series([demographics.loc[participant_index, "Tiredness"]]), errors="coerce").iloc[0]

        participant_records.append({
            "Participant ID": participant_id,
            "Participant folder": participant_name,
            "Tiredness": tiredness,
            "Valid perception trials": number_valid,
            "Accurate perception trials": number_accurate,
            "Total accuracy": total_accuracy,
            "Total accuracy percent": total_accuracy * 100,
            "Final number of collisions": final_collisions,
        })

    participant_results_df = pd.DataFrame(participant_records)

    accuracy_data = participant_results_df[["Tiredness", "Total accuracy percent"]].dropna()
    collision_data = participant_results_df[["Tiredness", "Final number of collisions"]].dropna()

    if len(accuracy_data) >= 2 and accuracy_data["Tiredness"].nunique() > 1 and accuracy_data["Total accuracy percent"].nunique() > 1:
        accuracy_r, accuracy_p = pearsonr(accuracy_data["Tiredness"], accuracy_data["Total accuracy percent"])
    else:
        accuracy_r, accuracy_p = np.nan, np.nan

    if len(collision_data) >= 2 and collision_data["Tiredness"].nunique() > 1 and collision_data["Final number of collisions"].nunique() > 1:
        collision_r, collision_p = pearsonr(collision_data["Tiredness"], collision_data["Final number of collisions"])
    else:
        collision_r, collision_p = np.nan, np.nan

    correlation_df = pd.DataFrame([
        {"Relationship": "Tiredness vs total accuracy", "N": len(accuracy_data), "Pearson r": accuracy_r, "p-value": accuracy_p},
        {"Relationship": "Tiredness vs final collisions", "N": len(collision_data), "Pearson r": collision_r, "p-value": collision_p},
    ])

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    rng = np.random.default_rng(42)

    tiredness_accuracy_x = accuracy_data["Tiredness"].to_numpy(dtype=float)
    accuracy_y = accuracy_data["Total accuracy percent"].to_numpy(dtype=float)
    tiredness_accuracy_jittered = tiredness_accuracy_x + rng.normal(loc=0, scale=0.04, size=len(tiredness_accuracy_x))

    axes[0].scatter(tiredness_accuracy_jittered, accuracy_y, s=65, color=color_palette["visual"], edgecolor="black", linewidth=0.6, alpha=0.85)

    if len(tiredness_accuracy_x) >= 2 and np.unique(tiredness_accuracy_x).size > 1:
        slope, intercept = np.polyfit(tiredness_accuracy_x, accuracy_y, 1)
        line_x = np.linspace(tiredness_accuracy_x.min(), tiredness_accuracy_x.max(), 100)
        axes[0].plot(line_x, slope * line_x + intercept, color=color_palette["visual"], linewidth=2.5)

    accuracy_text = f"N = {len(accuracy_data)}\nPearson r = {accuracy_r:.3f}\np = {accuracy_p:.3f}" if not np.isnan(accuracy_r) else f"N = {len(accuracy_data)}\nPearson r = undefined"

    axes[0].text(0.04, 0.96, accuracy_text, transform=axes[0].transAxes, ha="left", va="top", fontsize=10, bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.8})
    axes[0].set_title("Tiredness and Localization Accuracy")
    axes[0].set_xlabel("Tiredness")
    axes[0].set_ylabel("Total accuracy (%)")
    axes[0].set_xticks(sorted(accuracy_data["Tiredness"].unique()))
    axes[0].set_ylim(-5, 105)
    axes[0].grid(alpha=0.25)

    tiredness_collision_x = collision_data["Tiredness"].to_numpy(dtype=float)
    collision_y = collision_data["Final number of collisions"].to_numpy(dtype=float)
    tiredness_collision_jittered = tiredness_collision_x + rng.normal(loc=0, scale=0.04, size=len(tiredness_collision_x))

    axes[1].scatter(tiredness_collision_jittered, collision_y, s=65, color=color_palette["haptic"], edgecolor="black", linewidth=0.6, alpha=0.85)

    if len(tiredness_collision_x) >= 2 and np.unique(tiredness_collision_x).size > 1:
        slope, intercept = np.polyfit(tiredness_collision_x, collision_y, 1)
        line_x = np.linspace(tiredness_collision_x.min(), tiredness_collision_x.max(), 100)
        axes[1].plot(line_x, slope * line_x + intercept, color=color_palette["haptic"], linewidth=2.5)

    collision_text = f"N = {len(collision_data)}\nPearson r = {collision_r:.3f}\np = {collision_p:.3f}" if not np.isnan(collision_r) else f"N = {len(collision_data)}\nPearson r = undefined"

    axes[1].text(0.04, 0.96, collision_text, transform=axes[1].transAxes, ha="left", va="top", fontsize=10, bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.8})
    axes[1].set_title("Tiredness and Final Collisions")
    axes[1].set_xlabel("Tiredness")
    axes[1].set_ylabel("Final number of collisions")
    axes[1].set_xticks(sorted(collision_data["Tiredness"].unique()))
    axes[1].set_ylim(bottom=0)
    axes[1].grid(alpha=0.25)

    fig.suptitle("Tiredness and Actual Performance", fontsize=15)
    fig.tight_layout()
    plt.show()
    fig.savefig('tiredness_perform_corr.pdf', format='pdf', bbox_inches='tight')
    print("\nPearson correlation results:")
    print(correlation_df.round(3).to_string(index=False))

    return correlation_df, participant_results_df, fig, axes



def plot_ticklishness_haptic_correlations(demographics, perception_results_all, color_palette):
    """
    Plot the relationship between Ticklishness and:
        1. Haptic angle accuracy.
        2. Haptic distance accuracy.

    Ticklishness encoding:
        No  -> 0
        Yes -> 1

    Returns:
        correlation_df
        participant_results_df
        fig
        axes
    """

    required_demographic_columns = {"Participant ID", "Ticklishness"}
    missing_demographic_columns = required_demographic_columns - set(demographics.columns)

    if missing_demographic_columns:
        raise ValueError(f"Missing demographics columns: {sorted(missing_demographic_columns)}")

    participant_names = list(perception_results_all.keys())
    demographics = demographics.reset_index(drop=True).copy()

    if len(participant_names) != len(demographics):
        raise ValueError(f"The number of perception participants ({len(participant_names)}) does not match the number of demographics rows ({len(demographics)}).")

    required_perception_columns = {"Modality", "Angle", "Perceived angle", "Distance", "Perceived distance"}
    numeric_columns = ["Angle", "Perceived angle", "Distance", "Perceived distance"]
    participant_records = []

    for participant_index, participant_name in enumerate(participant_names):
        trials = perception_results_all[participant_name].copy()
        missing_perception_columns = required_perception_columns - set(trials.columns)

        if missing_perception_columns:
            raise ValueError(f"Participant '{participant_name}' is missing perception columns: {sorted(missing_perception_columns)}")

        trials["Modality"] = trials["Modality"].astype(str).str.strip().str.lower()

        for column in numeric_columns:
            trials[column] = pd.to_numeric(trials[column], errors="coerce")

        haptic_trials = trials.loc[trials["Modality"] == "haptic"].copy()

        valid_angle_mask = haptic_trials["Angle"].notna() & haptic_trials["Perceived angle"].notna() & ~haptic_trials["Perceived angle"].isin([0, -1])
        valid_angle_trials = haptic_trials.loc[valid_angle_mask]
        accurate_angle_mask = valid_angle_trials["Angle"].eq(valid_angle_trials["Perceived angle"])

        number_valid_angle = len(valid_angle_trials)
        number_accurate_angle = int(accurate_angle_mask.sum())
        angle_accuracy = number_accurate_angle / number_valid_angle if number_valid_angle > 0 else np.nan

        valid_distance_mask = haptic_trials["Distance"].notna() & haptic_trials["Perceived distance"].notna() & ~haptic_trials["Perceived distance"].isin([0, -1])
        valid_distance_trials = haptic_trials.loc[valid_distance_mask]
        accurate_distance_mask = valid_distance_trials["Distance"].eq(valid_distance_trials["Perceived distance"])

        number_valid_distance = len(valid_distance_trials)
        number_accurate_distance = int(accurate_distance_mask.sum())
        distance_accuracy = number_accurate_distance / number_valid_distance if number_valid_distance > 0 else np.nan

        ticklishness_text = str(demographics.loc[participant_index, "Ticklishness"]).strip().lower()

        if ticklishness_text == "yes":
            ticklishness_binary = 1
        elif ticklishness_text == "no":
            ticklishness_binary = 0
        else:
            ticklishness_binary = np.nan

        participant_records.append({
            "Participant ID": demographics.loc[participant_index, "Participant ID"],
            "Participant folder": participant_name,
            "Ticklishness": demographics.loc[participant_index, "Ticklishness"],
            "Ticklishness binary": ticklishness_binary,
            "Valid haptic angle trials": number_valid_angle,
            "Accurate haptic angle trials": number_accurate_angle,
            "Haptic angle accuracy": angle_accuracy,
            "Haptic angle accuracy percent": angle_accuracy * 100,
            "Valid haptic distance trials": number_valid_distance,
            "Accurate haptic distance trials": number_accurate_distance,
            "Haptic distance accuracy": distance_accuracy,
            "Haptic distance accuracy percent": distance_accuracy * 100,
        })

    participant_results_df = pd.DataFrame(participant_records)

    angle_data = participant_results_df[["Ticklishness binary", "Haptic angle accuracy percent"]].dropna()
    distance_data = participant_results_df[["Ticklishness binary", "Haptic distance accuracy percent"]].dropna()


    distance_no = distance_data.loc[distance_data["Ticklishness binary"] == 0, "Haptic distance accuracy percent"]
    distance_yes = distance_data.loc[distance_data["Ticklishness binary"] == 1, "Haptic distance accuracy percent"]

    if len(distance_no) >= 2 and len(distance_yes) >= 2:
        distance_t, distance_group_p = ttest_ind(distance_yes, distance_no, equal_var=False, nan_policy="omit")
    else:
        distance_t, distance_group_p = np.nan, np.nan


    if len(angle_data) >= 2 and angle_data["Ticklishness binary"].nunique() > 1 and angle_data["Haptic angle accuracy percent"].nunique() > 1:
        angle_r, angle_p = pearsonr(angle_data["Ticklishness binary"], angle_data["Haptic angle accuracy percent"])
    else:
        angle_r, angle_p = np.nan, np.nan

    if len(distance_data) >= 2 and distance_data["Ticklishness binary"].nunique() > 1 and distance_data["Haptic distance accuracy percent"].nunique() > 1:
        distance_r, distance_p = pearsonr(distance_data["Ticklishness binary"], distance_data["Haptic distance accuracy percent"])
    else:
        distance_r, distance_p = np.nan, np.nan

    correlation_df = pd.DataFrame([
        {"Relationship": "Ticklishness vs haptic angle accuracy", "N": len(angle_data), "Pearson r": angle_r, "p-value": angle_p},
        {"Relationship": "Ticklishness vs haptic distance accuracy", "N": len(distance_data), "Pearson r": distance_r, "p-value": distance_p},
    ])

    fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharey=True)
    rng = np.random.default_rng(42)
    haptic_color = color_palette["haptic"]

    ticklishness_angle_x = angle_data["Ticklishness binary"].to_numpy(dtype=float)
    angle_accuracy_y = angle_data["Haptic angle accuracy percent"].to_numpy(dtype=float)
    ticklishness_angle_jittered = ticklishness_angle_x + rng.normal(loc=0, scale=0.035, size=len(ticklishness_angle_x))

    axes[0].scatter(ticklishness_angle_jittered, angle_accuracy_y, s=65, color=haptic_color, edgecolor="black", linewidth=0.6, alpha=0.85)

    if len(ticklishness_angle_x) >= 2 and np.unique(ticklishness_angle_x).size > 1:
        slope, intercept = np.polyfit(ticklishness_angle_x, angle_accuracy_y, 1)
        line_x = np.linspace(0, 1, 100)
        axes[0].plot(line_x, slope * line_x + intercept, color=haptic_color, linewidth=2.5)

    angle_text = f"N = {len(angle_data)}\nPearson r = {angle_r:.3f}\np = {angle_p:.3f}" if not np.isnan(angle_r) else f"N = {len(angle_data)}\nPearson r = undefined"

    axes[0].text(0.04, 0.96, angle_text, transform=axes[0].transAxes, ha="left", va="top", fontsize=10, bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.8})
    axes[0].set_title("Ticklishness and Haptic Angle Accuracy")
    axes[0].set_xlabel("Ticklishness")
    axes[0].set_ylabel("Haptic accuracy (%)")
    axes[0].set_xticks([0, 1])
    axes[0].set_xticklabels(["No", "Yes"])
    axes[0].set_xlim(-0.25, 1.25)
    axes[0].set_ylim(-5, 105)
    axes[0].grid(alpha=0.25)

    ticklishness_distance_x = distance_data["Ticklishness binary"].to_numpy(dtype=float)
    distance_accuracy_y = distance_data["Haptic distance accuracy percent"].to_numpy(dtype=float)
    ticklishness_distance_jittered = ticklishness_distance_x + rng.normal(loc=0, scale=0.035, size=len(ticklishness_distance_x))

    axes[1].scatter(ticklishness_distance_jittered, distance_accuracy_y, s=65, color=haptic_color, edgecolor="black", linewidth=0.6, alpha=0.85)

    if len(ticklishness_distance_x) >= 2 and np.unique(ticklishness_distance_x).size > 1:
        slope, intercept = np.polyfit(ticklishness_distance_x, distance_accuracy_y, 1)
        line_x = np.linspace(0, 1, 100)
        axes[1].plot(line_x, slope * line_x + intercept, color=haptic_color, linewidth=2.5)

    distance_text = f"N = {len(distance_data)}\nPearson r = {distance_r:.3f}\np = {distance_p:.3f}" if not np.isnan(distance_r) else f"N = {len(distance_data)}\nPearson r = undefined"

    axes[1].text(0.04, 0.96, distance_text, transform=axes[1].transAxes, ha="left", va="top", fontsize=10, bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.8})
    axes[1].set_title("Ticklishness and Haptic Distance Accuracy")
    axes[1].set_xlabel("Ticklishness")
    axes[1].set_xticks([0, 1])
    axes[1].set_xticklabels(["No", "Yes"])
    axes[1].set_xlim(-0.25, 1.25)
    axes[1].set_ylim(-5, 105)
    axes[1].grid(alpha=0.25)

    fig.suptitle("Ticklishness and Haptic Localization Accuracy", fontsize=15)
    fig.tight_layout()
    fig.savefig('Ticklishness_haptic_corr.pdf', format='pdf', bbox_inches='tight')
    plt.show()

    print("\nPoint-biserial/Pearson correlation results:")
    print(correlation_df.round(3).to_string(index=False))

    return correlation_df, participant_results_df, fig, axes


def count_gender_by_phase_sequence(demographics):
    required_columns = {"Gender", "Phase difficulty level sequence"}
    missing_columns = required_columns - set(demographics.columns)

    if missing_columns:
        raise ValueError(f"Missing demographics columns: {sorted(missing_columns)}")

    data = demographics[["Gender", "Phase difficulty level sequence"]].copy()
    data["Gender"] = data["Gender"].astype(str).str.strip().str.lower()
    data["Phase difficulty level sequence"] = data["Phase difficulty level sequence"].astype(str).str.strip()

    data = data.loc[data["Gender"].isin(["male", "female"])]
    data = data.loc[~data["Phase difficulty level sequence"].isin(["", "nan"])]

    gender_counts = pd.crosstab(data["Phase difficulty level sequence"], data["Gender"])

    gender_counts = gender_counts.reindex(columns=["male", "female"], fill_value=0)
    gender_counts = gender_counts.rename(columns={"male": "Male", "female": "Female"}).reset_index()
    gender_counts["Total"] = gender_counts["Male"] + gender_counts["Female"]

    print("\nGender counts by phase difficulty level sequence:")
    print(gender_counts.to_string(index=False))

    return gender_counts

