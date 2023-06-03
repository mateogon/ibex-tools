"""
This function `generate_results()` generates a combined CSV file containing the results of different test cases 
and their respective improvements over a baseline.

This script works by:
- Reading all the CSV files in the same directory of the script.
- Finding the baseline benchmark CSV file in the directory.
- Extracting the parameter configurations from each CSV file name.
- Adding a new 'parameters' column in each DataFrame to hold the extracted parameters.
- Merging the data from all CSVs into one DataFrame.
- Calculating the improvement for each file, defined as the percent change from the baseline to the test file's average time.
- Identifying the best parameters per file, defined as the ones that yield the minimum average time.
- Counting how often each parameter configuration yields the best results.
- Calculating the average improvement for each parameter configuration and for the best configuration.
- Writing the results to a new CSV file 'combined_results_data.csv', which contains two sections:
    1. 'Best Parameters per File': Listing each file with its best parameter configuration and corresponding statistics.
    2. 'All Parameter Configurations': Listing each parameter configuration with its average improvements (best and overall) and how often it was the best.

The output file 'combined_results_data.csv' will be written to the same directory where the script is located.
"""

import os
import pandas as pd
import re

def generate_results():
    # Define the path where your CSVs are located
    csv_directory = os.path.dirname(os.path.abspath(__file__))

    # Define the name of the output CSV file
    output_file = 'combined_results_data.csv'

    # Initialize list to hold all data
    all_data = []

    # Find the latest baseline file in the directory
    baseline_files = [f for f in os.listdir(csv_directory) if f.startswith("baseline_bench_data_")]
    latest_baseline_file = max(baseline_files, key=lambda f: os.path.getmtime(os.path.join(csv_directory, f)))
    baseline_path = os.path.join(csv_directory, latest_baseline_file)

    # Read the baseline data
    baseline_data = pd.read_csv(baseline_path)

    # Iterate over CSVs in the directory
    for filename in os.listdir(csv_directory):
        if filename.endswith(".csv"):
            # Extract parameter configuration from the filename
            match = re.search('alpha.*', filename)
            if match is not None:
                raw_parameters = match.group()
            else:
                #print(f"No match in filename: {filename}")
                continue
            # Process parameters to make them more readable
            parameters = raw_parameters.replace('_', ' ').replace('.csv', '')

            # Read the CSV
            df = pd.read_csv(os.path.join(csv_directory, filename))

            # Add a column for the parameters
            df['parameters'] = parameters

            # Append the DataFrame to the all_data list
            all_data.append(df)

    # Concatenate all dataframes
    all_data_df = pd.concat(all_data, ignore_index=True)

    # Merge all_data_df with the baseline_data DataFrame on the 'file' column
    all_merged_df = pd.merge(all_data_df, baseline_data, on='file', suffixes=('_test', '_baseline'))

    # Calculate the improvement and add it as a new column for all data
    all_merged_df['improvement'] = 100 * (all_merged_df['avg_time_baseline'] - all_merged_df['avg_time_test']) / all_merged_df['avg_time_baseline']

    # Find the parameters that resulted in the minimum average time for each file
    best_params_per_file = all_data_df.loc[all_data_df.groupby('file')['avg_time'].idxmin()]

    # Merge the best_params_per_file DataFrame with the baseline_data DataFrame on the 'file' column
    merged_df = pd.merge(best_params_per_file, baseline_data, on='file', suffixes=('_best', '_baseline'))

    # Calculate the improvement and add it as a new column
    merged_df['improvement_best'] = 100 * (merged_df['avg_time_baseline'] - merged_df['avg_time_best']) / merged_df['avg_time_baseline']

    # Create a new DataFrame with the necessary columns
    best_params_per_file = merged_df[['file', 'parameters', 'avg_time_best', 'avg_time_baseline', 'improvement_best']]

    # Count how often each parameter configuration is the best
    param_counts = best_params_per_file['parameters'].value_counts()

    # Create a DataFrame from these counts
    param_counts_df = param_counts.reset_index()
    param_counts_df.columns = ['parameters', 'count_best']

    # Calculate average improvement for each parameter configuration
    all_param_improvements = all_merged_df.groupby('parameters')['improvement'].mean()

    # Calculate average improvement for best parameter configuration
    best_param_improvements = best_params_per_file.groupby('parameters')['improvement_best'].mean()

    # Merge the dataframes on 'parameters'
    merged_param_df = pd.merge(best_param_improvements, all_param_improvements, left_index=True, right_index=True)

    # Rename the columns
    merged_param_df.columns = ['mean_best', 'mean_all']

    # Merge with counts
    merged_param_df = merged_param_df.merge(param_counts_df, left_index=True, right_on='parameters')

    # Reorder the columns
    merged_param_df = merged_param_df[['parameters', 'count_best', 'mean_best', 'mean_all']]

    # Sort the DataFrame by the count column in descending order
    merged_param_df = merged_param_df.sort_values(by='count_best', ascending=False)

    # Write best_params_per_file dataframe to csv
    with open(output_file, 'w') as f:
        f.write("\nBest Parameters per File\n")
    best_params_per_file.to_csv(output_file, mode='a', index=False)

    # Write merged_param_df dataframe to csv
    with open(output_file, 'a') as f:
        f.write("\nAll Parameter Configurations\n")
    merged_param_df.to_csv(output_file, mode='a', index=False)



