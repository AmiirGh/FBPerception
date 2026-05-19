from utils import *





def clean(folder_dir, subject_namee):
    setup_misses = pd.read_excel('setup misses.xlsx')
    for i, subject in subjects.iterrows():
        subject_name = subject['Subject']
        subject_setup_misses = setup_misses.loc[setup_misses['Subject'] == subject_name].iloc[0, 1]

        if subject_name != subject_namee:
            continue
        print(f'Cleaning {subject_name}')
        df_subject_full = pd.read_csv(os.path.join(folder_dir, subject['Subject'], f'received_data_{subject_name}.csv'))

        df_trials = extract_dynamic_obstacle_trials(df_subject_full)
        df_trials = create_relative_stamps(df_trials, df_subject_full)

        for phase in range(1, 4):

            voice_delay = subject[f'p{phase}']
            file_path = f'{folder_dir}/{subject_name}/audio_{subject_name}_{phase}_full.json'

            text_arr, voice = load_and_process(file_path)

            full_text_arr = merge_tokens_to_text(text_arr, voice['tokens'])

            precived_values = extract_degree_levels(full_text_arr, degrees_dict, levels_dict)

            df_trials = append_voice_stamps(df_trials, precived_values, voice_delay, phase, subject_name)

            df_trials = add_setup_misses(df_trials, subject_setup_misses)

            # df_trials = add column with

            st = f'{folder_dir}/{subject_name}/{subject_name}_cleaned.xlsx'
            df_trials.to_excel(st)
        print('Subject misses: ', len(df_trials[df_trials['degree_perceived'] == 0]))
        print('Setup misses: ', len(df_trials[df_trials['degree_perceived'] == -1]))

        print("\n===================================================\n")



def remove_all_cleaned_from(list, dir):
    for s in list:
        try:
            d = f'../{dir}/{s}/{s}_cleaned.xlsx'
            os.remove(d)
        except:
            pass


if __name__ == '__main__':
    delays = pd.read_excel('audio delays.xlsx')
    subjects = delays.loc[0:54]

    for index in subjects.index:
        subject_name = subjects.loc[index, 'Subject']
        subject_file = f'test128_{subject_name}.csv'
        subjects.loc[index, 'file_name'] = subject_file

    s1_j_c1 = []

    s1_s2_j = []

    # subjects that are cleaned and manually verified
    cleaned_subjects = ['AliFartoot_2080', 'Alireza_9044', 'Arya_3561', 'Bita_2861', 'Diba_8191', 'Erfan_3914',
                        'Faezeh_3703', 'Ghazal_5424', 'Ghazal_8825', 'Kamyar_564', 'Mana_2933', 'Sina_678',
                        'Alireza_45', 'AmirGh_9738', 'Arezoo_8327', 'Ehsan_9637', 'FatemehSh_9953', 'Arshia_9647',
                        'Ghazal_7107', 'MArian_1967', 'Mehrnoosh_7150', 'Paniz_762', 'saghar_9096', 'Sajjad_2730',
                        'Salar_3600', 'Tohid_5715', 'Zahra_6890', 'Diba_9193', 'Amirreza_6433', 'Amir_7295',
                        'Amirhossein_9951', 'Yegane_2669', 'Matin_1453', 'Navid_4966', 'Saba_2541', 'Tina_4890',
                        'Alireza_4326', 'Ebram_9796', 'MohammadHossein_7311', 'Mehrsa_8611', 'Shahla_6430',
                        'Hossein_8754', 'MohammadMash_317', 'Zahra_3701', 'Sepideh_6913', 'Yegane_5688', 'Saber_1648',
                        'Samar_1783',  'Shahab_2645', 'Hossein_1501', 'Asra_9174', 'Asal_6565', 'Fatemeh_5992',
                        'Yas_4358']

    not_cleaned_subjects = []
    single_subject_mode = []

    # remove_all_cleaned_from(s1_j_c1, 's1-j-c1')
    # remove_all_cleaned_from(cleaned_subjects, 's1-s2-j')

    i = 0
    for s in single_subject_mode:
        clean(folder_dir='../s1-s2-j', subject_namee=s)
        i += 1


    print(f'from {len(cleaned_subjects)} subjects, cleaned {i}')
    print(f'Remaining {len(not_cleaned_subjects)} subjects')


