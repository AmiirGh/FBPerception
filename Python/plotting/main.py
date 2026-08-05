
from utils import *
from utils_questionnaire import *
from utils_demographic import *
from utils_results_paper import *

def exp_performance_full():
    subjects_data_path_part = '../temp-data-for-plotting'
    subjects_data_path_full = '../s1-s2-j'
    subjects_data_path = subjects_data_path_full
    subject_names = os.listdir(subjects_data_path)
    subjects_data_trials = get_subjects_data_trials_df(subject_names, subjects_data_path)
    subjects_data_full = get_subjects_data_full_df(subject_names, subjects_data_path)

    plot_difficulty_error_collision_tradeoff(subjects_data_trials, 'hard')
    plot_error_collision_tradeoff(subjects_data_trials, subjects_data_full)



    plot_mean_head_position_heatmap(subjects_data_full, bins=5)
    plot_thumbstick_heatmap(subjects_data_full, bins=5)
    plot_collisions_over_time_by_difficulty(subjects_data_full)
    plot_collisions_by_difficulty(subjects_data_full)
    # temp = final_coll_by_gr_p_val_df(final_collision_by_gr)


def exp_performance_trials(color_palette):

    # all_miss_counts = get_all_miss_counts(subjects_data_trials)
    # plot_all_miss_counts(all_miss_counts, color_palette)
    # v_a_miss_counts_p_val, v_h_miss_counts_p_val = get_p_val_miss_counts(all_miss_counts)

    # all_miss_counts_outliers = get_all_miss_counts_outliers(all_miss_counts, min_val=24) # returns a dataframe showing who and what are the outliers

    # gr, all_miss_counts_gr_df = get_miss_rates_by_generation_rate(subjects_data_trials)
    # miss_counts_by_gr_p_val_df = get_p_val_miss_counts_by_gr(all_miss_counts_gr_df, gr)

    # plot_all_miss_counts_by_generation_rate(gr, all_miss_counts_gr_df, color_palette)

    # accuracy_degree_all, accuracy_level_all, accuracy_full_all = get_accuracy_rates(subjects_data_trials)
    # plot_all_accuracy_rates([
    #     (accuracy_degree_all, "accuracy_degree", "Degree accuracy (%)"),
    #     (accuracy_level_all, "accuracy_level", "Level accuracy (%)"),
    #     (accuracy_full_all, "accuracy_full", "Level and degree accuracy (%)")], color_palette)
    # accuracy_p_val_df = get_p_val_accuracy(accuracy_degree_all, accuracy_level_all, accuracy_full_all)

    # accuracy_degree_all_by_gr, accuracy_level_all_by_gr, accuracy_full_all_by_gr = get_accuracy_rates_by_generation_rate(
    #     subjects_data_trials)
    # plot_accuracy_rates_by_generation_rate([
    #     (accuracy_degree_all_by_gr, "accuracy_degree", "Degree accuracy (%)"),
    #     (accuracy_level_all_by_gr, "accuracy_level", "Level accuracy (%)"),
    #     (accuracy_full_all_by_gr, "accuracy_full", "Level and degree accuracy (%)")], color_palette)
    # accuracy_rate_by_gr_p_val_df = get_p_val_accuracy_by_gr(accuracy_degree_all_by_gr, accuracy_level_all_by_gr, accuracy_full_all_by_gr, gr)

    # plot_spatial_perception(subjects_data_trials, fbmod='audio')
    # plot_spatial_perception(subjects_data_trials, fbmod='visual')
    # plot_spatial_perception(subjects_data_trials, fbmod='haptic')


    # plot_all_perceptions(subjects_data_trials, color_palette, 'auditory', 'haptic', 'visual')


    # error_results, error_distribution = compute_error_by_modality(subjects_data_trials)


    # plot_error_bars(error_results, color_palette)



    # plot_error_boxplots(error_distribution, color_palette)
    # get_lvl_err_1_p_value(error_distribution)

    # plot_weighted_error_means(error_results)

    # plot_answer_duration(subjects_data_trials, color_palette)
    # plot_overall_timing_metrics(subjects_data_trials)
    # a_h_duration_p_val = get_duration_p_value(subjects_data_trials)
    # plot_reaction_time(subjects_data_trials, color_palette)
    # a_h_reaction_time_p_val = get_reaction_time_p_value(subjects_data_trials)


    # plot_misses_collision_tradeoff(perception_results_all, experiment_logs_all)
    # plot_tradeoff_groups_error(perception_results_all, experiment_logs_all)
    # plot_tradeoff_groups_misses(perception_results_all, experiment_logs_all)

    # plot_deg_lvl_position_misses_boxplot(subjects_data_trials, 'visual')
    # plot_deg_lvl_position_misses_boxplot(subjects_data_trials, 'audio')
    # plot_deg_lvl_position_misses_boxplot(subjects_data_trials, 'haptic')
    # visual_miss_outliers = ['Yas_4358']
    # comparison_df = evaluate_outliers_performance(visual_miss_outliers, error_distribution)
    # print_subjects_with_high_specific_mod_misses(subjects_data_trials, 'haptic')
    # plot_misses_vs_errors(perception_results_all)

    # get_missed_invalidated_trials_percentage(perception_results_all)
    pass
def questionnaire():


    # plot_final_DEFGHIJK(df_questionnaire_final)
    # plot_final_MNO(df_questionnaire_final)
    # plot_final_L(df_questionnaire_final)
    # plot_final_P(df_questionnaire_final)
    # plot_final_QRS(df_questionnaire_final)

    # plot_mid_fatigue_progression(df_questionnaire_mid)
    # plot_mid_Dizziness_progression(df_questionnaire_mid)
    # plot_mid_usefull_fb(df_questionnaire_mid)
    # plot_mid_learning_curve(df_questionnaire_mid)
    # plot_mid_modality_confusion(df_questionnaire_mid)
    # plot_mid_percieved_speed(df_questionnaire_mid)

    # plot_metacognition_correlations(perception_results_all, df_questionnaire_final, color_palette)
    # plot_self_perc_success_vs_performance_correlations(perception_results_all, experiment_logs_all, df_questionnaire_final,
    #                                       color_palette)

    # plot_questionnaire_results(df_questionnaire_final, color_code='#99DDFF')

    # plot_unified_performance_correlations(perception_results_all, experiment_logs_all, df_questionnaire_final, color_palette)
    ...
def demographic():
    # check_folder_contents('../s1-s2-j')
    # number_of_subjects_info('../s1-s2-j', 'gender', 'male')

    # plot_tiredness_performance_correlations(demographics, perception_results_all, experiment_logs_all, color_palette)

    # plot_ticklishness_haptic_correlations(demographics, perception_results_all, color_palette)

    # count_gender_by_phase_sequence(demographics)
    pass


def exp_results_paper():




    # plot_misses_grouped_box(perception_results_all, color_palette)
    # error_results, error_distribution = compute_error_by_modality_temp(perception_results_all)
    # plot_error_boxplots_temp(error_distribution, color_palette)

    ####### Needs experiment logs
    # experiment_logs_all = get_experiment_logs_df(data_path)

    # plot_tradeoff_groups_error(perception_results_all, experiment_logs_all)
    # plot_tradeoff_groups_misses(perception_results_all, experiment_logs_all)

    # plot_multiple_collision_time_windows(windows, experiment_logs_all, perception_results_all, color_palette)

    # print("_______Q1________")
    # test_wickens_with_task_shedding(perception_results_all, experiment_logs_all)

    # test_cross_modal_mapping_cost(perception_results_all)
    # test_perceptual_tunneling(perception_results_all, color_palette)

    # test_speed_accuracy_tradeoffs(perception_results_all)
    # test_depth_perception_limits(perception_results_all)
    # analyze_spatial_anisotropy(perception_results_all)
    # analyze_motor_cognitive_interference(perception_results_all, experiment_logs_all)

    # gpt Qs
    # analyze_attention_redistribution(perception_results_all, experiment_logs_all)
    # plot_cognitive_signatures_heatmap(perception_results_all, experiment_logs_all)
    # analyze_latent_strategies(perception_results_all, experiment_logs_all, n_clusters=4)
    # plot_collision_vs_accuracy(perception_results_all, experiment_logs_all, color_palette)

    # Claude Qs
    # Q1: Is dual-task interference resource-specific, or just general capacity?
    # test_mrt_interaction(perception_results_all, experiment_logs_all, color_palette)
    #
    # plot_accuracy_over_time_by_modality(perception_results_all, color_palette)
    # plot_longitudinal_performance(perception_results_all, experiment_logs_all, color_palette)
    # df = plot_gender_differences(perception_results_all, demographics_data_path)
    # test_gender_differences(df, metrics_to_test=None)
    # plot_gender_differences_by_modality(perception_results_all, experiment_logs_all, demographics_data_path, color_palette)

    demo_path  = '../Dataset/Dataset/Metadata/Demographics.csv'
    # plot_analysis_dashboard(windows, perception_results_all, experiment_logs_all, error_distribution, demographics_path, color_palette)
    # plot_timing_metrics_unpaired(perception_results_all, color_palette)


    # analyze_sequence_vs_adaptation(experiment_logs_all, bin_size=5)

    # correlate_fatigue_and_adaptation(experiment_logs_all, df_questionnaire_mid, bin_size=5)
    # plot_timing_metrics_paired(perception_results_all, color_palette)



    # Spider
    # plot_modality_spider_chart(perception_results_all, color_palette)

    pass


def exp_results_paper_final():

    # Timings
    # plot_timing_metrics_unpaired(perception_results_all, color_palette)

    # Meta cognition Q9
    # plot_metacognitive_awareness_stacked(perception_results_all, experiment_logs_all, df_questionnaire_final)

    # Q1, Q2, Q13, Q14, Q15 statistics
    # print_questionnaire_stats_and_pvalue(df_questionnaire_final)


    # Collisions over time
    # plot_stitched_collision_timeline_with_metric(experiment_logs_all, bin_size=10, time_col='Timestamp', color='#DD8452', deviation_percent=5)
    # plot_adaptation_index_by_difficulty(experiment_logs_all, bin_size=5, deviation_percent=5)
    # analyze_individual_adaptation(experiment_logs_all, bin_size=5)

    # Gender differences - No statistical significance
    # plot_performance_by_condition(perception_results_all, experiment_logs_all, color_palette, axes=None)

    # Trade offs
    # plot_unified_tradeoffs(perception_results_all, experiment_logs_all)


    ...


def exp_results_paper_final_2():
    '''
    This function is for the final plots
    '''

    # Modality analysis
    plot_performance_and_polar_accuracy(perception_results_all, experiment_logs_all, color_palette, axes=None)


    # CLFE
    # plot_multiple_collision_time_windows(0.5, experiment_logs_all, perception_results_all, color_palette)

    # Difficulty analysis
    analyze_attention_redistribution(perception_results_all, experiment_logs_all, demographics)

    # Meta cognition, Q5, Q10, Q11, Q12
    plot_unified_performance_correlations(perception_results_all, experiment_logs_all, df_questionnaire_final,
                                          color_palette)

    pass

if __name__ == "__main__":

    color_palette = {'visual': '#99DDFF', 'auditory': '#BBCC33', 'haptic': '#EE8866', 'total': '#2205d1',
                     'collision': '#8a754d', 'male': '#525EFF', 'female':'#C052FF',
                     'easy': '#AEFF52', 'medium':'#FFE252' , 'hard':'#FF5252'}
    data_path = '../Dataset/Dataset/Recordings'
    demographics_path = '../Dataset/Dataset/Metadata/Demographics.csv'
    # demographics_data_path = '../Dataset/Dataset/Metadata/Demographics.csv'
    # subject_names = os.listdir(data_path)
    perception_results_all = get_perception_results_df(data_path)
    experiment_logs_all = get_experiment_logs_df(data_path)
    df_questionnaire_final = pd.read_csv('../Dataset/Dataset/Questionnaire/final.csv')
    df_questionnaire_mid = pd.read_csv('../Dataset/Dataset/Questionnaire/mid.csv')
    demographics = pd.read_csv(demographics_path)


    # exp_performance_full()
    # exp_performance_trials(color_palette)
    # exp_results_paper()
    # exp_results_paper_final()
    exp_results_paper_final_2()

    # questionnaire()
    # demographic()




