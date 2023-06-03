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


 The dataframe best_params_per_file is added to the CSV file with the following columns:
 'file': The file name of the test case.
 'parameters': The configuration parameters extracted from the file name.
 'avg_time_best': The average time of the best performing configuration for the test case.
 'avg_time_baseline': The average time of the baseline for the test case.
 'improvement_best': The improvement percentage of the best configuration over the baseline for the test case.

 The dataframe merged_param_df is added to the CSV file with the following columns:
 'parameters': The configuration parameters.
 'count_best': The number of times the parameters configuration was the best.
 'mean_improvement_best': The mean improvement of the best cases for this configuration.
 'std_dev_improvement_best': The standard deviation of the improvement of the best cases for this configuration.
 'min_improvement_best': The minimum improvement of the best cases for this configuration.
 'max_improvement_best': The maximum improvement of the best cases for this configuration.
 'mean_improvement_all': The mean improvement of all cases for this configuration.
 'std_dev_improvement_all': The standard deviation of the improvement of all cases for this configuration.
 'min_improvement_all': The minimum improvement of all cases for this configuration.
 'max_improvement_all': The maximum improvement of all cases for this configuration.
 'total_time_improvement': The total time improvement for this configuration.

"""

import os
import pandas as pd
import re
import numpy as np

def generate_results(num_runs_test=10, num_runs_baseline=10, decimals=7):
    csv_directory = os.path.dirname(os.path.abspath(__file__))
    output_file = 'combined_results_data.csv'
    all_data = []

    baseline_files = [f for f in os.listdir(csv_directory) if f.startswith("baseline_bench_data_")]
    latest_baseline_file = max(baseline_files, key=lambda f: os.path.getmtime(os.path.join(csv_directory, f)))
    baseline_path = os.path.join(csv_directory, latest_baseline_file)
    baseline_data = pd.read_csv(baseline_path)

    for filename in os.listdir(csv_directory):
        if filename.endswith(".csv"):
            match = re.search('alpha.*', filename)
            if match is not None:
                raw_parameters = match.group()
            else:
                continue
            parameters = raw_parameters.replace('_', ' ').replace('.csv', '')
            df = pd.read_csv(os.path.join(csv_directory, filename))
            df['parameters'] = parameters
            all_data.append(df)

    all_data_df = pd.concat(all_data, ignore_index=True)
    all_merged_df = pd.merge(all_data_df, baseline_data, on='file', suffixes=('_test', '_baseline'))
    all_merged_df['improvement'] = 100 * (all_merged_df['avg_time_baseline'] - all_merged_df['avg_time_test']) / all_merged_df['avg_time_baseline']
    best_params_per_file = all_data_df.loc[all_data_df.groupby('file')['avg_time'].idxmin()]
    merged_df = pd.merge(best_params_per_file, baseline_data, on='file', suffixes=('_best', '_baseline'))
    merged_df['improvement_best'] = 100 * (merged_df['avg_time_baseline'] - merged_df['avg_time_best']) / merged_df['avg_time_baseline']
    best_params_per_file = merged_df[['file', 'parameters', 'avg_time_best', 'avg_time_baseline', 'improvement_best']]

    # New metrics
    all_merged_df['total_time_test'] = all_merged_df['avg_time_test'] * num_runs_test
    all_merged_df['total_time_baseline'] = all_merged_df['avg_time_baseline'] * num_runs_baseline
    all_merged_df['total_time_improvement'] = all_merged_df['total_time_baseline'] - all_merged_df['total_time_test']
    total_time_per_param = all_merged_df.groupby('parameters')['total_time_improvement'].sum()
    total_time_df = total_time_per_param.reset_index()
    total_time_df.columns = ['parameters', 'total_time_improvement']

    param_counts = best_params_per_file['parameters'].value_counts()
    param_counts_df = param_counts.reset_index()
    param_counts_df.columns = ['parameters', 'count_best']

    all_param_improvements = all_merged_df.groupby('parameters')['improvement'].agg([np.mean, np.std, np.min, np.max])
    all_param_improvements.columns = ['mean_improvement_all', 'std_dev_improvement_all', 'min_improvement_all', 'max_improvement_all']

    best_param_improvements = best_params_per_file.groupby('parameters')['improvement_best'].agg([np.mean, np.std, np.min, np.max])
    best_param_improvements.columns = ['mean_improvement_best', 'std_dev_improvement_best', 'min_improvement_best', 'max_improvement_best']

    # Combine dataframes
    merged_param_df = pd.merge(best_param_improvements, all_param_improvements, left_index=True, right_index=True)
    merged_param_df = merged_param_df.merge(param_counts_df, left_index=True, right_on='parameters')
    merged_param_df = merged_param_df.merge(total_time_df, on='parameters')
    merged_param_df = merged_param_df[['parameters', 'count_best', 'mean_improvement_best', 'std_dev_improvement_best', 'min_improvement_best', 'max_improvement_best', 'mean_improvement_all', 'std_dev_improvement_all', 'min_improvement_all', 'max_improvement_all', 'total_time_improvement']]
    merged_param_df = merged_param_df.sort_values(by='count_best', ascending=False)

    # After calculations, before writing to CSV
    best_params_per_file = best_params_per_file.round(decimals)
    merged_param_df = merged_param_df.round(decimals)

    with open(output_file, 'w') as f:
        f.write("\nBest Parameters per File\n")
    best_params_per_file.to_csv(output_file, mode='a', index=False)

    with open(output_file, 'a') as f:
        f.write("\nAll Parameter Configurations\n")
    merged_param_df.to_csv(output_file, mode='a', index=False)