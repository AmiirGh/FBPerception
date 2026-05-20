
from utils import *
from utils_questionnaire import *


def exp_performance_full():
    subjects_data_path_part = '../temp-data-for-plotting'
    subjects_data_path_full = '../s1-s2-j'
    subjects_data_path = subjects_data_path_full
    subject_names = os.listdir(subjects_data_path)
    subjects_data_trials = get_subjects_data_trials_df(subject_names, subjects_data_path)
    subjects_data_full = get_subjects_data_full_df(subject_names, subjects_data_path)

    plot_error_collision_tradeoff(subjects_data_trials, subjects_data_full)
    # plot_collisions_all(subjects_data_full)





    windows = [[0, 0.5], [0.5, 1], [1, 1.5], [1.5, 2], [2, 2.5], [2.5, 3],
               [3, 3.5], [3.5, 4], [4, 4.5], [4.5, 5], [5, 5.5], [5.5, 6]]
    plot_multiple_collision_time_windows(windows, subjects_data_full, subjects_data_trials)


    plot_mean_head_position_heatmap(subjects_data_full, bins=5)
    plot_thumbstick_heatmap(subjects_data_full, bins=5)
    plot_collisions_over_time_by_difficulty(subjects_data_full)
    plot_collisions_by_difficulty(subjects_data_full)
    # temp = final_coll_by_gr_p_val_df(final_collision_by_gr)


def exp_performance_trials():
    subjects_data_path_full = '../s1-s2-j'
    subjects_data_path = subjects_data_path_full
    subject_names = os.listdir(subjects_data_path)

    subjects_data_trials = get_subjects_data_trials_df(subject_names, subjects_data_path)

    all_miss_counts = get_all_miss_counts(subjects_data_trials)
    plot_all_miss_counts(all_miss_counts)
    v_a_miss_counts_p_val, v_h_miss_counts_p_val = get_p_val_miss_counts(all_miss_counts)

    # all_miss_counts_outliers = get_all_miss_counts_outliers(all_miss_counts, min_val=24) # returns a dataframe showing who and what are the outliers

    gr, all_miss_counts_gr_df = get_miss_rates_by_generation_rate(subjects_data_trials)
    miss_counts_by_gr_p_val_df = get_p_val_miss_counts_by_gr(all_miss_counts_gr_df, gr)

    plot_all_miss_counts_by_generation_rate(gr, all_miss_counts_gr_df)

    # accuracy_degree_all, accuracy_level_all, accuracy_full_all = get_accuracy_rates(subjects_data_trials)
    # plot_all_accuracy_rates([
    #     (accuracy_degree_all, "accuracy_degree", "Degree accuracy (%)"),
    #     (accuracy_level_all, "accuracy_level", "Level accuracy (%)"),
    #     (accuracy_full_all, "accuracy_full", "Level and degree accuracy (%)")])
    # accuracy_p_val_df = get_p_val_accuracy(accuracy_degree_all, accuracy_level_all, accuracy_full_all)

    # accuracy_degree_all_by_gr, accuracy_level_all_by_gr, accuracy_full_all_by_gr = get_accuracy_rates_by_generation_rate(
    #     subjects_data_trials)
    # plot_accuracy_rates_by_generation_rate([
    #     (accuracy_degree_all_by_gr, "accuracy_degree", "Degree accuracy (%)"),
    #     (accuracy_level_all_by_gr, "accuracy_level", "Level accuracy (%)"),
    #     (accuracy_full_all_by_gr, "accuracy_full", "Level and degree accuracy (%)")])
    # accuracy_rate_by_gr_p_val_df = get_p_val_accuracy_by_gr(accuracy_degree_all_by_gr, accuracy_level_all_by_gr, accuracy_full_all_by_gr, gr)

    plot_spatial_perception(subjects_data_trials, fbmod='audio')
    plot_spatial_perception(subjects_data_trials, fbmod='visual')
    plot_spatial_perception(subjects_data_trials, fbmod='haptic')

    error_results, error_distribution = compute_error_by_modality(subjects_data_trials)


    # plot_error_bars(error_results)



    # plot_error_boxplots(error_distribution)
    # get_lvl_err_1_p_value(error_distribution)

    # plot_weighted_error_means(error_results)

    # plot_answer_duration(subjects_data_trials)
    # a_h_duration_p_val = get_duration_p_value(subjects_data_trials)
    # plot_reaction_time(subjects_data_trials)
    # a_h_reaction_time_p_val = get_reaction_time_p_value(subjects_data_trials)


    # plot_misses_collision_tradeoff(subjects_data_trials)
    # plot_tradeoff_groups_error(subjects_data_trials)
    # plot_tradeoff_groups_misses(subjects_data_trials)

    # plot_deg_lvl_position_misses_boxplot(subjects_data_trials, 'visual')
    # plot_deg_lvl_position_misses_boxplot(subjects_data_trials, 'audio')
    # plot_deg_lvl_position_misses_boxplot(subjects_data_trials, 'haptic')
    # visual_miss_outliers = ['Yas_4358']
    # comparison_df = evaluate_outliers_performance(visual_miss_outliers, error_distribution)
    # print_subjects_with_high_specific_mod_misses(subjects_data_trials, 'haptic')


def questionnaire():
    df_questionnaire_final = pd.read_excel('../Questionnaire/final.xlsx')
    df_questionnaire_mid = pd.read_excel('../Questionnaire/mid.xlsx')

    plot_final_DEFGHIJK(df_questionnaire_final)
    plot_final_MNO(df_questionnaire_final)
    plot_final_L(df_questionnaire_final)
    plot_final_P(df_questionnaire_final)
    plot_final_QRS(df_questionnaire_final)

    plot_mid_fatigue_progression(df_questionnaire_mid)
    plot_mid_Dizziness_progression(df_questionnaire_mid)
    plot_mid_usefull_fb(df_questionnaire_mid)
    plot_mid_learning_curve(df_questionnaire_mid)
    plot_mid_modality_confusion(df_questionnaire_mid)
    plot_mid_percieved_speed(df_questionnaire_mid)

if __name__ == "__main__":
    # exp_performance_full()
    exp_performance_trials()
    # questionnaire()
