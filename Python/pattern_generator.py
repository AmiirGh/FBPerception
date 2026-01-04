import csv
import itertools


def create_repeated_experiment_csv():
    # 1. Define your values
    degrees = list(range(1, 9))  # 1 to 8
    feedback_modalities = ['Visual', 'Audio', 'Haptic']
    levels = ['far', 'mid', 'near']

    # 2. Generate the base combinations (72 rows)
    # This creates a list of tuples: (1, 'Visual', 'far'), etc.
    base_combinations = list(itertools.product(degrees, feedback_modalities, levels))

    # 3. Repeat the list 3 times
    # This appends the list to itself, creating Block 1, then Block 2, then Block 3
    final_data = base_combinations * 3

    filename = 'experiment_3x_repetition.csv'

    # 4. Write to CSV
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)

        # Write Header
        writer.writerow(['Degree', 'Feedback_Modality', 'Level'])

        # Write Data
        writer.writerows(final_data)

    print(f"Successfully created '{filename}'")
    print(f"Total rows generated: {len(final_data)}")


if __name__ == "__main__":
    create_repeated_experiment_csv()