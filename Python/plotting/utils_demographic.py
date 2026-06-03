from pathlib import Path
from utils import *


def check_folder_contents(base_dir):
    base_path = Path(base_dir)

    # print(f"Scanning folders in: {base_path.resolve()}\n{'-' * 50}")

    for item in base_path.iterdir():
        # We only care about directories (folders), skip standalone files
        if item.is_dir():
            folder_name = item.name

            # Define the exact paths for the three files we expect to see
            file1_csv = item / f"received_data_{folder_name}.csv"
            file2_xlsx = item / f"{folder_name}_cleaned.xlsx"
            file3_info = item / "subject_info.xlsx"

            # Check which files are missing
            missing_files = []
            if not file1_csv.exists():
                missing_files.append(f"received_data_{folder_name}.csv")
            if not file2_xlsx.exists():
                missing_files.append(f"{folder_name}_cleaned.xlsx")
            if not file3_info.exists():
                missing_files.append("subject_info.xlsx")

            # Print the results for this folder
            if not missing_files:
                print(f"✅ [{folder_name}] - All files present.")
            else:
                print(f"❌ [{folder_name}] - Missing: {', '.join(missing_files)}")


def number_of_subjects_info(base_dir, info='ticklish', value='yes'):
    base_path = Path(base_dir)
    subject_count = 0
    for item in base_path.iterdir():
        if item.is_dir():
            excel_path = item / "subject_info.xlsx"
            if excel_path.exists():
                df = pd.read_excel(excel_path)
                    # Filter rows where Info and Value match (ignoring case and whitespace)
                matching_rows = df[
                    (df['Subject_Info'].astype(str).str.strip().str.lower() == info.lower()) &
                    (df['Value'].astype(str).str.strip().str.lower() == value.lower())
                    ]
                if not matching_rows.empty:
                    subject_count += 1
                    # print(item)
    print(f"Number of subjects with '{info} {value}' is: {subject_count}")


    return subject_count
