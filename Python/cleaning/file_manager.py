from utils_file_manager import *


recording_directory = '../Dataset/Recordings'
questionnaire_directory = '../Dataset/Questionnaire'

output_dir = Path("../Dataset/Recordings_csv")
output_directory_path = './xlsx_csv_json_files_only'
if __name__ == "__main__":
    # excel_to_csv(directory_path, output_dir)
    # find_problematic_recordings(directory_path)
    # remove_specific_spreadsheets(directory_path, dry_run=True)
    # filter_and_copy_spreadsheets(recording_directory, output_directory_path)
    anonymize_folders(recording_directory, questionnaire_directory)

    rename_and_remove_columns_rows(recording_directory, questionnaire_directory)

    pass