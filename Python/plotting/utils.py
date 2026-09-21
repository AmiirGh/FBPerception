import os, time, warnings
import pandas as pd, numpy as np, seaborn as sns
import matplotlib.pyplot as plt, matplotlib.ticker as mtick, matplotlib.lines as mlines, matplotlib.patches as mpatches
import scipy.stats as stats, scipy.cluster.hierarchy as sch
from matplotlib.patches import Patch
from collections import Counter
from math import pi
from itertools import combinations
from matplotlib.lines import Line2D
from scipy.interpolate import make_interp_spline
from scipy.stats import ttest_rel, shapiro, gamma, skewnorm, spearmanr, pearsonr, ttest_ind, friedmanchisquare, wilcoxon, mannwhitneyu, ranksums
from scipy.stats import ranksums, shapiro, ttest_ind, levene
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import AgglomerativeClustering
from scipy.spatial.distance import pdist, squareform
from statsmodels.multivariate.manova import MANOVA


warnings.filterwarnings("ignore")






def get_perception_results_df(data_path, participants_to_remove=None):
    # Initialize as an empty list if no arguments are passed
    if participants_to_remove is None:
        participants_to_remove = []

    subjects_data_trials = {}

    for folder_name in sorted(os.listdir(data_path)):
        # Skip this participant if they are in the removal list
        if folder_name in participants_to_remove:
            continue

        folder_path = os.path.join(data_path, folder_name)

        if not os.path.isdir(folder_path):
            continue

        csv_path = os.path.join(folder_path, "Perception results.csv")

        # Safely check if the file exists before reading
        if os.path.exists(csv_path):
            trials_data = pd.read_csv(csv_path)
            subjects_data_trials[folder_name] = trials_data

    return subjects_data_trials


def get_experiment_logs_df(data_path, participants_to_remove=None):
    # Initialize as an empty list if no arguments are passed
    if participants_to_remove is None:
        participants_to_remove = []

    subjects_data_full = {}

    for folder_name in sorted(os.listdir(data_path)):
        # Skip this participant if they are in the removal list
        if folder_name in participants_to_remove:
            continue

        folder_path = os.path.join(data_path, folder_name)
        if not os.path.isdir(folder_path):
            continue

        csv_path = os.path.join(folder_path, "Experiment logs.csv")

        # Safely check if the file exists before reading
        if os.path.exists(csv_path):
            trials_data = pd.read_csv(csv_path)
            subjects_data_full[folder_name] = trials_data

    return subjects_data_full



def extract_collision_modality(df, trials_df, start_offset=0.5, duration=0.5):
    """
    Extract collisions in a time window (in seconds) AFTER rising edge,
    ignoring trials where the subject missed (degree_perceived == 0).
    """
    df = df.copy().reset_index(drop=True)

    df["is_dynamic_obstacle_present"] = ~df["Modality"].isin([0, "0"])

    df["dynamic_rise"] = (
            df["is_dynamic_obstacle_present"] &
            ~df["is_dynamic_obstacle_present"].shift(1, fill_value=False)
    )

    df.loc[df["dynamic_rise"], "Modality"] = (
        df["Modality"].shift(-1)
    )

    trials = df[df["dynamic_rise"]].copy()

    collision_results = []

    for idx in trials.index:
        # 1. Identify which trial this is in the continuous data
        current_trial_num = df.loc[idx, "Trial number"]

        # 2. Look up this exact trial in the perception_results_all dataframe
        matching_trial = trials_df[trials_df["Trial number"] == current_trial_num]

        # 3. Check if the trial was missed
        if not matching_trial.empty:
            deg_perceived = matching_trial["Perceived angle"].iloc[0]
            if deg_perceived == 0 or deg_perceived == -1:
                continue
        else:
            # If for some reason the trial isn't in the trials_df, skip it to be safe
            continue

        # --- Proceed with time-based collision calculation ---
        t_cue = df.loc[idx, "Timestamp"]
        t_start = t_cue + start_offset
        t_end = t_start + duration

        # Find the first row where Timestamp is >= t_start
        start_mask = df["Timestamp"] >= t_start
        if not start_mask.any():
            continue  # The recording ends before the start window is reached
        start_idx = start_mask.idxmax() # idxmax() returns the first index where the mask is True

        # Find the first row where Timestamp is >= t_end
        end_mask = df["Timestamp"] >= t_end
        if not end_mask.any():
            end_idx = df.index[-1] # Use the very last row if the recording cuts off early
        else:
            end_idx = end_mask.idxmax()

        start_collision = df.loc[start_idx, "Number of collision"]
        end_collision = df.loc[end_idx, "Number of collision"]

        collisions_in_window = end_collision - start_collision

        collision_results.append({
            "Modality": df.loc[idx, "Modality"],
            "collisions": collisions_in_window
        })

    return pd.DataFrame(collision_results)


def is_normal(dist_values):
    statistic, p_value = stats.shapiro(dist_values)
    return True if p_value > 0.05 else False


def get_p_val_miss_counts(df):
    v_a_miss_counts_p_val = get_pairwise_p_value(df[df['Modality'] == 'visual']['count'],
                                                 df[df['Modality'] == 'auditory']['count'])
    v_h_miss_counts_p_val = get_pairwise_p_value(df[df['Modality'] == 'visual']['count'],
                                                 df[df['Modality'] == 'haptic']['count'])
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






def get_p_val_accuracy(accuracy_degree_all, accuracy_level_all, accuracy_full_all):
    v_deg = accuracy_degree_all[accuracy_degree_all['Modality'] == 'visual']['accuracy_degree']
    v_lvl = accuracy_level_all[accuracy_level_all['Modality'] == 'visual']['accuracy_level']
    v_full = accuracy_full_all[accuracy_full_all['Modality'] == 'visual']['accuracy_full']

    a_deg = accuracy_degree_all[accuracy_degree_all['Modality'] == 'auditory']['accuracy_degree']
    a_lvl = accuracy_level_all[accuracy_level_all['Modality'] == 'auditory']['accuracy_level']
    a_full = accuracy_full_all[accuracy_full_all['Modality'] == 'auditory']['accuracy_full']

    h_deg = accuracy_degree_all[accuracy_degree_all['Modality'] == 'haptic']['accuracy_degree']
    h_lvl = accuracy_level_all[accuracy_level_all['Modality'] == 'haptic']['accuracy_level']
    h_full = accuracy_full_all[accuracy_full_all['Modality'] == 'haptic']['accuracy_full']

    a_full_h_full_p_val = get_pairwise_p_value(a_full, h_full)
    a_deg_h_deg_p_val = get_pairwise_p_value(a_deg, h_deg)
    a_lvl_h_lvl_p_val = get_pairwise_p_value(a_lvl, h_lvl)

    return v_deg
















def calc_no_collisions_by_fbmod_for_time_window(experiment_logs_all, perception_results_all, start_sec, end_sec):
    all_results = []

    for subject_name, df in experiment_logs_all.items():
        # Safety check: Ensure we have the trial data for this subject
        if subject_name not in perception_results_all or perception_results_all[subject_name] is None:
            continue

        trials_df = perception_results_all[subject_name]

        start_offset = int(start_sec * 12)
        end_offset = int(end_sec * 12)

        # Pass the trials_df down to the extraction function
        results = extract_collision_modality(df, trials_df, start_offset=start_offset, end_offset=end_offset)

        # If the results are empty (e.g., all trials were missed), skip
        if results.empty:
            continue

        summary = (results.groupby("Modality")["collisions"].sum().reset_index())
        summary["subject"] = subject_name
        all_results.append(summary)

    if not all_results:
        return pd.DataFrame()  # Return empty df if nothing matched

    all_summary = pd.concat(all_results, ignore_index=True)
    return all_summary



def _fit_gamma_collision_distribution(observed_counts, window_starts, window_ends, n_bootstrap=1000, random_state=42):
    observed_counts = np.asarray(observed_counts, dtype=float)
    observed_counts = np.clip(np.rint(observed_counts), 0, None).astype(int)

    window_starts = np.asarray(window_starts, dtype=float)
    window_ends = np.asarray(window_ends, dtype=float)
    window_midpoints = (window_starts + window_ends) / 2

    total_collisions = int(observed_counts.sum())

    if total_collisions < 4 or np.count_nonzero(observed_counts) < 2:
        return {"shape": np.nan, "location": np.nan, "scale": np.nan, "gof_statistic": np.nan, "p-value": np.nan, "expected_counts": np.full(len(observed_counts), np.nan)}

    collision_times = np.repeat(window_midpoints, observed_counts)

    try:
        # gamma.fit returns shape (a), loc, and scale
        shape_a, location, scale = gamma.fit(collision_times)
    except Exception:
        return {"shape": np.nan, "location": np.nan, "scale": np.nan, "gof_statistic": np.nan, "p-value": np.nan, "expected_counts": np.full(len(observed_counts), np.nan)}

    if not np.isfinite(scale) or scale <= 0:
        return {"shape": np.nan, "location": np.nan, "scale": np.nan, "gof_statistic": np.nan, "p-value": np.nan, "expected_counts": np.full(len(observed_counts), np.nan)}

    probabilities = gamma.cdf(window_ends, shape_a, loc=location, scale=scale) - gamma.cdf(window_starts, shape_a, loc=location, scale=scale)
    probabilities = np.clip(probabilities, 1e-12, None)
    probabilities = probabilities / probabilities.sum()

    expected_counts = total_collisions * probabilities
    observed_statistic = np.sum((observed_counts - expected_counts) ** 2 / expected_counts)

    rng = np.random.default_rng(random_state)
    bootstrap_statistics = []

    for _ in range(n_bootstrap):
        simulated_counts = rng.multinomial(total_collisions, probabilities)

        if np.count_nonzero(simulated_counts) < 2:
            continue

        simulated_times = np.repeat(window_midpoints, simulated_counts)

        try:
            simulated_shape, simulated_location, simulated_scale = gamma.fit(simulated_times)

            if not np.isfinite(simulated_scale) or simulated_scale <= 0:
                continue

            simulated_probabilities = gamma.cdf(window_ends, simulated_shape, loc=simulated_location, scale=simulated_scale) - gamma.cdf(window_starts, simulated_shape, loc=simulated_location, scale=simulated_scale)
            simulated_probabilities = np.clip(simulated_probabilities, 1e-12, None)
            simulated_probabilities = simulated_probabilities / simulated_probabilities.sum()

            simulated_expected = total_collisions * simulated_probabilities
            simulated_statistic = np.sum((simulated_counts - simulated_expected) ** 2 / simulated_expected)
            bootstrap_statistics.append(simulated_statistic)

        except Exception:
            continue

    if len(bootstrap_statistics) > 0:
        bootstrap_statistics = np.asarray(bootstrap_statistics)
        p_value = (np.sum(bootstrap_statistics >= observed_statistic) + 1) / (len(bootstrap_statistics) + 1)
    else:
        p_value = np.nan

    return {
        "shape": shape_a,
        "location": location,
        "scale": scale,
        "gof_statistic": observed_statistic,
        "p-value": p_value,
        "expected_counts": expected_counts,
    }


def plot_multiple_collision_time_windows(step, experiment_logs_all, perception_results_all, color_palette,
                                         axes=None, n_bootstrap=100):
    """
    Plots collision boxplots across time windows for auditory, haptic and
    visual modalities.

    A Gamma temporal distribution is fitted to the median collisions
    across the time windows for each modality, with dotted lines marking
    the peak of the fitted curve. Subplot titles are removed in favor
    of a color legend.
    """


    windows_list = [[i * step, (i + 1) * step] for i in range(int(6 / step))]

    standalone = axes is None
    window_summaries = []

    for window in windows_list:
        summary_df = calc_no_collisions_by_fbmod_for_time_window(experiment_logs_all, perception_results_all,
                                                                 start_sec=window[0], end_sec=window[1])
        summary_df["Time Window"] = f"{window[0]}-{window[1]}s"
        window_summaries.append(summary_df)

    combined_all_windows = pd.concat(window_summaries, ignore_index=True)
    combined_all_windows["Modality"] = combined_all_windows["Modality"].astype(str).str.strip().str.lower()
    combined_all_windows["collisions"] = pd.to_numeric(combined_all_windows["collisions"], errors="coerce")

    time_order = [f"{window[0]}-{window[1]}s" for window in windows_list]
    window_starts = np.asarray([window[0] for window in windows_list], dtype=float)
    window_ends = np.asarray([window[1] for window in windows_list], dtype=float)
    window_midpoints = (window_starts + window_ends) / 2
    modalities = ["visual", "auditory", "haptic"]

    if standalone:
        fig, axes = plt.subplots(3, 1, figsize=(14, 12), sharex=True, sharey=True)

    axes = np.atleast_1d(axes).flatten()

    if len(axes) != 3:
        raise ValueError(f"'axes' must contain exactly three axes, but {len(axes)} were provided.")

    fit_records = []

    for i, modality in enumerate(modalities):
        ax = axes[i]
        modality_data = combined_all_windows.loc[combined_all_windows["Modality"] == modality].copy()

        sns.boxplot(data=modality_data, x="Time Window", y="collisions", order=time_order,
                    color=color_palette[modality], width=0.4, showfliers=False, boxprops={"alpha": 0.4}, ax=ax)

        # Calculate totals (for the reporting table) and medians (for fitting and plotting)
        observed_totals = modality_data.groupby("Time Window")["collisions"].sum().reindex(time_order,
                                                                                           fill_value=0).to_numpy(
            dtype=float)
        observed_medians = modality_data.groupby("Time Window")["collisions"].median().reindex(time_order).to_numpy(
            dtype=float)



        # Fit the Gamma distribution to the medians
        fit_result = _fit_gamma_collision_distribution(observed_medians, window_starts, window_ends,
                                                       n_bootstrap=n_bootstrap, random_state=42 + i)

        shape = fit_result["shape"]
        location = fit_result["location"]
        scale = fit_result["scale"]
        p_value = fit_result["p-value"]
        expected_medians = fit_result["expected_counts"]

        # ax.scatter(np.arange(len(time_order)), observed_medians, color=color_palette[modality], s=70, edgecolor="black",
        #            linewidth=0.7, zorder=6, label="Observed median")

        # Initialize base fit text
        fit_text = "Gamma fit undefined"
        peak_time_record = np.nan
        peak_val_record = np.nan

        if np.all(np.isfinite([shape, location, scale])) and np.isfinite(expected_medians).sum() >= 2:
            smooth_time = np.linspace(window_starts.min(), window_ends.max(), 400)
            smooth_pdf = gamma.pdf(smooth_time, shape, loc=location, scale=scale)
            midpoint_pdf = gamma.pdf(window_midpoints, shape, loc=location, scale=scale)

            # Scale the PDF amplitude to match the observed medians via least-squares
            valid_scale_mask = np.isfinite(observed_medians) & np.isfinite(midpoint_pdf)

            if valid_scale_mask.sum() >= 2 and np.sum(midpoint_pdf[valid_scale_mask] ** 2) > 0:
                amplitude = np.sum(observed_medians[valid_scale_mask] * midpoint_pdf[valid_scale_mask]) / np.sum(
                    midpoint_pdf[valid_scale_mask] ** 2)
            else:
                amplitude = 1

            smooth_collision_curve = amplitude * smooth_pdf
            smooth_axis_positions = np.interp(smooth_time, window_midpoints, np.arange(len(time_order)))
            ax.plot(smooth_axis_positions, smooth_collision_curve, color=color_palette[modality], linewidth=3, zorder=5,
                    label="Gamma fit")

            ax.scatter(np.arange(len(time_order)), expected_medians, marker="D", s=45, color=color_palette[modality],
                       edgecolor="black", linewidth=0.7, zorder=7, label="Fitted window median")

            # --- PEAK CALCULATION AND DOTTED LINES ---
            peak_idx = np.argmax(smooth_collision_curve)
            peak_y = smooth_collision_curve[peak_idx]
            peak_x_plot = smooth_axis_positions[peak_idx]
            peak_x_time = smooth_time[peak_idx]

            # Get current axis limits to ensure lines draw cleanly to the edges
            xmin, xmax = ax.get_xlim()
            ymin, ymax = ax.get_ylim()

            # Vertical dotted line down to the x-axis
            ax.vlines(x=peak_x_plot, ymin=ymin, ymax=peak_y, color='gray', linestyle=':', linewidth=2, zorder=4)

            # Horizontal dotted line across to the y-axis
            ax.hlines(y=peak_y, xmin=xmin, xmax=peak_x_plot, color='gray', linestyle=':', linewidth=2, zorder=4)

            # Highlight the exact peak point
            ax.scatter(peak_x_plot, peak_y, color=color_palette[modality], marker='o', s=80, edgecolor='black',
                       linewidth=1.2, zorder=8)

            peak_time_record = peak_x_time
            peak_val_record = peak_y
            fit_text = f"Peak Time = {peak_x_time:.2f} s\nPeak Val = {peak_y:.1f}"

        ax.text(0.02, 0.96, fit_text, transform=ax.transAxes, ha="left", va="top", fontsize=12,
                bbox={"facecolor": "white", "edgecolor": "gray", "alpha": 0.85})
        ax.set_ylabel("Collisions", fontsize=14)
        ax.grid(axis="y", linestyle="--", alpha=0.7)

        if i == 2:
            ax.set_xlabel("Time Window (seconds)", fontsize=14)
        else:
            ax.set_xlabel("")

        for ax in axes:
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.spines["left"].set_color("black")
            ax.spines["bottom"].set_color("black")

        fit_records.append({
            "Modality": modality,
            "Total collisions": int(np.nansum(observed_totals)),
            "Gamma shape (a)": shape,
            "Location": location,
            "Scale": scale,
            "GOF p-value": p_value,
            "Peak Time (s)": peak_time_record,
            "Peak Collisions": peak_val_record
        })

    custom_legend_handles = [
        mpatches.Patch(color=color_palette['visual'], label='Visual'),
        mpatches.Patch(color=color_palette['auditory'], label='Auditory'),
        mpatches.Patch(color=color_palette['haptic'], label='Haptic'),
        mlines.Line2D([], [], color='black', linewidth=2, label='Fitted Curve'),
        mlines.Line2D([], [], color='black', marker='s', linestyle='None', markersize=7, label='Fitted Median')
    ]

    # Add it only to the top right of the first subplot
    axes[0].legend(handles=custom_legend_handles, loc="upper right", fontsize=12)

    gamma_fit_df = pd.DataFrame(fit_records)

    print("\nGamma collision-distribution fits:")
    print(gamma_fit_df.round(3).to_string(index=False))

    if standalone:
        # Reset limits strictly to avoid the dotted lines expanding the plot area
        for ax in axes:
            ax.set_xlim(-0.5, len(time_order) - 0.5)

        plt.tight_layout()
        plt.show()

    fig.savefig('gamma_distribution.pdf', format='pdf', bbox_inches='tight')







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
        valid_positions = df["Camera position"].dropna()

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
        x = df["Thumbstick x"].dropna().values
        y = df["Thumbstick y"].dropna().values

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










def plot_all_perceptions(perception_results_all, color_palette, mod1='auditory', mod2='haptic', mod3='visual'):
    modalities = [mod1, mod2, mod3]

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

    def level_to_radius(l):
        return l * 1.4

    color_map = color_palette
    base_scatter_size = 18

    all_subject_dfs = [df for df in perception_results_all.values() if df is not None and not df.empty]
    full_data = pd.concat(all_subject_dfs, ignore_index=True)
    full_data = full_data[full_data["Perceived angle"] > 0]
    max_count = full_data.groupby(["Modality", "Angle", "Distance", "Perceived angle", "Perceived distance"]).size().max()
    print(f"The maximum response count is: {max_count}")



    # ------------------------------------------------------------------
    # Plot
    # ------------------------------------------------------------------
    fig, axes = plt.subplots(9,8, subplot_kw={'projection': 'polar'}, figsize=(28, 32))

    for m_idx, fbmod in enumerate(modalities):
        mod_color = color_map.get(fbmod, 'tab:blue')
        all_data = []

        for subject_name, df in perception_results_all.items():
            if df is None or df.empty:
                continue
            df_mod = df[df["Modality"] == fbmod].copy()
            # remove misses and setup misses
            df_mod = df_mod[df_mod["Perceived angle"] > 0]
            cols = ["Angle", "Distance", "Perceived angle", "Perceived distance"]
            if not df_mod.empty:
                all_data.append(df_mod[cols])

        if len(all_data) == 0:
            continue

        data = pd.concat(all_data, ignore_index=True)

        for l in range(1, 4):
            for d in range(1, 9):
                row_idx = (m_idx * 3) + (l - 1)
                col_idx = d - 1
                ax = axes[row_idx, col_idx]
                subset = data[(data["Angle"] == d) & (data["Distance"] == l)]
                R = level_to_radius(l)

                # ------------------------------------------------------
                # Reference circles
                # ------------------------------------------------------
                theta_full = np.linspace(0, 2 * np.pi, 200)
                ax.plot(theta_full, np.full_like(theta_full, level_to_radius(1)), alpha=0.5, color='black')
                ax.plot(theta_full, np.full_like(theta_full, level_to_radius(2)), alpha=0.5, color='black')
                ax.plot(theta_full, np.full_like(theta_full, level_to_radius(3)), alpha=0.5, color='black')

                # ------------------------------------------------------
                # True stimulus arrow
                # ------------------------------------------------------
                base_width = 0.25
                base_head_width = 0.7
                base_head_length = 0.55
                ax.arrow(degree_to_angle(d),0, 0, R, width=base_width / R, head_width=base_head_width / R,
                    head_length=base_head_length, alpha=0.9, color='red', length_includes_head=True)

                # ------------------------------------------------------
                # Perceived responses
                # ------------------------------------------------------
                if len(subset) > 0:
                    grouped = (subset.groupby(["Perceived angle","Perceived distance"]).size().reset_index(name="count"))
                    angles = grouped["Perceived angle"].apply(degree_to_angle)
                    radii = grouped["Perceived distance"].apply(level_to_radius)
                    sizes = grouped["count"] * base_scatter_size
                    ax.scatter(angles, radii, s=sizes, alpha=0.6, color=mod_color, zorder=3, clip_on=False)

                ax.set_ylim(0, 4.5)
                ax.set_xticks([])
                ax.set_yticks([])
                ax.spines['polar'].set_visible(False)
                ax.set_facecolor('none')

    # ------------------------------------------------------------------
    # Modality color legend
    # ------------------------------------------------------------------
    modality_handles = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor=color_map['auditory'], markersize=40, label='Auditory'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor=color_map['haptic'], markersize=40, label='Haptic'),
        Line2D([0], [0],marker='o',color='w',markerfacecolor=color_map['visual'],markersize=40,label='Visual')]

    modality_legend = fig.legend(handles=modality_handles, loc='upper left', bbox_to_anchor=(0.0, 0.99),
        ncol=3, prop={'family': 'Times New Roman', 'size': 40}, frameon=False, handletextpad=0.4,columnspacing=1.2)
    fig.add_artist(modality_legend)

    # ------------------------------------------------------------------
    # Scatter size legend
    # ------------------------------------------------------------------
    legend_ax = fig.add_axes([0.60, 0.92, 0.38, 0.08])
    legend_ax.axis('off')
    my_font = {'family': 'Times New Roman', 'size': 40}
    legend_ax.text(0.4, 0.6, 'Scale:', ha='left', va='center',
                   fontdict=my_font, transform=legend_ax.transAxes)
    size_values = [10, 70, max_count]
    x_positions = [0.6, 0.75, 0.9]
    for x, v in zip(x_positions, size_values):
        legend_ax.scatter(x, 0.6, s=v * base_scatter_size, color='gray', alpha=0.6,
                          transform=legend_ax.transAxes, clip_on=False)
        legend_ax.text(x, 0.4, f'{v}', ha='center', va='top',
                       fontdict=my_font, transform=legend_ax.transAxes)
    # ------------------------------------------------------------------
    # Layout and save
    # ------------------------------------------------------------------
    plt.tight_layout(rect=[0, 0.01, 1, 0.93])
    plt.savefig('spatial_perception_allmods.pdf', format='pdf')
    plt.show()











def evaluate_outliers_performance(outlier_names, subject_distributions):
    """
    Compares the auditory and haptic performance of specific outlier subjects
    against the rest of the population.
    """
    # 1. Filter for only auditory and haptic modalities
    df_filtered = subject_distributions[
        subject_distributions['Modality'].isin(['auditory', 'haptic'])
    ].copy()

    # 2. Assign subjects to either 'Outliers' or 'Population'
    df_filtered['Group'] = np.where(
        df_filtered['subject_id'].isin(outlier_names),
        'Outliers',
        'Population'
    )

    # 3. Aggregate the error counts for both groups
    # Drop subject_id so we just sum up the error counts per Group and Modality
    group_sums = df_filtered.drop(columns=['subject_id']).groupby(['Group', 'Modality']).sum().reset_index()

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

    results = group_sums[['Group', 'Modality', 'mean_deg_err', 'mean_lvl_err']]

    # 6. Print the Comparison
    print("=" * 60)
    print(" OUTLIERS VS POPULATION PERFORMANCE (auditory & HAPTIC)")
    print("=" * 60)

    for mod in ['auditory', 'haptic']:
        print(f"\n--- {mod.upper()} MODALITY ---")

        # Safely extract values
        try:
            outlier_deg = \
            results[(results['Group'] == 'Outliers') & (results['Modality'] == mod)]['mean_deg_err'].values[0]
            pop_deg = \
            results[(results['Group'] == 'Population') & (results['Modality'] == mod)]['mean_deg_err'].values[
                0]

            outlier_lvl = \
            results[(results['Group'] == 'Outliers') & (results['Modality'] == mod)]['mean_lvl_err'].values[0]
            pop_lvl = \
            results[(results['Group'] == 'Population') & (results['Modality'] == mod)]['mean_lvl_err'].values[
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







def plot_error_boxplots(error_distribution, color_palette):
    """Plots the distribution of angular and radial distance errors across feedback modalities."""

    if error_distribution is None or error_distribution.empty:
        return

    sns.set_theme(style="whitegrid")

    angle_cols = [col for col in error_distribution.columns if col.startswith('Angle_err_') and col != 'Angle_err_0']
    dist_cols = [col for col in error_distribution.columns if col.startswith('Dist_err_') and col != 'Dist_err_0']
    all_cols = angle_cols + dist_cols

    melted_df = error_distribution.melt(
        id_vars=['Participant ID', 'Modality'],
        value_vars=all_cols,
        var_name='error_type',
        value_name='count'
    )

    label_mapping = {
        col: col.replace('Angle_err_', 'Angle error: ').replace('Dist_err_', 'Distance error: ')
        for col in all_cols
    }
    melted_df['error_type'] = melted_df['error_type'].map(label_mapping)

    modality_order = ['visual', 'auditory', 'haptic']

    fig, ax = plt.subplots(figsize=(12, 6))

    sns.boxplot(
        data=melted_df,
        x='error_type',
        y='count',
        hue='Modality',
        hue_order=modality_order,
        palette=color_palette,
        ax=ax
    )

    ax.set_ylabel("Error Count (per subject)")
    # ax.set_title("Distribution of Errors by Modality Across Subjects", fontsize=14, pad=15)

    ax.yaxis.set_major_locator(mtick.MaxNLocator(integer=True))

    plt.xticks(rotation=45)

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
        id_vars='Modality',
        value_vars=['weighted_mean_Angle_err', 'weighted_mean_Dist_err'],
        var_name='error_type',
        value_name='weighted_mean'
    )

    # Clean up the error type names so the legend looks professional
    melted_means['error_type'] = melted_means['error_type'].map({
        'weighted_mean_Angle_err': 'Degree Error',
        'weighted_mean_Dist_err': 'Level Error'
    })

    # Enforce consistent order across all your visualizations
    modality_order = ['auditory', 'haptic', 'visual']

    # --- Create the plot ---
    fig, ax = plt.subplots(figsize=(10, 6))

    # Seaborn automatically groups the bars side-by-side using 'hue'
    sns.barplot(
        data=melted_means,
        x='Modality',
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











def get_duration_p_value(subjects_data_trials):
    auditory_durations = []
    haptic_durations = []

    # Iterate through the dictionary to extract durations
    for subject_name, df in subjects_data_trials.items():

        df = df.copy()

        df = df[df['voice_start'] != 0]

        df['answer_duration'] = df['voice_end'] - df['voice_start']

        auditory_vals = df[df['Modality'] == 'auditory']['answer_duration'].tolist()
        haptic_vals = df[df['Modality'] == 'haptic']['answer_duration'].tolist()

        auditory_durations.extend(auditory_vals)
        haptic_durations.extend(haptic_vals)


    # Calculate and return the p-value using your custom function
    p_val = get_pairwise_p_value(auditory_durations, haptic_durations)

    return p_val






def get_reaction_time_p_value(subjects_data_trials):
    auditory_rts = []
    haptic_rts = []

    # Iterate through the dictionary to extract reaction times
    for subject_name, df in subjects_data_trials.items():
        if df is None or df.empty:
            continue

        df = df.copy()

        # Filter out missed/invalid trials where voice_start is 0
        df = df[df['Response start'] != 0]

        if df.empty:
            continue

        # Calculate Reaction Time: Voice Start minus Cue Presentation
        df['reaction_time'] = df['Response start'] - df['Phase timestamp']

        # Extract values for auditory and haptic
        auditory_vals = df[df['Modality'] == 'auditory']['reaction_time'].tolist()
        haptic_vals = df[df['Modality'] == 'haptic']['reaction_time'].tolist()

        auditory_rts.extend(auditory_vals)
        haptic_rts.extend(haptic_vals)

    # Safety check to ensure we have data for both modalities
    if not auditory_rts or not haptic_rts:
        print("Not enough valid reaction time data to compare auditory and haptic.")
        return None

    # Calculate and return the p-value using your custom function
    p_val = get_pairwise_p_value(auditory_rts, haptic_rts)

    return p_val








def plot_unified_tradeoffs(perception_results_all, experiment_logs_all):
    """
    Combines difficulty-specific error trade-offs, overall accuracy trade-offs,
    and overall misses trade-offs into a single 2x3 subplot grid.
    """
    # Create the figure grid
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    axes = axes.flatten()

    props = dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='gray')

    # =========================================================================
    # 1-3. Difficulty-Specific Trade-offs (Easy, Medium, Hard) -> axes[0], [1], [2]
    # =========================================================================
    difficulties = ['easy', 'medium', 'hard']

    for i, diff in enumerate(difficulties):
        stats_list = []
        for subject_name, perc_df in perception_results_all.items():
            log_df = experiment_logs_all.get(subject_name)
            if perc_df is None or perc_df.empty or log_df is None or log_df.empty:
                continue
            if 'Difficulty level' not in perc_df.columns or 'Difficulty level' not in log_df.columns:
                continue

            # Perception filter
            df_diff_perc = perc_df[perc_df['Difficulty level'].astype(str).str.strip().str.lower() == diff]
            if df_diff_perc.empty:
                continue

            df_diff_filtered = df_diff_perc[
                (df_diff_perc['Perceived angle'] != -1) & (df_diff_perc['Perceived angle'] != 0)]
            dist_col = 'Distance' if 'Distance' in df_diff_filtered.columns else 'Distnce'

            diff_errors = ((df_diff_filtered['Angle'] != df_diff_filtered['Perceived angle']) |
                           (df_diff_filtered[dist_col] != df_diff_filtered['Perceived distance'])).sum()

            # Log filter
            df_diff_log = log_df[log_df['Difficulty level'].astype(str).str.strip().str.lower() == diff].copy()
            if df_diff_log.empty or 'Number of collision' not in df_diff_log.columns:
                continue

            df_diff_log['Number of collision'] = pd.to_numeric(df_diff_log['Number of collision'], errors='coerce')
            diff_collisions = df_diff_log['Number of collision'].max() - df_diff_log['Number of collision'].min()

            if pd.isna(diff_collisions):
                continue

            stats_list.append({f'{diff} Errors': diff_errors, f'{diff} Collisions': diff_collisions})

        df_summary = pd.DataFrame(stats_list)

        if not df_summary.empty and len(df_summary) > 1:
            r, p = stats.pearsonr(df_summary[f'{diff} Errors'], df_summary[f'{diff} Collisions'])

            sns.regplot(data=df_summary, x=f'{diff} Errors', y=f'{diff} Collisions', ax=axes[i],
                        scatter_kws={'s': 60, 'alpha': 0.8, 'color': '#ff7f0e'},
                        line_kws={'color': '#d62728', 'linewidth': 2})

            stats_text = f'Pearson r = {r:.2f}\np-value = {p:.3f}'
            axes[i].text(0.05, 0.95, stats_text, transform=axes[i].transAxes, fontsize=12,
                         verticalalignment='top', bbox=props)

        axes[i].set_title(f'{diff.capitalize()} Phase: Errors vs. Collisions', fontsize=13, fontweight='bold')
        axes[i].set_xlabel(f'Errors in {diff.capitalize()} Phase', fontsize=11)
        axes[i].set_ylabel(f'Collisions in {diff.capitalize()} Phase', fontsize=11)
        axes[i].grid(True, linestyle='--', alpha=0.5)

    # =========================================================================
    # 4. Total Accuracy vs Total Collisions -> axes[3]
    # =========================================================================
    stats_list_tot = []
    for subject_name, perc_df in perception_results_all.items():
        log_df = experiment_logs_all.get(subject_name)
        if perc_df is None or perc_df.empty or log_df is None or log_df.empty:
            continue

        # Perception total accuracy (ignore -1 hardware faults and 0 misses)
        df_filtered = perc_df[(perc_df['Perceived angle'] > 0) & (perc_df['Perceived distance'] > 0)]
        if df_filtered.empty:
            continue

        dist_col = 'Distance' if 'Distance' in df_filtered.columns else 'Distnce'

        # Count trials where BOTH angle and distance were correct
        total_correct = ((df_filtered['Angle'] == df_filtered['Perceived angle']) &
                         (df_filtered[dist_col] == df_filtered['Perceived distance'])).sum()

        accuracy_pct = (total_correct / len(df_filtered)) * 100

        # Log total collisions
        if 'Number of collision' not in log_df.columns:
            continue
        log_df_copy = log_df.copy()
        log_df_copy['Number of collision'] = pd.to_numeric(log_df_copy['Number of collision'], errors='coerce')
        total_collisions = log_df_copy['Number of collision'].max() - log_df_copy['Number of collision'].min()

        if pd.isna(total_collisions):
            continue

        stats_list_tot.append({'Total Accuracy (%)': accuracy_pct, 'Total Collisions': total_collisions})

    df_tot = pd.DataFrame(stats_list_tot)
    if not df_tot.empty and len(df_tot) > 1:
        r, p_value = stats.pearsonr(df_tot['Total Accuracy (%)'], df_tot['Total Collisions'])

        sns.regplot(data=df_tot, x='Total Accuracy (%)', y='Total Collisions', ax=axes[3],
                    scatter_kws={'s': 60, 'alpha': 0.8, 'color': '#1f77b4'},
                    line_kws={'color': '#d62728', 'linewidth': 2})

        stats_text = f'Pearson r = {r:.2f}\np-value = {p_value:.3f}'
        axes[3].text(0.05, 0.95, stats_text, transform=axes[3].transAxes, fontsize=12,
                     verticalalignment='top', bbox=props, fontweight='bold')

    axes[3].set_title('Overall: Total Accuracy vs. Collisions', fontsize=13, fontweight='bold')
    axes[3].set_xlabel('Total Accuracy (%)', fontsize=11, fontweight='bold')
    axes[3].set_ylabel('Total Collisions', fontsize=11, fontweight='bold')
    axes[3].grid(True, linestyle='--', alpha=0.5)

    # =========================================================================
    # 5. Total Misses vs Total Collisions -> axes[4]
    # =========================================================================
    stats_list_misses = []
    for subject_name, perc_df in perception_results_all.items():
        log_df = experiment_logs_all.get(subject_name)
        if perc_df is None or perc_df.empty or log_df is None or log_df.empty:
            continue

        # Perception misses (perceived == 0)
        df_filtered = perc_df[(perc_df['Perceived angle'] != -1) & (perc_df['Perceived distance'] != -1)]
        misses = ((df_filtered['Perceived angle'] == 0) | (df_filtered['Perceived distance'] == 0)).sum()

        # Log total collisions
        if 'Number of collision' not in log_df.columns:
            continue
        log_df_copy = log_df.copy()
        log_df_copy['Number of collision'] = pd.to_numeric(log_df_copy['Number of collision'], errors='coerce')
        total_collisions = log_df_copy['Number of collision'].max() - log_df_copy['Number of collision'].min()

        if pd.isna(total_collisions):
            continue

        stats_list_misses.append({'Total Misses': misses, 'Total Collisions': total_collisions})

    df_misses = pd.DataFrame(stats_list_misses)
    if not df_misses.empty and len(df_misses) > 1:
        # User requested to only show Pearson r for this specific plot
        r, _ = stats.pearsonr(df_misses['Total Misses'], df_misses['Total Collisions'])

        sns.regplot(data=df_misses, x='Total Misses', y='Total Collisions', ax=axes[4],
                    scatter_kws={'s': 60, 'alpha': 0.8, 'color': '#2ca02c'},
                    line_kws={'color': '#d62728', 'linewidth': 2})

        stats_text = f'Pearson r = {r:.2f}'
        axes[4].text(0.05, 0.95, stats_text, transform=axes[4].transAxes, fontsize=12,
                     verticalalignment='top', bbox=props)

    axes[4].set_title('Overall: Perception Misses vs. Collisions', fontsize=13, fontweight='bold')
    axes[4].set_xlabel('Total Misses (Perceived == 0)', fontsize=11, fontweight='bold')
    axes[4].set_ylabel('Total Collisions', fontsize=11, fontweight='bold')
    axes[4].grid(True, linestyle='--', alpha=0.5)

    # =========================================================================
    # 6. Clean Up and Display
    # =========================================================================
    # Remove the 6th empty subplot
    fig.delaxes(axes[5])

    plt.tight_layout(pad=2.0)
    plt.show()










def print_subjects_with_high_specific_mod_misses(subjects_data_trials, fb_mod):
    print(f"Subjects with >3 {fb_mod} Misses at Degree 3:")
    print("-" * 45)


    for subject_name, df in subjects_data_trials.items():

        df_filtered = df[(df['Modality'] == {fb_mod}) &
                         (df['degree'] == 3) &
                         (df['Perceived angle'] != -1) &
                         (df['Perceived distance'] != -1)]

        # 2. Count the misses (where perceived degree or level is 0)
        miss_count = ((df_filtered['Perceived angle'] == 0) |
                      (df_filtered['Perceived distance'] == 0)).sum()

        if miss_count > 3:
            print(f"• {subject_name} (Total misses: {miss_count})")
            found_any = True


def plot_misses_vs_errors(subjects_data_trials):
    """
    Plots a regression scatter plot of Total Misses vs Total Errors per subject,
    and calculates the Pearson correlation coefficient.
    """
    stats_list = []

    # 1. Calculate metrics per subject
    for subject_name, df in subjects_data_trials.items():
        if df is None or df.empty:
            continue

        # Filter out invalid trials (-1)
        df_filtered = df[(df['Perceived angle'] != -1) & (df['Perceived distance'] != -1)]

        # Count Misses (where perceived is strictly 0)
        misses = ((df_filtered['Perceived angle'] == 0) |
                  (df_filtered['Perceived distance'] == 0)).sum()

        # Count Errors (where perceived does not match the actual stimuli)
        errors = ((df_filtered['Angle'] != df_filtered['Perceived angle']) |
                  (df_filtered['Distance'] != df_filtered['Perceived distance'])).sum()

        stats_list.append({
            'Subject': subject_name,
            'Total Misses': misses,
            'Total Errors': errors
        })

    df_summary = pd.DataFrame(stats_list)

    if df_summary.empty:
        print("No valid data to plot.")
        return

    # 2. Calculate the Pearson Correlation Coefficient
    corr_val, p_val = stats.pearsonr(df_summary['Total Errors'], df_summary['Total Misses'])

    # 3. Create the Scatter Plot
    plt.figure(figsize=(8, 6))

    sns.regplot(
        data=df_summary,
        x='Total Errors',
        y='Total Misses',
        scatter_kws={'s': 60, 'alpha': 0.8, 'color': '#9467bd'},  # Purple dots
        line_kws={'color': '#d62728', 'linewidth': 2}  # Red regression line
    )

    # 4. Add the correlation text box inside the plot
    textstr = f'Pearson r = {corr_val:.3f}'
    plt.text(
        0.05, 0.95, textstr,
        transform=plt.gca().transAxes,
        fontsize=12,
        verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='gray')
    )

    # 5. Customize Aesthetics
    plt.title('Relationship Between Total Errors and Total Misses', fontsize=14)
    plt.xlabel('Total Errors (Degree or Level mismatch)', fontsize=12)
    plt.ylabel('Total Misses (Perceived == 0)', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.show()


def get_missed_invalidated_trials_percentage(subjects_data_trials):
    """Calculates global and modality-specific percentages for missed and invalidated trials."""

    valid_dfs = [df for df in subjects_data_trials.values() if df is not None and not df.empty]

    if not valid_dfs:
        print("No valid data found in the provided dictionary.")
        return

    full_data = pd.concat(valid_dfs, ignore_index=True)

    col_name = 'Distance perceived'
    if col_name not in full_data.columns:
        if 'Perceived distance' in full_data.columns:
            col_name = 'Perceived distance'
        else:
            print("❌ Error: Could not find a 'Distance perceived' column in the dataset.")
            return

    total_trials = len(full_data)

    invalidated_count = (full_data[col_name] == -1).sum()
    missed_count = (full_data[col_name] == 0).sum()

    invalidated_pct = (invalidated_count / total_trials) * 100
    missed_pct = (missed_count / total_trials) * 100

    print("=========================================")
    print("📊 Trial Status Summary")
    print("=========================================")
    print(f"Total Trials Analyzed: {total_trials:,}")
    print(f"Invalidated Trials (-1): {invalidated_count:,} ({invalidated_pct:.2f}%)")
    print(f"Missed Trials (0):       {missed_count:,} ({missed_pct:.2f}%)")

    if 'Modality' in full_data.columns:
        print("=========================================")
        print("📊 Missed Trials by Modality")
        print("=========================================")

        modalities = ['visual', 'auditory', 'haptic']
        existing_mods = full_data['Modality'].unique()

        for mod in [m for m in modalities if m in existing_mods]:
            mod_data = full_data[full_data['Modality'] == mod]
            total_mod_trials = len(mod_data)

            if total_mod_trials == 0:
                continue

            mod_misses = (mod_data[col_name] == 0).sum()

            pct_within_modality = (mod_misses / total_mod_trials) * 100
            pct_overall = (mod_misses / total_trials) * 100

            print(f"--- {mod.capitalize()} ---")
            print(f"Misses: {mod_misses:,} (out of {total_mod_trials:,} {mod} cues)")
            print(f"% within {mod} cues: {pct_within_modality:.2f}%")
            print(f"% of all trials overall:  {pct_overall:.2f}%")
            print("")

    print("=========================================")


def print_collision_statistics_by_difficulty(experiment_logs_all):
    """
    Calculates and prints the min, max, median, and mean number of collisions
    for Easy, Medium, and Hard difficulty levels across all participants.
    """
    collision_data = []

    for subject, logs_df in experiment_logs_all.items():
        # Check if valid dataframe and required columns exist
        if logs_df is None or logs_df.empty or 'Number of collision' not in logs_df.columns or 'Difficulty level' not in logs_df.columns:
            continue

        valid_logs = logs_df.dropna(subset=['Number of collision', 'Difficulty level']).copy()
        if valid_logs.empty:
            continue

        valid_logs['Number of collision'] = pd.to_numeric(valid_logs['Number of collision'], errors='coerce')
        valid_logs['Difficulty level'] = valid_logs['Difficulty level'].astype(str).str.strip().str.lower()

        # Calculate total collisions per phase for this subject
        for diff in ['easy', 'medium', 'hard']:
            diff_logs = valid_logs[valid_logs['Difficulty level'] == diff]
            if not diff_logs.empty:
                phase_col = diff_logs['Number of collision'].max() - diff_logs['Number of collision'].min()
                if pd.notna(phase_col):
                    collision_data.append({
                        'Difficulty': diff.capitalize(),
                        'Collisions': phase_col
                    })

    df_cols = pd.DataFrame(collision_data)

    if df_cols.empty:
        print("No valid collision data found.")
        return None

    # Group by difficulty and calculate statistics
    stats_df = df_cols.groupby('Difficulty')['Collisions'].agg(
        Min='min',
        Max='max',
        Median='median',
        Mean='mean'
    ).reset_index()

    # Sort to ensure standard Easy -> Medium -> Hard order
    difficulty_order = {'Easy': 0, 'Medium': 1, 'Hard': 2}
    stats_df['Sort_Order'] = stats_df['Difficulty'].map(difficulty_order)
    stats_df = stats_df.sort_values(by='Sort_Order').drop(columns=['Sort_Order'])

    # Print the results
    print("\n" + "=" * 65)
    print("COLLISION STATISTICS BY DIFFICULTY")
    print("=" * 65)
    for _, row in stats_df.iterrows():
        print(f"Difficulty: {row['Difficulty']:<8} | Min: {row['Min']:<4.0f} | Max: {row['Max']:<4.0f} | Median: {row['Median']:<6.1f} | Mean: {row['Mean']:<6.2f}")
    print("=" * 65)

    return stats_df


def analyze_and_plot_joystick_variance(experiment_logs_all):
    """
    Calculates the variance of joystick magnitude for each participant across
    Easy, Medium, and Hard difficulties. Performs pairwise Wilcoxon signed-rank
    tests and plots a box plot with statistical annotations.
    """
    variance_data = []
    difficulty_order = ['easy', 'medium', 'hard']

    # 1. Process data and calculate magnitude variance
    for subject, logs_df in experiment_logs_all.items():
        if logs_df is None or logs_df.empty:
            continue

        if not {'Thumbstick x', 'Thumbstick y', 'Difficulty level'}.issubset(logs_df.columns):
            continue

        df_copy = logs_df.copy()
        df_copy['Difficulty level'] = df_copy['Difficulty level'].astype(str).str.strip().str.lower()

        for diff in difficulty_order:
            phase_logs = df_copy[df_copy['Difficulty level'] == diff]

            if phase_logs.empty:
                continue

            x_vals = pd.to_numeric(phase_logs['Thumbstick x'], errors='coerce')
            y_vals = pd.to_numeric(phase_logs['Thumbstick y'], errors='coerce')

            # Calculate magnitude: r = sqrt(x^2 + y^2)
            magnitude = np.sqrt(x_vals ** 2 + y_vals ** 2)

            # Calculate variance of the magnitude
            mag_variance = magnitude.var()

            if pd.notna(mag_variance):
                variance_data.append({
                    'Subject': subject,
                    'Difficulty': diff.capitalize(),
                    'Magnitude Variance': mag_variance
                })

    metrics_df = pd.DataFrame(variance_data)

    if metrics_df.empty:
        print("No valid joystick data found.")
        return None

    # Ensure correct categorical order for plotting
    plot_order = ['Easy', 'Medium', 'Hard']
    metrics_df['Difficulty'] = pd.Categorical(metrics_df['Difficulty'], categories=plot_order, ordered=True)

    # 2. Prepare for statistical testing
    # Pivot to align subject data row-by-row for paired testing
    pivot_df = metrics_df.pivot(index='Subject', columns='Difficulty', values='Magnitude Variance')

    pairs = [('Easy', 'Medium'), ('Medium', 'Hard'), ('Easy', 'Hard')]
    p_values = {}

    print("\n" + "=" * 50)
    print("WILCOXON SIGNED-RANK TEST (PAIRED, NON-PARAMETRIC)")
    print("=" * 50)

    for diff1, diff2 in pairs:
        # Drop any subjects missing data in either of the two difficulties being compared
        paired_data = pivot_df[[diff1, diff2]].dropna()

        if len(paired_data) < 2:
            p_values[(diff1, diff2)] = np.nan
            print(f"{diff1} vs {diff2}: Not enough data for paired test.")
            continue

        # Run Wilcoxon without checking normality
        stat, p_val = wilcoxon(paired_data[diff1], paired_data[diff2], alternative='two-sided')
        p_values[(diff1, diff2)] = p_val

        p_str = "< 0.001" if p_val < 0.001 else f"= {p_val:.4f}"
        print(f"{diff1:<6} vs {diff2:<6} | W = {stat:<6.1f} | p {p_str}")

    print("=" * 50)

    # 3. Plotting
    sns.set_theme(style="whitegrid", context="paper", font_scale=1.2)
    fig, ax = plt.subplots(figsize=(9, 6))

    # Box plot
    sns.boxplot(data=metrics_df, x='Difficulty', y='Magnitude Variance', order=plot_order,
                palette='Set2', width=0.5, showmeans=True,
                meanprops={"marker": "o", "markerfacecolor": "white", "markeredgecolor": "black"}, ax=ax)

    # Overlay individual data points for transparency
    sns.stripplot(data=metrics_df, x='Difficulty', y='Magnitude Variance', order=plot_order,
                  color='black', alpha=0.5, jitter=True, ax=ax)

    # 4. Statistical Annotations
    y_max = metrics_df['Magnitude Variance'].max()
    y_range = y_max - metrics_df['Magnitude Variance'].min()

    # Heights for the bracket lines
    h1 = y_max + (y_range * 0.05)  # Height for consecutive pairs (Easy-Med, Med-Hard)
    h2 = y_max + (y_range * 0.15)  # Height for outer pair (Easy-Hard)

    bracket_configs = [
        ('Easy', 'Medium', 0, 1, h1),
        ('Medium', 'Hard', 1, 2, h1),
        ('Easy', 'Hard', 0, 2, h2)
    ]

    for diff1, diff2, x1, x2, height in bracket_configs:
        p_val = p_values.get((diff1, diff2), np.nan)
        if pd.isna(p_val):
            continue

        p_text = "p < 0.001" if p_val < 0.001 else f"p = {p_val:.3f}"

        # Determine font weight based on significance (alpha = 0.05)
        weight = "bold" if p_val < 0.05 else "normal"

        # Draw bracket
        ax.plot([x1, x1, x2, x2], [height - y_range * 0.02, height, height, height - y_range * 0.02],
                lw=1.5, color='black')

        # Add text
        ax.text((x1 + x2) * 0.5, height + y_range * 0.01, p_text, ha='center', va='bottom',
                color='black', fontsize=11, fontweight=weight)

    # Adjust y-limit to fit annotations
    ax.set_ylim(bottom=max(0, metrics_df['Magnitude Variance'].min() - y_range * 0.05),
                top=h2 + (y_range * 0.1))

    ax.set_title("Joystick Magnitude Variance Across Difficulties", fontweight='bold', fontsize=14, pad=15)
    ax.set_ylabel("Variance of Magnitude ($r^2$)", fontweight='bold')
    ax.set_xlabel("Difficulty", fontweight='bold')

    plt.tight_layout()
    plt.show()


def run_multivariate_joystick_analysis(experiment_logs_all, n_permutations=999):
    """
    Calculates 2D Joystick Variances (X and Y) per participant and difficulty,
    then runs both:
      1. Parametric: Multivariate Analysis of Variance (MANOVA)
      2. Non-Parametric: Permutational Multivariate Analysis (PERMANOVA-style)
    """
    data_list = []
    difficulty_order = ['easy', 'medium', 'hard']

    # 1. Extract 2D variances (X and Y separately)
    for subject, logs_df in experiment_logs_all.items():
        if logs_df is None or logs_df.empty:
            continue
        if not {'Thumbstick x', 'Thumbstick y', 'Difficulty level'}.issubset(logs_df.columns):
            continue

        df_copy = logs_df.copy()
        df_copy['Difficulty level'] = df_copy['Difficulty level'].astype(str).str.strip().str.lower()

        for diff in difficulty_order:
            phase_logs = df_copy[df_copy['Difficulty level'] == diff]
            if phase_logs.empty:
                continue

            x_vals = pd.to_numeric(phase_logs['Thumbstick x'], errors='coerce')
            y_vals = pd.to_numeric(phase_logs['Thumbstick y'], errors='coerce')

            var_x = x_vals.var()
            var_y = y_vals.var()

            if pd.notna(var_x) and pd.notna(var_y):
                data_list.append({
                    'Subject': subject,
                    'Difficulty': diff.capitalize(),
                    'Var_X': var_x,
                    'Var_Y': var_y
                })

    df = pd.DataFrame(data_list)
    if df.empty:
        print("No valid 2D joystick data found.")
        return None

    # Keep only subjects who completed all 3 phases
    counts = df.groupby('Subject')['Difficulty'].nunique()
    complete_subjects = counts[counts == 3].index
    df = df[df['Subject'].isin(complete_subjects)].copy()

    print("=" * 80)
    print(f"MULTIVARIATE ANALYSIS (2D Joystick: Var_X & Var_Y) | N = {df['Subject'].nunique()} subjects")
    print("=" * 80)

    # -------------------------------------------------------------
    # METHOD 1: Parametric MANOVA
    # -------------------------------------------------------------
    print("\n" + "-" * 35 + " 1. PARAMETRIC MANOVA " + "-" * 35)
    try:
        manova_model = MANOVA.from_formula('Var_X + Var_Y ~ C(Difficulty)', data=df)
        manova_res = manova_model.mv_test()
        print(manova_res)
    except Exception as e:
        print(f"Error in MANOVA calculation: {e}")

    # -------------------------------------------------------------
    # METHOD 2: Non-Parametric Permutational Multivariate Test (PERMANOVA)
    # -------------------------------------------------------------
    print("-" * 30 + " 2. NON-PARAMETRIC PERMANOVA " + "-" * 30)

    # Coordinates in 2D space: [Var_X, Var_Y]
    X_coords = df[['Var_X', 'Var_Y']].values
    groups = df['Difficulty'].values
    unique_groups = np.unique(groups)
    g = len(unique_groups)
    n = len(df)

    # Pairwise Euclidean Distance Matrix
    D = squareform(pdist(X_coords, metric='euclidean'))

    def compute_pseudo_f(dist_mat, grp_labels):
        """Calculates Anderson's Pseudo-F statistic from a distance matrix."""
        # Total Sum of Squares (SST)
        sst = np.sum(dist_mat ** 2) / (2 * n)

        # Within-group Sum of Squares (SSW)
        ssw = 0.0
        for grp in unique_groups:
            idx = np.where(grp_labels == grp)[0]
            n_grp = len(idx)
            if n_grp > 1:
                sub_d = dist_mat[np.ix_(idx, idx)]
                ssw += np.sum(sub_d ** 2) / (2 * n_grp)

        ssb = sst - ssw  # Between-group Sum of Squares
        df_b = g - 1
        df_w = n - g
        pseudo_f = (ssb / df_b) / (ssw / df_w) if ssw > 0 else 0.0
        return pseudo_f

    # Observed statistic
    obs_f = compute_pseudo_f(D, groups)

    # Permutation Test (shuffling difficulty labels)
    np.random.seed(42)
    perm_f = []
    for _ in range(n_permutations):
        shuffled_groups = np.random.permutation(groups)
        perm_f.append(compute_pseudo_f(D, shuffled_groups))

    perm_f = np.array(perm_f)
    p_permanova = (np.sum(perm_f >= obs_f) + 1) / (n_permutations + 1)

    print(f"Number of Permutations : {n_permutations}")
    print(f"Observed Pseudo-F      : {obs_f:.4f}")
    print(f"Permutational p-value  : {p_permanova:.4f}" + (
        " (Significant p < 0.05)" if p_permanova < 0.05 else " (Not Significant)"))
    print("=" * 80 + "\n")
    plot_multivariate_joystick(df)


def plot_multivariate_joystick(df):
    """
    Plots the 2D distribution of Joystick Variances (X vs Y) across difficulties.
    Shows individual data points, density contours, and the trajectory of centroids.
    """
    if df is None or df.empty:
        print("No data available to plot.")
        return

    # تنظیمات گرافیکی
    sns.set_theme(style="whitegrid", context="paper", font_scale=1.2)
    plt.figure(figsize=(10, 8))

    difficulty_order = ['Easy', 'Medium', 'Hard']
    colors = {'Easy': '#2ca02c', 'Medium': '#ff7f0e', 'Hard': '#d62728'}

    # 1. رسم نقاط پراکندگی (داده‌های تک تک افراد)
    sns.scatterplot(
        data=df,
        x='Var_X',
        y='Var_Y',
        hue='Difficulty',
        hue_order=difficulty_order,
        palette=colors,
        alpha=0.6,
        s=80,
        edgecolor='k',
        zorder=3
    )

    # 2. رسم هاله چگالی (Density Contours) برای نشان دادن پراکندگی هر سطح
    sns.kdeplot(
        data=df,
        x='Var_X',
        y='Var_Y',
        hue='Difficulty',
        hue_order=difficulty_order,
        palette=colors,
        levels=3,
        alpha=0.4,
        linewidths=1.5,
        zorder=2
    )

    # 3. محاسبه و رسم مراکز ثقل (میانگین دو بعدی) و مسیر تغییرات
    centroids_x = []
    centroids_y = []

    for diff in difficulty_order:
        subset = df[df['Difficulty'] == diff]
        mean_x = subset['Var_X'].mean()
        mean_y = subset['Var_Y'].mean()

        centroids_x.append(mean_x)
        centroids_y.append(mean_y)

        # علامت‌گذاری مرکز ثقل با یک ضربدر بزرگ
        plt.scatter(mean_x, mean_y, marker='X', s=250, color=colors[diff],
                    edgecolor='black', linewidths=2, zorder=5)

        # اضافه کردن متن راهنما برای مرکز ثقل
        plt.text(mean_x, mean_y + (df['Var_Y'].max() * 0.02), f'{diff} Mean',
                 ha='center', va='bottom', fontsize=10, fontweight='bold')

    # 4. رسم فلش برای نشان دادن مسیر تغییرات از Easy به Medium و Hard
    for i in range(len(centroids_x) - 1):
        plt.annotate(
            '',
            xy=(centroids_x[i + 1], centroids_y[i + 1]),
            xytext=(centroids_x[i], centroids_y[i]),
            arrowprops=dict(facecolor='black', width=2, headwidth=10, alpha=0.5, shrink=0.05),
            zorder=4
        )

    # تنظیمات نهایی ظاهر نمودار
    plt.title('Multivariate Shift in Joystick Variance (X vs Y)', fontweight='bold', fontsize=15, pad=15)
    plt.xlabel('Variance of X-Axis (Horizontal Movement)', fontweight='bold')
    plt.ylabel('Variance of Y-Axis (Vertical Movement)', fontweight='bold')

    # تنظیم محدوده محورها از صفر برای درک بهتر مقیاس
    plt.xlim(left=0)
    plt.ylim(bottom=0)

    # تنظیم راهنمای نمودار
    handles, labels = plt.gca().get_legend_handles_labels()
    # فیلتر کردن راهنما برای حذف موارد تکراری ناشی از kdeplot
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys(), title='Difficulty', loc='upper right', framealpha=0.9)

    plt.tight_layout()
    plt.show()











def plot_modality_accuracy(
    perception_results_all,
    modality_column="Modality",
    figsize=(16, 7)
):
    """
    Plot accuracy and polar accuracy (%) across difficulty levels.

    Modalities:
        Visual, Auditory, Haptic, Total

    Valid trials:
        Exclude trials where perceived angle or distance is
        -1 or 0.

    Accuracy:
        Exact match of actual and perceived angle AND distance.

    Polar accuracy:
        Geometric accuracy in polar coordinates, expressed
        as a percentage.

    Statistics:
        Paired two-sided Wilcoxon signed-rank tests between
        Easy vs Medium, Medium vs Hard, and Easy vs Hard.

    Total:
        Calculated by pooling all valid trials across
        Visual, Auditory, and Haptic for each participant
        and difficulty.

    Returns:
        results_df, pvalues_df, fig, axes
    """

    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
    from scipy.stats import wilcoxon

    # ------------------------------------------------------
    # Settings
    # ------------------------------------------------------

    difficulty_order = ["easy", "medium", "hard"]

    modality_order = [
        "Visual",
        "Auditory",
        "Haptic",
        "Total"
    ]

    original_modalities = [
        "Visual",
        "Auditory",
        "Haptic"
    ]

    comparisons = [
        ("easy", "medium"),
        ("medium", "hard"),
        ("easy", "hard")
    ]

    required_columns = {
        "Difficulty level",
        modality_column,
        "Angle",
        "Distance",
        "Perceived angle",
        "Perceived distance"
    }

    results_list = []

    # ------------------------------------------------------
    # Prepare all participant data
    # ------------------------------------------------------

    for subject_id, trials_df in perception_results_all.items():

        missing = required_columns - set(trials_df.columns)

        if missing:
            raise ValueError(
                f"Participant {subject_id} is missing columns: "
                f"{sorted(missing)}"
            )

        df = trials_df.copy()

        # Standardize modality and difficulty labels
        df["_Modality"] = (
            df[modality_column]
            .astype(str)
            .str.strip()
            .str.lower()
        )

        df["_Difficulty"] = (
            df["Difficulty level"]
            .astype(str)
            .str.strip()
            .str.lower()
        )

        numeric_cols = [
            "Angle",
            "Distance",
            "Perceived angle",
            "Perceived distance"
        ]

        for col in numeric_cols:
            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            )

        # --------------------------------------------------
        # Filter valid trials
        # --------------------------------------------------

        valid_mask = (
            df["Perceived angle"].notna()
            & df["Perceived angle"].ne(-1)
            & df["Perceived angle"].ne(0)
            & df["Perceived distance"].notna()
            & df["Perceived distance"].ne(-1)
            & df["Perceived distance"].ne(0)
            & df["Angle"].notna()
            & df["Distance"].notna()
        )

        valid_df = df.loc[valid_mask].copy()

        # --------------------------------------------------
        # Calculate each modality and Total
        # --------------------------------------------------

        for difficulty in difficulty_order:

            difficulty_df = valid_df.loc[
                valid_df["_Difficulty"] == difficulty
            ]

            for modality in modality_order:

                if modality == "Total":

                    # Pool all modalities together
                    subset = difficulty_df.loc[
                        difficulty_df["_Modality"].isin(
                            [
                                m.lower()
                                for m in original_modalities
                            ]
                        )
                    ].copy()

                else:

                    subset = difficulty_df.loc[
                        difficulty_df["_Modality"]
                        == modality.lower()
                    ].copy()

                n_valid = len(subset)

                if n_valid > 0:

                    actual_angle = subset["Angle"]
                    actual_distance = subset["Distance"]

                    perceived_angle = subset[
                        "Perceived angle"
                    ]

                    perceived_distance = subset[
                        "Perceived distance"
                    ]

                    # --------------------------------------
                    # Exact-match accuracy
                    # --------------------------------------

                    correct_mask = (
                        actual_angle.eq(perceived_angle)
                        & actual_distance.eq(perceived_distance)
                    )

                    accuracy = correct_mask.mean() * 100

                    # --------------------------------------
                    # Polar accuracy
                    # --------------------------------------

                    theta_true = (
                        actual_angle * (np.pi / 4)
                    )

                    theta_perceived = (
                        perceived_angle * (np.pi / 4)
                    )

                    r_true = actual_distance
                    r_perceived = perceived_distance

                    squared_error = (
                        r_true**2
                        + r_perceived**2
                        - 2 * r_true * r_perceived
                        * np.cos(
                            theta_true - theta_perceived
                        )
                    )

                    geometric_error = np.sqrt(
                        np.maximum(squared_error, 0)
                    )

                    r_max = max(
                        r_true.max(),
                        r_perceived.max()
                    )

                    if pd.isna(r_max) or r_max <= 0:

                        polar_accuracy = np.nan

                    else:

                        polar_accuracy_values = (
                            1 - geometric_error / (2 * r_max)
                        ) * 100

                        polar_accuracy = (
                            polar_accuracy_values
                            .clip(0, 100)
                            .mean()
                        )

                else:

                    accuracy = np.nan
                    polar_accuracy = np.nan

                results_list.append({
                    "Subject": subject_id,
                    "Modality": modality,
                    "Difficulty": difficulty,
                    "Accuracy": accuracy,
                    "Polar Accuracy": polar_accuracy,
                    "N Valid": n_valid
                })

    results_df = pd.DataFrame(results_list)

    # ======================================================
    # Paired Wilcoxon tests
    # ======================================================

    pvalues_list = []

    for modality in modality_order:

        modality_df = results_df.loc[
            results_df["Modality"] == modality
        ]

        for metric in [
            "Accuracy",
            "Polar Accuracy"
        ]:

            pivot = modality_df.pivot(
                index="Subject",
                columns="Difficulty",
                values=metric
            )

            for diff1, diff2 in comparisons:

                paired = pivot[
                    [diff1, diff2]
                ].dropna()

                n_pairs = len(paired)

                if n_pairs == 0:

                    p_val = np.nan

                elif np.allclose(
                    paired[diff1].values,
                    paired[diff2].values
                ):

                    p_val = 1.0

                else:

                    try:
                        _, p_val = wilcoxon(
                            paired[diff1],
                            paired[diff2],
                            alternative="two-sided"
                        )
                    except ValueError:
                        p_val = np.nan

                pvalues_list.append({
                    "Modality": modality,
                    "Metric": metric,
                    "Comparison": (
                        f"{diff1.capitalize()} vs "
                        f"{diff2.capitalize()}"
                    ),
                    "N": n_pairs,
                    "p-value": p_val
                })

    pvalues_df = pd.DataFrame(pvalues_list)

    # ======================================================
    # Print results
    # ======================================================

    print("\nMean Accuracy (%)")

    print(
        results_df.pivot_table(
            index="Modality",
            columns="Difficulty",
            values="Accuracy",
            aggfunc="mean"
        ).reindex(modality_order).round(2)
    )

    print("\nMean Polar Accuracy (%)")

    print(
        results_df.pivot_table(
            index="Modality",
            columns="Difficulty",
            values="Polar Accuracy",
            aggfunc="mean"
        ).reindex(modality_order).round(2)
    )

    print("\nPaired Wilcoxon p-values")

    print(
        pvalues_df.to_string(
            index=False,
            formatters={
                "p-value": lambda p: (
                    "p<0.001"
                    if pd.notna(p) and p < 0.001
                    else f"p={p:.3f}"
                    if pd.notna(p)
                    else "NaN"
                )
            }
        )
    )

    # ======================================================
    # Plot
    # ======================================================

    fig, axes = plt.subplots(
        1,
        2,
        figsize=figsize,
        sharex=True
    )

    metrics = [
        ("Accuracy", "Accuracy (%)"),
        ("Polar Accuracy", "Polar Accuracy (%)")
    ]

    palette = {
        "Visual": "tab:blue",
        "Auditory": "tab:orange",
        "Haptic": "tab:green",
        "Total": "tab:red"
    }

    markers = {
        "Visual": "o",
        "Auditory": "s",
        "Haptic": "^",
        "Total": "D"
    }

    for ax, (metric, ylabel) in zip(axes, metrics):

        sns.pointplot(
            data=results_df,
            x="Difficulty",
            y=metric,
            hue="Modality",
            hue_order=modality_order,
            order=difficulty_order,
            palette=palette,
            markers=[
                markers[m]
                for m in modality_order
            ],
            linestyles="-",
            errorbar=("ci", 95),
            capsize=0.06,
            dodge=0.3,
            ax=ax
        )

        ax.set_title(metric, fontsize=13)
        ax.set_xlabel("Difficulty")
        ax.set_ylabel(ylabel)
        ax.set_ylim(0, 115)
        ax.grid(True, alpha=0.3)

        # ----------------------------------------------
        # P-value annotations
        # ----------------------------------------------

        # Put annotations above the plotting area
        # in a separate text block to avoid overlap.
        annotation_lines = []

        for modality in modality_order:

            modality_pvals = pvalues_df.loc[
                (pvalues_df["Modality"] == modality)
                & (pvalues_df["Metric"] == metric)
            ]

            for _, row in modality_pvals.iterrows():

                p = row["p-value"]

                if pd.isna(p):
                    p_text = "p=NA"
                elif p < 0.001:
                    p_text = "p<0.001"
                else:
                    p_text = f"p={p:.3f}"

                annotation_lines.append(
                    f"{modality} | "
                    f"{row['Comparison']}: {p_text}"
                )

        ax.text(
            0.5,
            1.02,
            "\n".join(annotation_lines),
            transform=ax.transAxes,
            ha="center",
            va="bottom",
            fontsize=7.5,
            clip_on=False,
            bbox=dict(
                boxstyle="round,pad=0.3",
                facecolor="white",
                edgecolor="gray",
                alpha=0.9
            )
        )

        ax.legend(
            title="Modality",
            loc="lower left"
        )

    fig.tight_layout()

    plt.show()

    return results_df, pvalues_df, fig, axes














