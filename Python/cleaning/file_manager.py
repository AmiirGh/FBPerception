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
    folders = [
        f for f in os.listdir(recording_directory)
        if os.path.isdir(os.path.join(recording_directory, f))
    ]

    if not folders:
        print("No folders found.")
        return

    # -------------------------
    # Shuffle + mapping
    # -------------------------
    random.seed(seed)
    shuffled = folders.copy()
    random.shuffle(shuffled)

    width = max(2, len(str(len(shuffled))))

    id_mapping = {
        old_id: str(i + 1).zfill(width)
        for i, old_id in enumerate(shuffled)
    }

    print("Mapping (old -> new):")
    for k, v in id_mapping.items():
        print(k, "->", v)

    # -------------------------
    # Rename files inside folders
    # -------------------------
    for old_id, new_id in id_mapping.items():

        folder_path = os.path.join(recording_directory, old_id)

        for filename in os.listdir(folder_path):

            old_file_path = os.path.join(folder_path, filename)

            if not os.path.isfile(old_file_path):
                continue

            if old_id in filename:
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

        output_path = os.path.join(
            questionnaire_directory,
            file_name.replace(".xlsx", "_new.xlsx")
        )

        df.to_excel(output_path, index=False)
        print(f"Saved: {output_path}")

    return id_mapping



recording_directory = '../Dataset/Recordings'
questionnaire_directory = '../Dataset/Questionnaire'

output_dir = Path("../Dataset/Recordings_csv")
output_directory_path = './xlsx_csv_json_files_only'
if __name__ == "__main__":
    # excel_to_csv(directory_path, output_dir)
    # find_problematic_recordings(directory_path)
    # remove_specific_spreadsheets(directory_path, dry_run=True)
    # filter_and_copy_spreadsheets(recording_directory, output_directory_path)
    mapping = anonymize_folders(recording_directory, questionnaire_directory)