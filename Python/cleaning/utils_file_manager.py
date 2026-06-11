import pandas as pd

from utils import *
import uuid
# 1. Define paths


def excel_to_csv(source_dir, output_dir): # reformats all xlsx files to csv
    if not source_dir.exists():
        print(f"Error: The directory {source_dir} does not exist.")
        exit()

    # 2. Find all .xlsx files in all subfolders using rglob (recursive glob)
    excel_files = list(source_dir.rglob("*.xlsx"))

    if not excel_files:
        print(f"No .xlsx files found in {source_dir}")
    else:
        print(f"Found {len(excel_files)} Excel files. Starting conversion...\n")

    # 3. Loop through and convert each file
    for excel_file in excel_files:
        # Ignore hidden/temporary excel files (which usually start with '~$')
        if excel_file.name.startswith("~$"):
            continue

        # Get the relative path of the folder (e.g., "folderA/subfolderB")
        relative_folder = excel_file.parent.relative_to(source_dir)

        # Create the corresponding target folder in the new output directory
        target_folder = output_dir / relative_folder
        target_folder.mkdir(parents=True, exist_ok=True)

        # Define the target CSV file path
        csv_file_path = target_folder / f"{excel_file.stem}.csv"

        try:
            # Read the Excel file (reads the first sheet by default)
            df = pd.read_excel(excel_file)

            # Save as CSV without the index column
            df.to_csv(csv_file_path, index=False)

            print(f"✅ Converted: {relative_folder}/{excel_file.name}")

        except Exception as e:
            print(f"❌ Error converting {excel_file.name}: {e}")

    print("\nAll done!")


def find_problematic_recordings(base_path):
    for folder in os.listdir(base_path):
        folder_path = os.path.join(base_path, folder)

        if not os.path.isdir(folder_path):
            continue

        subject_id = folder

        expected_files = {
            f"received_data_{subject_id}.csv",
            "subject_info.xlsx",
            f"{subject_id}_cleaned.xlsx",
            f"audio_{subject_id}_1.wav",
            f"audio_{subject_id}_2.wav",
            f"audio_{subject_id}_3.wav",
            f"audio_{subject_id}_1_full.json",
            f"audio_{subject_id}_2_full.json",
            f"audio_{subject_id}_3_full.json",
        }

        actual_files = {
            f for f in os.listdir(folder_path)
            if os.path.isfile(os.path.join(folder_path, f))
        }

        missing_files = expected_files - actual_files
        extra_files = actual_files - expected_files

        if missing_files or extra_files:
            print(f"\nFolder with issues: {folder}")

            if missing_files:
                print("  Missing files:")
                for f in sorted(missing_files):
                    print(f"    {f}")

            if extra_files:
                print("  Unexpected files:")
                for f in sorted(extra_files):
                    print(f"    {f}")


def filter_and_copy_spreadsheets(input_dir, output_dir):
    """
    Finds all .csv and .xlsx files in the input_dir and copies them to output_dir
    while preserving the original folder structure.
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    # Ensure the main output directory exists
    output_path.mkdir(parents=True, exist_ok=True)

    # Use rglob to recursively find all .csv and .xlsx files
    for ext in ('*.csv', '*.xlsx', '*.json'):
        for file_path in input_path.rglob(ext):
            if file_path.is_file():
                # Get the relative path (e.g., 'FolderA/data.csv')
                relative_path = file_path.relative_to(input_path)

                # Construct the full target path
                target_file_path = output_path / relative_path

                # Create the parent directory in the output location if it doesn't exist
                target_file_path.parent.mkdir(parents=True, exist_ok=True)

                # Copy the file (shutil.copy2 preserves file metadata like creation date)
                shutil.copy2(file_path, target_file_path)
                print(f"Copied: {relative_path}")


def remove_specific_spreadsheets(directory_path, dry_run=True):
    """
    Finds and removes .csv and .xlsx files in the directory if they
    start with 'test128' or contain 'Copy'.
    """
    input_path = Path(directory_path)

    # Ensure the directory actually exists before running
    if not input_path.exists():
        print(f"Error: The directory {directory_path} does not exist.")
        return

    removed_count = 0

    # Recursively find all .csv and .xlsx files
    for ext in ('*.csv', '*.xlsx'):
        for file_path in input_path.rglob(ext):
            if file_path.is_file():
                file_name = file_path.name

                # --- DELETION LOGIC ---
                if file_name.startswith('test128') or 'Copy' in file_name:
                    if dry_run:
                        # Safety mode: just tell us what WOULD happen
                        print(f"[DRY RUN] Would delete: {file_path}")
                    else:
                        # Danger zone: actually delete the file
                        file_path.unlink()
                        print(f"Deleted: {file_path}")

                    removed_count += 1

    # Print a summary
    if dry_run:
        print(f"\nDry run complete. {removed_count} files WOULD be deleted.")
        print("To actually delete these files, change 'dry_run=False' in your code.")
    else:
        print(f"\nCleanup complete. {removed_count} files were deleted permanently.")


def anonymize_folders(recording_directory, questionnaire_directory, seed=42):

    # -------------------------
    # Get folders
    # -------------------------
    folders = [f for f in os.listdir(recording_directory)
               if os.path.isdir(os.path.join(recording_directory, f))]

    # -------------------------
    # Shuffle + mapping
    # -------------------------
    random.seed(seed)
    shuffled = folders.copy()
    random.shuffle(shuffled)

    width = max(2, len(str(len(shuffled))))

    id_mapping = {old_id: str(i + 1).zfill(width)
        for i, old_id in enumerate(shuffled)}

    print("Mapping (old -> new):")
    for k, v in id_mapping.items():
        print(k, "->", v)

    # -------------------------
    # Rename files inside folders
    # -------------------------
    for old_id, new_id in id_mapping.items():

        folder_path = os.path.join(recording_directory, old_id)

        # Safety check in case the folder doesn't exist
        if not os.path.exists(folder_path):
            continue

        for filename in os.listdir(folder_path):

            old_file_path = os.path.join(folder_path, filename)

            if not os.path.isfile(old_file_path):
                continue

            if old_id in filename:
                # Define the exact prefix we want to remove for the special files
                audio_prefix = f"audio_{old_id}_"

                # Check if it's one of your special audio/json files
                if filename.startswith(audio_prefix) and (filename.endswith(".wav") or filename.endswith(".json")):
                    # This removes "audio_old_id_" entirely AND removes "_full"
                    new_filename = filename.replace(audio_prefix, "").replace("_full", "")
                else:
                    # Default behavior for all other files
                    new_filename = filename.replace(old_id, new_id)

                new_file_path = os.path.join(folder_path, new_filename)
                os.rename(old_file_path, new_file_path)

    # -------------------------
    # Rename folders safely (two-step)
    # -------------------------
    temp_names = {}

    for old_id in id_mapping:
        old_path = os.path.join(recording_directory, old_id)
        temp_path = os.path.join(recording_directory, "__tmp__" + old_id)
        os.rename(old_path, temp_path)
        temp_names[old_id] = temp_path

    for old_id, new_id in id_mapping.items():
        temp_path = temp_names[old_id]
        new_path = os.path.join(recording_directory, new_id)
        os.rename(temp_path, new_path)

    # -------------------------
    # Update questionnaire files
    # -------------------------
    for file_name in ["mid.xlsx", "final.xlsx"]:

        file_path = os.path.join(questionnaire_directory, file_name)
        df = pd.read_excel(file_path)
        col = "4 رقم آخر شماره موبایل:"

        # Build mapping using numeric ID extracted from folder name
        numeric_id_to_new = {}

        for old_folder_name, new_id in id_mapping.items():
            try:
                numeric_id = old_folder_name.split("_")[-1]
                numeric_id_to_new[int(numeric_id)] = new_id
            except:
                continue

        def map_id(x):
            try:
                return numeric_id_to_new.get(int(x), x)
            except:
                return x

        df[col] = df[col].apply(map_id)

        output_path = os.path.join(questionnaire_directory, file_name.replace(".xlsx", "_new.xlsx"))

        df.to_excel(output_path, index=False)
        print(f"Saved: {output_path}")

    mapping_df = pd.DataFrame([{"old_id": old_id,"new_id": new_id} for old_id, new_id in id_mapping.items()])

    mapping_path = os.path.join(questionnaire_directory, "id_mapping.xlsx")
    mapping_df.to_excel(mapping_path, index=False)

    print(f"Mapping saved to: {mapping_path}")
    return id_mapping


def process_recording_files(
    recording_directory,
    trials_new_name, rec_data_new_name, sub_info_new_name,
    cols_to_remove_1, cols_to_remove_2, rows_to_remove_sub_info):

    for folder in os.listdir(recording_directory):
        folder_path = os.path.join(recording_directory, folder)

        if not os.path.isdir(folder_path):
            continue

        subject_id = folder

        # -------------------------
        # FILE 1: id_cleaned.xlsx
        # -------------------------
        file1 = os.path.join(folder_path, f"{subject_id}_cleaned.xlsx")
        if os.path.exists(file1):

            df1 = pd.read_excel(file1)
            df1 = df1.drop(columns=cols_to_remove_1, errors="ignore")

            new_file1 = os.path.join(folder_path, f"{trials_new_name}.xlsx")
            df1.to_excel(new_file1, index=False)

            os.remove(file1)

        # -------------------------
        # FILE 2: recieved_data_id.csv
        # -------------------------
        file2 = os.path.join(folder_path, f"received_data_{subject_id}.csv")
        if os.path.exists(file2):

            df2 = pd.read_csv(file2)
            df2 = df2.drop(columns=cols_to_remove_2, errors="ignore")

            new_file2 = os.path.join(folder_path, f"{rec_data_new_name}.csv")
            df2.to_csv(new_file2, index=False)

            os.remove(file2)

            # -------------------------
            # FILE 3: subject_info.xlsx (ROW REMOVAL LOGIC FIXED)
            # -------------------------
            file3 = os.path.join(folder_path, "subject_info.xlsx")
            if os.path.exists(file3):

                df3 = pd.read_excel(file3)

                if "Subject_Info" in df3.columns:
                    df3 = df3[~df3["Subject_Info"].isin(rows_to_remove_sub_info)]

                new_file3 = os.path.join(folder_path, f"{sub_info_new_name}.xlsx")
                df3.to_excel(new_file3, index=False)

                os.remove(file3)


def rename_dataset_labels(
        recording_directory,
        trials_file_name,
        rec_data_file_name,
        sub_info_file_name,
        cols_to_rename_raw_exp_logs_old, cols_to_rename_raw_exp_logs_new,
        cols_to_rename_perception_results_old, cols_to_rename_perception_results_new,
        rows_to_rename_raw_demographics_old, rows_to_rename_raw_demographics_new
):
    # Convert the parallel lists into dictionary mappings for Pandas
    raw_exp_map = dict(zip(cols_to_rename_raw_exp_logs_old, cols_to_rename_raw_exp_logs_new))
    perception_map = dict(zip(cols_to_rename_perception_results_old, cols_to_rename_perception_results_new))
    demographics_row_map = dict(zip(rows_to_rename_raw_demographics_old, rows_to_rename_raw_demographics_new))

    # Difficulty mapping (accounting for both float and string types just in case)
    difficulty_mapping = {
        0.05: 'easy',
        0.075: 'medium',
        0.1: 'hard',
        '0.05': 'easy',
        '0.075': 'medium',
        '0.1': 'hard'
    }

    for folder in os.listdir(recording_directory):
        folder_path = os.path.join(recording_directory, folder)

        if not os.path.isdir(folder_path):
            continue

        # -------------------------
        # FILE 1: Perception Results (Column Rename & Difficulty Map)
        # -------------------------
        file1 = os.path.join(folder_path, f"{trials_file_name}.xlsx")
        if os.path.exists(file1):
            df1 = pd.read_excel(file1)

            # Rename the columns
            df1 = df1.rename(columns=perception_map)

            # Replace Difficulty values
            for col in ["Difficulty"]:
                if col in df1.columns:
                    df1[col] = df1[col].replace(difficulty_mapping)

            df1.to_excel(file1, index=False)

        # -------------------------
        # FILE 2: Raw Experimental Logs (Column Rename & Difficulty Map)
        # -------------------------
        file2 = os.path.join(folder_path, f"{rec_data_file_name}.csv")
        if os.path.exists(file2):
            df2 = pd.read_csv(file2)

            # Rename the columns
            df2 = df2.rename(columns=raw_exp_map)

            # Replace Difficulty values
            for col in ["Difficulty"]:
                if col in df2.columns:
                    df2[col] = df2[col].replace(difficulty_mapping)

            df2.to_csv(file2, index=False)

        # -------------------------
        # FILE 3: Subject Info / Demographics (Row Value Rename)
        # -------------------------
        file3 = os.path.join(folder_path, f"{sub_info_file_name}.xlsx")
        if os.path.exists(file3):
            df3 = pd.read_excel(file3)

            # 1. Rename the column from "Subject_Info" to "Info"
            df3 = df3.rename(columns={"Subject_Info": "Info"})

            # 2. Process the newly named "Info" column
            if "Info" in df3.columns:
                # Replace the specific row values (e.g., 'Dobini' -> 'Diplopia')
                df3["Info"] = df3["Info"].replace(demographics_row_map)

                # Capitalize the first word (and makes the rest lowercase)
                # e.g., "age of subject" -> "Age of subject"
                df3["Info"] = df3["Info"].str.capitalize()

            df3.to_excel(file3, index=False)


def change_format_xlsx_to_csv(root_directory):
    """
    Recursively searches for .xlsx files in the given directory and its subfolders,
    converts them to .csv, and deletes the original .xlsx files.
    """
    # os.walk goes through the root directory and all sub-directories
    for dirpath, _, filenames in os.walk(root_directory):
        for filename in filenames:

            # Find .xlsx files (and ignore temporary Excel files that start with ~$)
            if filename.endswith(".xlsx") and not filename.startswith("~$"):

                # Get the full path to the old Excel file
                xlsx_path = os.path.join(dirpath, filename)

                # Create the new CSV file path
                csv_filename = filename.replace(".xlsx", ".csv")
                csv_path = os.path.join(dirpath, csv_filename)

                try:
                    # 1. Read the Excel file
                    df = pd.read_excel(xlsx_path)

                    # 2. Save it as a CSV (index=False prevents pandas from adding row numbers)
                    df.to_csv(csv_path, index=False)
                    print(f"✅ Converted: {filename} -> {csv_filename}")

                    # 3. Delete the original .xlsx file
                    os.remove(xlsx_path)
                    print(f"🗑️ Deleted original: {filename}")

                except Exception as e:
                    print(f"❌ Error processing {xlsx_path}: {e}")


def remove_cols_ques_mid_final(questionnaire_directory, cols_to_remove_que_mid, cols_to_remove_que_final):
    # Construct the exact file paths for the Excel files
    mid_path = os.path.join(questionnaire_directory, 'mid_new.xlsx')
    final_path = os.path.join(questionnaire_directory, 'final_new.xlsx')

    # -------------------------
    # 1. Process mid_new.xlsx
    # -------------------------
    if os.path.exists(mid_path):
        try:
            # Read the Excel file
            df_mid = pd.read_excel(mid_path)

            # Drop the columns (errors='ignore' prevents crashes if already removed)
            df_mid = df_mid.drop(columns=cols_to_remove_que_mid, errors='ignore')

            # Overwrite the original Excel file
            df_mid.to_excel(mid_path, index=False)
            print(f"✅ Successfully removed columns and updated: {mid_path}")

        except Exception as e:
            print(f"❌ Error processing {mid_path}: {e}")
    else:
        print(f"⚠️ File not found: {mid_path}")

    # -------------------------
    # 2. Process final_new.xlsx
    # -------------------------
    if os.path.exists(final_path):
        try:
            # Read the Excel file
            df_final = pd.read_excel(final_path)

            # Drop the columns
            df_final = df_final.drop(columns=cols_to_remove_que_final, errors='ignore')

            # Overwrite the original Excel file
            df_final.to_excel(final_path, index=False)
            print(f"✅ Successfully removed columns and updated: {final_path}")

        except Exception as e:
            print(f"❌ Error processing {final_path}: {e}")
    else:
        print(f"⚠️ File not found: {final_path}")


def process_final_questionnaire(questionnaire_directory):
    file_path = os.path.join(questionnaire_directory, 'final_new.xlsx')
    try:
        # 1. Load the dataset
        df = pd.read_excel(file_path)

        # 2. Rename the columns
        new_column_names = ['Participant ID'] + [f'Q{i}' for i in range(1, 17)]

        if len(df.columns) == len(new_column_names):
            df.columns = new_column_names
        else:
            print(f"Warning: Expected 17 columns, but found {len(df.columns)}.")
            return

        # 3. Map the specific answers in Q9 to English
        q9_mapping = {
            "هر دو به یک اندازه": "both",
            "اجتناب از برخورد با موانع": "avoidance",
            "تشخیص مکان جسم": "cue localization"
        }
        df['Q9'] = df['Q9'].replace(q9_mapping)

        # 4. Sort the rows based on the 'Participant ID'
        df = df.sort_values(by='Participant ID', ascending=True)

        # 5. Save exactly as 'final.csv' and delete the old Excel file
        csv_file_path = os.path.join(questionnaire_directory, 'final.csv')
        df.to_csv(csv_file_path, index=False, encoding='utf-8-sig')

        # Remove the intermediate .xlsx file
        os.remove(file_path)

        print(f"✅ Successfully processed and saved as: {csv_file_path}")

    except Exception as e:
        print(f"❌ Error processing the file: {e}")


def process_mid_questionnaire(questionnaire_directory):
    file_path = os.path.join(questionnaire_directory, 'mid_new.xlsx')
    try:
        # 1. Load the dataset
        df = pd.read_excel(file_path)

        # 2. Rename the columns dynamically
        new_columns = ['Participant ID']

        for part in range(1, 4):
            for q in range(1, 10):
                new_columns.append(f'Q{q}.{part}')

        if len(df.columns) == len(new_columns):
            df.columns = new_columns
        else:
            print(f"Warning: Expected {len(new_columns)} columns, but found {len(df.columns)}.")
            return

        # 3. Create a helper function to map the modalities while preserving order
        def map_modalities(text):
            if not isinstance(text, str):
                return text

            mapping = {
                'صوتی': 'a',
                'تصویری': 'v',
                'لرزشی': 'h'
            }

            parts = [p.strip() for p in text.replace('،', ',').split(',')]
            mapped_parts = [mapping.get(p, p) for p in parts]
            return ','.join(mapped_parts)

        # Apply the helper function only to the specific columns
        for col in ['Q3.1', 'Q3.2', 'Q3.3']:
            if col in df.columns:
                df[col] = df[col].apply(map_modalities)

        # 4. Sort the rows based on the 'Participant ID'
        df = df.sort_values(by='Participant ID', ascending=True)

        # 5. Save exactly as 'mid.csv' and delete the old Excel file
        csv_file_path = os.path.join(questionnaire_directory, 'mid.csv')
        df.to_csv(csv_file_path, index=False, encoding='utf-8-sig')

        # Remove the intermediate .xlsx file
        os.remove(file_path)

        print(f"✅ Successfully processed, mapped, and saved as: {csv_file_path}")

    except Exception as e:
        print(f"❌ Error processing the file: {e}")

def remove_nondominant_ind_but_col(recording_directory):
    # Iterate through all folders in the recording directory
    for folder_name in os.listdir(recording_directory):
        folder_path = os.path.join(recording_directory, folder_name)

        # Ensure we are only looking inside directories (like '01', '02', etc.)
        if not os.path.isdir(folder_path):
            continue

        demographics_path = os.path.join(folder_path, "Demographics.csv")
        logs_path = os.path.join(folder_path, "Experiment logs.csv")

        # Skip this folder if it's missing either of the required files
        if not (os.path.exists(demographics_path) and os.path.exists(logs_path)):
            continue

        try:
            # 1. Read Demographics to find Handedness
            df_demo = pd.read_csv(demographics_path, header=None)
            handedness = None

            # Search row by row for 'handness'
            for index, row in df_demo.iterrows():
                row_str = row.astype(str).str.lower()

                if row_str.str.contains('handness').any():
                    if row_str.str.contains('right').any():
                        handedness = 'right'
                        break
                    elif row_str.str.contains('left').any():
                        handedness = 'left'
                        break

            if not handedness:
                print(f"⚠️ {folder_name}: Could not determine handedness.")
                continue

            # 2. Read Raw experiment logs
            df_logs = pd.read_csv(logs_path)
            # =========================================================
            # NEW: Set Angle and Distance to 0 if Modality is "-"
            # =========================================================
            zeroed_modality = False
            # Check that the necessary columns exist before trying to modify them
            if all(col in df_logs.columns for col in ['Modality', 'Angle', 'Distance']):
                # Create a boolean mask identifying rows where Modality is strictly "-"
                mask = df_logs['Modality'] == '-'

                if mask.any():
                    # Use .loc to efficiently overwrite only those specific rows with 0
                    df_logs.loc[mask, ['Angle', 'Distance']] = 0
                    zeroed_modality = True
            # Determine which column to REMOVE and which to RENAME
            col_to_remove = "Left index but" if handedness == 'right' else "Right index but"
            col_to_keep = "Right index but" if handedness == 'right' else "Left index but"

            # 3. Drop the non-dominant column
            if col_to_remove in df_logs.columns:
                df_logs = df_logs.drop(columns=[col_to_remove])
                removed = True
            else:
                removed = False

            # 4. Rename the dominant column to "Index button"
            if col_to_keep in df_logs.columns:
                df_logs = df_logs.rename(columns={col_to_keep: "Index button"})
                renamed = True
            else:
                renamed = False

            # 5. Overwrite the original file with the updated dataframe
            if removed or renamed:
                df_logs.to_csv(logs_path, index=False)
                print(
                    f"✅ {folder_name}: {handedness.capitalize()}-handed. Removed '{col_to_remove}' & Renamed '{col_to_keep}' to 'Index button'.")
            else:
                print(f"ℹ️ {folder_name}: No changes made (columns not found).")

        except Exception as e:
            print(f"❌ Error processing folder {folder_name}: {e}")


def merge_raw_perception(recording_directory):
    # Iterate through all folders in the recording directory
    for folder_name in os.listdir(recording_directory):
        folder_path = os.path.join(recording_directory, folder_name)

        # Ensure we are only looking inside directories
        if not os.path.isdir(folder_path):
            continue

        raw_path = os.path.join(folder_path, "Experiment logs.csv")
        perc_path = os.path.join(folder_path, "Perception results.csv")

        # Skip if either file is missing
        if not (os.path.exists(raw_path) and os.path.exists(perc_path)):
            continue

        try:
            # ==========================================
            # 1. LOAD DATA
            # ==========================================
            df_raw = pd.read_csv(raw_path)
            df_perc = pd.read_csv(perc_path)

            # ==========================================
            # 2. UPDATE PERCEPTION RESULTS (Move 'Difficulty')
            # ==========================================
            if 'Difficulty' in df_perc.columns:
                # Get all columns except 'Difficulty'
                cols = [col for col in df_perc.columns if col != 'Difficulty']
                # Append 'Difficulty' to the end
                cols.append('Difficulty')
                # Reorder and overwrite
                df_perc = df_perc[cols]
                df_perc.to_csv(perc_path, index=False)
                print(f"🔄 {folder_name}: Moved 'Difficulty' to the last column in Perception results.")

            # ==========================================
            # 3. MERGE INTO RAW LOGS
            # ==========================================
            # Select the 5 necessary columns from perception data
            perc_subset = df_perc[[
                'Trial number',
                'Angle perceived',
                'Distance perceived',
                'Phase timestamp',
                'Response start',
                'Response end'
            ]]

            # Merge these values into the raw logs based on 'Trial number'
            df_merged = df_raw.merge(perc_subset, on='Trial number', how='left')

            # Fill any NaNs resulting from missing trials with 0 temporarily
            target_columns = ['Angle perceived', 'Distance perceived', 'Phase timestamp', 'Response start',
                              'Response end']
            df_merged[target_columns] = df_merged[target_columns].fillna(0)

            # ==========================================
            # 4. FIND THE "TRIGGER" ROW
            # ==========================================
            # Create a boolean mask for rows where Modality is NOT 0
            nonzero_modality_mask = df_merged['Modality'] != '-'

            # Find the exact index of the FIRST occurrence of a non-zero modality for each trial
            # drop_duplicates keeps the first occurrence by default
            trigger_indices = df_merged[nonzero_modality_mask].drop_duplicates(subset=['Trial number']).index

            # Create a mask checking if the current row index is one of our trigger indices
            is_trigger = df_merged.index.isin(trigger_indices)

            # ==========================================
            # 5. APPLY THE LOGIC (Keep values only on trigger row, else 0)
            # ==========================================
            for col in target_columns:
                df_merged[col] = np.where(is_trigger, df_merged[col], 0)

            # ==========================================
            # 6. REORDER THE COLUMNS
            # ==========================================
            # Define the exact leading columns
            leading_columns = [
                'Timestamp',  # 1st
                'Trial number',  # 2nd
                'Modality',  # 3rd
                'Angle',  # 4th
                'Distance',  # 5th
                'Angle perceived',  # 6th
                'Distance perceived',  # 7th
                'Phase timestamp',  # 8th
                'Response start',  # 9th
                'Response end'  # 10th
            ]

            # Automatically grab all remaining columns that aren't in our list above
            remaining_columns = [col for col in df_merged.columns if col not in leading_columns]

            # Combine them to create the final column layout
            final_column_order = leading_columns + remaining_columns

            # Apply the new order to the dataframe
            df_merged = df_merged[final_column_order]

            # ==========================================
            # 7. SAVE THE FILE
            # ==========================================
            # Overwrite the original Raw logs file with the new order
            df_merged.to_csv(raw_path, index=False)
            print(f"✅ {folder_name}: Successfully formatted Experiment logs.")

        except Exception as e:
            print(f"❌ Error processing folder {folder_name}: {e}")


def rename_values(recording_directory):
    # This function replaces '-' with 0 and 'audio' to 'auditory' in the Modality column,
    # clears the Collision position appropriately, and reorders the Perception results columns.
    for folder_name in os.listdir(recording_directory):
        folder_path = os.path.join(recording_directory, folder_name)

        if not os.path.isdir(folder_path):
            continue

        raw_path = os.path.join(folder_path, "Experiment logs.csv")
        perc_path = os.path.join(folder_path, "Perception results.csv")

        # ---------------------------------------------------------
        # 1. Process Experiment logs.csv
        # ---------------------------------------------------------
        if os.path.exists(raw_path):
            try:
                # Note: if you are using the master script, change pd.read_csv to safe_read_csv
                df = pd.read_csv(raw_path)

                # Change Modality '-' to 0 and 'audio' to 'auditory'
                if 'Modality' in df.columns:
                    df['Modality'] = df['Modality'].replace('-', 0)
                    df['Modality'] = df['Modality'].replace('audio', 'auditory')

                # Filter Collision position
                if 'Number of collision' in df.columns and 'Collision position' in df.columns:
                    is_new_collision = df['Number of collision'].diff().fillna(0) > 0
                    df['Collision position'] = np.where(is_new_collision, df['Collision position'], "0")

                # Overwrite the original file
                df.to_csv(raw_path, index=False)
                print(f"✅ {folder_name}: Updated Modality and cleaned up Collision positions in Experiment logs.")

            except Exception as e:
                print(f"❌ Error processing Experiment logs for folder {folder_name}: {e}")

        # ---------------------------------------------------------
        # 2. Process Perception results.csv
        # ---------------------------------------------------------
        if os.path.exists(perc_path):
            try:
                df_perc = pd.read_csv(perc_path)

                # Change 'audio' to 'auditory'
                if 'Modality' in df_perc.columns:
                    df_perc['Modality'] = df_perc['Modality'].replace('audio', 'auditory')

                # REORDER COLUMNS
                # Define the exact leading columns as requested (Assuming Timestamp & Trial number are 1st and 2nd)
                leading_columns = [
                    'Timestamp',  # 1st
                    'Trial number',  # 2nd
                    'Modality',  # 3rd
                    'Angle',  # 4th
                    'Distance',  # 5th
                    'Angle perceived',  # 6th
                    'Distance perceived'  # 7th
                ]

                # Check which leading columns actually exist to prevent errors
                actual_leading = [col for col in leading_columns if col in df_perc.columns]

                # Gather all other columns that aren't in the specific list above
                remaining_columns = [col for col in df_perc.columns if col not in actual_leading]

                # Apply the new order
                df_perc = df_perc[actual_leading + remaining_columns]

                # Overwrite the original file
                df_perc.to_csv(perc_path, index=False)
                print(f"✅ {folder_name}: Updated Modality and reordered columns in Perception results.")

            except Exception as e:
                print(f"❌ Error processing Perception results for folder {folder_name}: {e}")



def merge_demographics(recording_directory):
    # A list to store the single-row dataframes for each participant
    all_demographics = []

    # A list to keep track of the files we want to delete later
    processed_files = []

    # Iterate through all folders in the recording directory
    for folder_name in os.listdir(recording_directory):
        folder_path = os.path.join(recording_directory, folder_name)

        # Ensure we are only looking inside directories
        if not os.path.isdir(folder_path):
            continue

        demo_path = os.path.join(folder_path, "Demographics.csv")

        # Skip if the Demographics file is missing
        if not os.path.exists(demo_path):
            continue

        try:
            # 1. Read the vertical Demographics file
            df = pd.read_csv(demo_path)

            # Standardize strings to avoid hidden spaces messing up column names
            if 'Info' in df.columns:
                df['Info'] = df['Info'].astype(str).str.strip()

            # 2. Transpose the data (flip rows into columns)
            df_transposed = df.set_index('Info').T

            # 3. Add the Participant ID (the folder name) as the very first column
            df_transposed.insert(0, 'Participant ID', folder_name)

            # Clean up the index so it doesn't say "Value" on the left side
            df_transposed = df_transposed.reset_index(drop=True)

            # 4. Add this participant's row to our master list
            all_demographics.append(df_transposed)

            # Record the path so we can delete it later
            processed_files.append(demo_path)

        except Exception as e:
            print(f"❌ Error processing folder {folder_name}: {e}")

    # 5. Combine all participants into one massive dataset and save it
    if all_demographics:
        merged_df = pd.concat(all_demographics, ignore_index=True)


        # Save directly inside the Setup files directory
        output_file = os.path.join(recording_directory, '../Setup files/Demographics all.csv')

        try:
            merged_df.to_csv(output_file, index=False)
            print(f"✅ Successfully merged all demographics into: {output_file}")

            # 6. Safely remove the original files NOW that the backup is saved
            for file_path in processed_files:
                os.remove(file_path)
            print(f"🗑️ Cleaned up {len(processed_files)} original Demographics.csv files.")

        except Exception as e:
            print(f"❌ Failed to save the merged file: {e}\n⚠️ Original files were NOT deleted.")

    else:
        print("⚠️ No valid Demographics files were found to merge.")


def update_demographics_values(recording_directory):
    # Construct the exact path to the merged Demographics file
    file_path = os.path.join(recording_directory, '../Setup files/Demographics all.csv')

    # Safety check: make sure the file actually exists before trying to open it
    if not os.path.exists(file_path):
        print(f"⚠️ File not found: {file_path}")
        return

    try:
        # 1. Load the dataset
        df = pd.read_csv(file_path)

        rename_dict = {
            "Which sense is superior": "Superior sense",
            "Sleepness - tiredness (1-5)": "Tiredness",
            "How often do you play joystick games(h per month)": "How much do you play joystick games per month",
            "Experience in using vr": "Experience in using VR",
            "Cybersickness": "Experience of motion sickness"
        }
        df = df.rename(columns=rename_dict)

        # 2. Convert 'Superior sence' to lowercase and map 'audio' -> 'auditory'

        df['Superior sense'] = df['Superior sense'].astype(str).str.lower()
        df['Superior sense'] = df['Superior sense'].replace(['audio', 'Audio'], 'auditory')
        df['Superior sense'] = df['Superior sense'].replace(['Visual'], 'visual')
        df['Handness'] = df['Handness'].replace(['Right'], 'right')


        # 3. Map the 'Experiment type' values
        if 'Experiment type' in df.columns:
            exp_mapping = {
                1: 'easy, medium, hard', '1': 'easy, medium, hard',
                2: 'medium, easy, hard', '2': 'medium, easy, hard',
                3: 'hard, medium, easy', '3': 'hard, medium, easy',
                4: 'easy, hard, medium', '4': 'easy, hard, medium',
                5: 'medium, hard, easy', '5': 'medium, hard, easy',
                6: 'hard, easy, medium', '6': 'hard, easy, medium'
            }
            df['Experiment type'] = df['Experiment type'].replace(exp_mapping)

        # 4. Fix the "femal" typo in the Gender column
        if 'Gender' in df.columns:
            # This checks the cell. If it is exactly "femal" (ignoring accidental spaces or caps like "Femal"),
            # it rewrites it as "female". Otherwise, it leaves the cell alone (so "male" or "female" stay perfectly safe).
            df['Gender'] = df['Gender'].apply(
                lambda x: 'female' if isinstance(x, str) and x.strip().lower() == 'femal' else x
            )

        # 5. Convert all "yes" and "no" values to lowercase across the ENTIRE file
        for col in df.columns:
            df[col] = df[col].apply(
                lambda x: x.strip().lower() if isinstance(x, str) and x.strip().lower() in ['yes', 'no'] else x
            )

        # 6. Overwrite the original file with the updated data
        df.to_csv(file_path, index=False)
        print(f"✅ Successfully updated values, fixed 'femal' typo, and lowercased yes/no in: {file_path}")

    except Exception as e:
        print(f"❌ Error processing the file: {e}")


def update_setup_participant_ids():
    audio_sync_offset = '../Dataset/Setup files/Audio sync offsets.xlsx'
    invalidated_trials = '../Dataset/Setup files/Invalidated trials.xlsx'
    new_id_map = '../Dataset/Questionnaire/id_mapping.xlsx'

    # Load mapping
    mapping_df = pd.read_excel(new_id_map)
    id_mapping = dict(zip(mapping_df['old_id'], mapping_df['new_id']))

    # Process Audio sync offsets
    audio_df = pd.read_excel(audio_sync_offset)
    audio_df['Participant ID'] = audio_df['Participant ID'].replace(id_mapping)

    # Sort by Participant ID
    try:
        audio_df = audio_df.sort_values('Participant ID').reset_index(drop=True)
    except Exception as e:
        pass
    audio_df.to_csv('../Dataset/Setup files/Audio sync offsets.csv', index=False)

    # Process Invalidated trials
    invalid_df = pd.read_excel(invalidated_trials)
    invalid_df['Participant ID'] = invalid_df['Participant ID'].replace(id_mapping)

    # Sort by Participant ID
    try:
        invalid_df = invalid_df.sort_values('Participant ID').reset_index(drop=True)
    except Exception as e:
        pass
    invalid_df.to_csv( '../Dataset/Setup files/Invalidated trials.csv', index=False)

    print("CSV files created successfully.")




def rename_and_remove_columns_rows(recording_directory, questionnaire_directory):
    cols_to_remove_perception_results = ['Unnamed: 0', 'index', 'interval_number', 'is_dynamic_obstacle_present',
                                         'right_index_button', 'left_index_button', 'right_thumbstick_x',
                                         'right_thumbstick_y','number_of_collision', 'head_position', 'collision_position',
                                         'head_rotation', 'generation_rate', 'forward_speed', 'dynamic_rise']

    cols_to_remove_exp_logs = ['is_dynamic_obstacle_present', 'generation_rate', 'trial_number','forward_speed']
    rows_to_remove_sub_info = ['name', 'ID']
    #renames the files and remove some columns
    process_recording_files(recording_directory,"Perception results", "Experiment logs", "Demographics",
        cols_to_remove_perception_results, cols_to_remove_exp_logs, rows_to_remove_sub_info)

    cols_to_rename_raw_exp_logs_old = ['timestamp', 'interval_number', 'degree', 'level', 'feedback_modality',
                                       'left_index_button', 'right_index_button', 'right_thumbstick_x', 'right_thumbstick_y',
                                       'number_of_collision',
                                       'head_position', 'head_rotation', 'collision_position', 's_obstacle_gen_on_player_prob']
    cols_to_rename_raw_exp_logs_new = ['Timestamp', 'Trial number', 'Angle', 'Distance', 'Modality',
                                       'Left index but', 'Right index but', 'Thumbstick x', 'Thumbstick y',
                                       'Number of collision',
                                       'Camera position', 'Head rotation', 'Collision position','Difficulty']

    cols_to_rename_perception_results_old = ['timestamp','trial_number', 'degree', 'degree_perceived', 'level', 'level_perceived',
                                             'feedback_modality', 'relative_timestamp', 'voice_start', 'voice_end',
                                             's_obstacle_gen_on_player_prob']
    cols_to_rename_perception_results_new = ['Timestamp', 'Trial number', 'Angle', 'Angle perceived', 'Distance', 'Distance perceived',
                                             'Modality', 'Phase timestamp', 'Response start', 'Response end',
                                             'Difficulty']

    rows_to_rename_raw_demographics_old = ['Dobini', 'ticklish', 'Subject_Info']
    rows_to_rename_raw_demographics_new = ['Diplopia', 'Ticklishness', 'Info']

    rename_dataset_labels(
        recording_directory=recording_directory,
        trials_file_name='Perception results',
        rec_data_file_name='Experiment logs',
        sub_info_file_name='Demographics',
        cols_to_rename_raw_exp_logs_old=cols_to_rename_raw_exp_logs_old,
        cols_to_rename_raw_exp_logs_new=cols_to_rename_raw_exp_logs_new,
        cols_to_rename_perception_results_old=cols_to_rename_perception_results_old,
        cols_to_rename_perception_results_new=cols_to_rename_perception_results_new,
        rows_to_rename_raw_demographics_old=rows_to_rename_raw_demographics_old,
        rows_to_rename_raw_demographics_new=rows_to_rename_raw_demographics_new
    )

    change_format_xlsx_to_csv(recording_directory)

    remove_nondominant_ind_but_col(recording_directory)

    merge_raw_perception(recording_directory)
    rename_values(recording_directory)


    cols_to_remove_que_final = ['نام و نام خانوادگی:', 'ایمیل:', 'تاریخ شروع', 'تاریخ اتمام', 'پاسخنامه', 'شناسه پاسخ دهنده']
    cols_to_remove_que_mid = cols_to_remove_que_final
    remove_cols_ques_mid_final(questionnaire_directory, cols_to_remove_que_mid, cols_to_remove_que_final)
    process_final_questionnaire(questionnaire_directory)
    process_mid_questionnaire(questionnaire_directory)

