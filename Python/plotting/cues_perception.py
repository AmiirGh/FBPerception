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
import matplotlib.lines as mlines
from matplotlib.lines import Line2D
from scipy.interpolate import make_interp_spline

def get_subjects_data_trials_df(subjects_data_path):
    subjects_data_trials = {}

    for folder_name in sorted(os.listdir(subjects_data_path)):
        folder_path = os.path.join(subjects_data_path, folder_name)

        if not os.path.isdir(folder_path):
            continue

        csv_path = os.path.join(folder_path, "Perception results.csv")

        trials_data = pd.read_csv(csv_path)
        subjects_data_trials[folder_name] = trials_data

    return subjects_data_trials



def plot_all_perceptions(subjects_data_trials, color_palette, mod1='auditory', mod2='haptic', mod3='visual'):
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

    all_subject_dfs = [df for df in subjects_data_trials.values() if df is not None and not df.empty]
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

        for subject_name, df in subjects_data_trials.items():
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

if __name__ == "__main__":
    color_palette = {'visual': '#99DDFF', 'auditory': '#BBCC33', 'haptic': '#EE8866'}
    subjects_data_path_full = '../Dataset/Dataset/Recordings'
    subjects_data_trials = get_subjects_data_trials_df(subjects_data_path_full)
    plot_all_perceptions(subjects_data_trials, color_palette, 'auditory', 'haptic', 'visual')