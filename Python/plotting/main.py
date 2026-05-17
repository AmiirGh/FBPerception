import time

from utils import *

subjects_data_path = '../../s1-s2-j'
subject_audio_delays_path = '../../cleaning/audio delays.xlsx'
subject_audio_delays = pd.read_excel(subject_audio_delays_path)
subject_names = os.listdir(subjects_data_path)

# file_names = get_file_names(csv_files)
subjects_data_trials = get_subjects_data_trials_df(subject_names, subjects_data_path)
# subjects_data_full = get_subjects_data_full_df(subject_names, subjects_data_path)

# df_list = get_df_list(csv_files, file_path)



# full_df_list = get_full_df_list()
# df_list_org = df_list.copy()
# df_list = remove_invalid_misses(subjects_data_trials)

all_miss_counts = get_all_miss_counts(subjects_data_trials)
plot_all_miss_counts(all_miss_counts)
# v_a_miss_counts_p_val, v_h_miss_counts_p_val = get_p_val_miss_counts(all_miss_counts)






# all_miss_counts_outliers = get_all_miss_counts_outliers(all_miss_counts, min_val=5) # returns a dataframe showing who and what are the outliers

gr, all_miss_counts_gr_df = get_miss_rates_by_generation_rate(subjects_data_trials)
miss_counts_by_gr_p_val_df = get_p_val_miss_counts_by_gr(all_miss_counts_gr_df, gr)

plot_all_miss_counts_by_generation_rate(gr, all_miss_counts_gr_df)

accuracy_degree_all, accuracy_level_all, accuracy_full_all = get_accuracy_rates(subjects_data_trials)
plot_all_accuracy_rates([
            (accuracy_degree_all, "accuracy_degree", "Degree accuracy (%)"),
            (accuracy_level_all, "accuracy_level", "Level accuracy (%)"),
            (accuracy_full_all, "accuracy_full", "Level and degree accuracy (%)")])
# accuracy_p_val_df = get_p_val_accuracy(accuracy_degree_all, accuracy_level_all, accuracy_full_all)


accuracy_degree_all_by_gr, accuracy_level_all_by_gr, accuracy_full_all_by_gr = get_accuracy_rates_by_generation_rate(subjects_data_trials)

plot_accuracy_rates_by_generation_rate([
            (accuracy_degree_all_by_gr, "accuracy_degree", "Degree accuracy (%)"),
            (accuracy_level_all_by_gr, "accuracy_level", "Level accuracy (%)"),
            (accuracy_full_all_by_gr, "accuracy_full", "Level and degree accuracy (%)")])
# accuracy_rate_by_gr_p_val_df = get_p_val_accuracy_by_gr(accuracy_degree_all_by_gr, accuracy_level_all_by_gr, accuracy_full_all_by_gr, gr)


# plot_collisions_all(df_list_org)

# collisions_by_gr, all_time_df_by_gr = get_collisions_by_generation_rate(df_list_org) # seems wrong
# plot_collisions_by_generation_rate(collisions_by_gr, all_time_df_by_gr)# seems wrong # seems wrong


# all_summary = calc_no_collisions_by_fbmod_for_time_window(full_df=full_df_list, start_sec=2, end_sec=4)
# plot_no_collisions_by_fbmod_for_time_window(all_summary, start_sec=2, end_sec=4)
# no_col_by_fbmod_p_val_df(all_summary)


# plot_mean_head_position_heatmap(full_df_list, bins=5)
# plot_thumbstick_heatmap(full_df_list, bins=5)

# final_collision_by_gr = get_final_collision_by_gr(full_df_list)
# plot_final_collisions_by_gr(final_collision_by_gr)
# temp = final_coll_by_gr_p_val_df(final_collision_by_gr)

time.sleep(3)
plot_spatial_perception(subjects_data_trials, fbmod='audio')
plot_spatial_perception(subjects_data_trials, fbmod='visual')
plot_spatial_perception(subjects_data_trials, fbmod='haptic')

error_results, error_distribution = compute_error_by_modality(subjects_data_trials)
plot_error_bars(error_results)

plot_error_boxplots(error_distribution)
# temp = amount_of_err_p_val_df(error_distribution)
plot_weighted_error_means(error_results)

# shifted_trials = apply_audio_delays(subjects_data_trials, subject_audio_delays)

plot_answer_duration(subjects_data_trials)

plot_reaction_time(subjects_data_trials)



