import pandas as pd

def calculate_state_percentages(csv_file, column_name):
    try:
        # Read the CSV file into a pandas DataFrame
        df = pd.read_csv(csv_file)

        # Check if the specified column exists
        if column_name not in df.columns:
            print(f"Column '{column_name}' does not exist in the CSV file.")
            return

        # Drop rows where the state is missing (optional)
        state_series = df[column_name].dropna()

        # Count the occurrences of each state
        state_counts = state_series.value_counts()

        # Calculate the total number of valid entries
        total = state_counts.sum()

        # Calculate the percentage for each state
        state_percentages = (state_counts / total) * 100

        # Round percentages to two decimal places (optional)
        state_percentages = state_percentages.round(2)

        # Create a DataFrame for better display
        result_df = pd.DataFrame({
            'Headquarters State': state_counts.index,
            'Count': state_counts.values,
            'Percentage': state_percentages.values
        })

        # Sort the DataFrame by percentage in descending order
        result_df = result_df.sort_values(by='Percentage', ascending=False).reset_index(drop=True)

        print(result_df)

        unique_values = state_counts.size
        print(f"\nTotal Number of Unique Values: {unique_values}")

    except FileNotFoundError:
        print(f"The file '{csv_file}' was not found.")
    except pd.errors.EmptyDataError:
        print(f"The file '{csv_file}' is empty.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Specify the path to your CSV file
    csv_file = 'data/processed/final_h1_data.csv'

    # Specify the column name containing the state information
    column_name = 'Cleaned Industry'

    # Call the function to calculate and display percentages
    calculate_state_percentages(csv_file, column_name)