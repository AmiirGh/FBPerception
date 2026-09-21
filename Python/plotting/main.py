from utils import *
from utils_questionnaire import *
from utils_demographic import *
from utils_results_paper import *



def results_modality():
    # 1. Manuscript
    # plot_timing_metrics_unpaired(perception_results_all, color_palette)
    # plot_performance_and_polar_accuracy(perception_results_all, experiment_logs_all, color_palette, axes=None)
    # plot_multiple_collision_time_windows(0.5, experiment_logs_all, perception_results_all, color_palette)
    # plot_all_perceptions(perception_results_all, color_palette, 'visual', 'auditory', 'haptic')
    # plot_error_boxplots(error_distribution, color_palette)
    # test_wickens_with_task_shedding(perception_results_all, experiment_logs_all) # *
    # test_perceptual_tunneling(perception_results_all, color_palette) # *
    # plot_modality_accuracy(perception_results_all, modality_column="Modality", figsize=(16, 7))

    # 2. Sup Mat
    # plot_longitudinal_performance(perception_results_all, experiment_logs_all, color_palette)
    # plot_modality_spider_chart(perception_results_all, color_palette)
    # plot_weighted_error_means(error_results) # -
    # test_depth_perception_limits(perception_results_all, color_palette)
    # plot_spatial_error_landscape(perception_results_all, color_palette)

    # 3. Remove
    # plot_collision_vs_accuracy(perception_results_all, experiment_logs_all, color_palette)
    # plot_efficiency_frontier_by_modality(perception_results_all, experiment_logs_all, color_palette)

    pass


def results_difficulty():
    # 1. Manuscript
    analyze_attention_redistribution(perception_results_all, experiment_logs_all, demographics) #if it doesnt include time metrics, add
    analyze_and_plot_joystick_variance(experiment_logs_all)
    print_collision_statistics_by_difficulty(experiment_logs_all)
    plot_workload_vs_accuracy_by_difficulty(perception_results_all, experiment_logs_all, color_palette)

    # 2. Sup Mat
    plot_stitched_collision_timeline_with_metric(experiment_logs_all, bin_size=10, time_col='Timestamp', color='#DD8452', deviation_percent=5)

    # 3. Remove
    pass

def results_modality_difficulty():
    # 1. Manuscript
    plot_performance_by_condition(perception_results_all, experiment_logs_all, color_palette, axes=None)
    plot_modality_difficulty_performance_matrices(perception_results_all, color_palette)

    # 2. Sup Mat

    # 3. Remove
    test_mrt_interaction(perception_results_all, experiment_logs_all, color_palette)
    pass

def results_gender():
    # 1. Manuscript
    df = plot_gender_differences(perception_results_all, demographics)
    test_gender_differences(df, metrics_to_test=None)
    plot_performance_by_gender(perception_results_all, experiment_logs_all, demographics_path, color_palette)
    pass


def results_questionnaire():
    # 1. Manuscript
    print_questionnaire_stats_and_pvalue(df_questionnaire_final)
    pass

def results_questionnaire_modality():
    # 1. Manuscript
    plot_unified_performance_correlations(perception_results_all, experiment_logs_all, df_questionnaire_final, color_palette)
    pass
def results_others():
    # 1. Manuscript
    # get_missed_invalidated_trials_percentage(perception_results_all)
    # plot_misses_vs_errors(perception_results_all)
    # plot_unified_tradeoffs(perception_results_all, experiment_logs_all)


    # 2. Sup Mat
    # plot_mean_head_position_heatmap(experiment_logs_all, bins=5)
    # plot_thumbstick_heatmap(experiment_logs_all, bins=5)

    # 3. Remove
    # run_multivariate_joystick_analysis(experiment_logs_all, n_permutations=999)

    # 4. Self evaluation
    # print_extreme_participants(perception_results_all, experiment_logs_all, demographics_path)
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
    # plot_self_perc_success_vs_performance_correlations(perception_results_all, experiment_logs_all, df_questionnaire_final, color_palette)

    # plot_questionnaire_results(df_questionnaire_final, color_code='#99DDFF')

    # plot_unified_performance_correlations(perception_results_all, experiment_logs_all, df_questionnaire_final, color_palette)
    return None
def demographic():
    # check_folder_contents('../s1-s2-j')
    # number_of_subjects_info('../s1-s2-j', 'gender', 'male')

    # plot_tiredness_performance_correlations(demographics, perception_results_all, experiment_logs_all, color_palette)

    # plot_ticklishness_haptic_correlations(demographics, perception_results_all, color_palette)

    # count_gender_by_phase_sequence(demographics)
    return None


if __name__ == "__main__":
    color_palette = {
        'visual': '#8cc5e3',
        'auditory': '#b5d1ae',
        'haptic': '#ffbb6f',
        'total': '#2205d1',
        'collision': '#8a754d',
        'male': '#525EFF',
        'female': '#C052FF',
        'easy': '#AEFF52',
        'medium': '#FFE252',
        'hard': '#FF5252',
    }

    data_path = '../Dataset/Dataset/Recordings'
    demographics_path = '../Dataset/Dataset/Metadata/Demographics.csv'
    participants_to_remove = ['39', '53', '24', '03']

    perception_results_all = get_perception_results_df(data_path, participants_to_remove)
    experiment_logs_all = get_experiment_logs_df(data_path, participants_to_remove)
    df_questionnaire_final = pd.read_csv('../Dataset/Dataset/Questionnaire/final.csv')
    df_questionnaire_mid = pd.read_csv('../Dataset/Dataset/Questionnaire/mid.csv')
    demographics = pd.read_csv(demographics_path)
    error_results, error_distribution = compute_error_by_modality(perception_results_all)

    # results_modality()
    # results_difficulty()
    # results_modality_difficulty()
    # results_gender()
    # results_questionnaire()
    # results_questionnaire_modality()
    # results_others()

    # questionnaire()
    # demographic()
