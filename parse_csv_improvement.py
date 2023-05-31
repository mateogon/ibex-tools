import os
import pandas as pd
import re

# Define the path where your CSVs are located
csv_directory = '/home/mateo/Desktop/ibex-tools/'  # Replace with the path to your CSV files
baseline_path = '/home/mateo/Desktop/ibex-tools/baseline_bench_data.csv'

# Read the baseline data
baseline_df = pd.read_csv(baseline_path)
baseline_df.set_index('file', inplace=True)

# Initialize list to hold all data
all_data = []

# Iterate over CSVs in the directory
for filename in os.listdir(csv_directory):
    if filename.endswith(".csv"):
        # Extract parameter configuration from the filename
        raw_parameters = re.search('alpha.*', filename)
        if raw_parameters is None:
            continue
        raw_parameters = raw_parameters.group()

        # Process parameters to make them more readable
        parameters = raw_parameters.replace('_', ' ').replace('.csv', '')

        # Read the CSV
        df = pd.read_csv(os.path.join(csv_directory, filename))
        df.set_index('file', inplace=True)

        # Calculate the percentage improvement over the baseline for each file
        df['improvement'] = (baseline_df['avg_time'] - df['avg_time']) / baseline_df['avg_time'] * 100

        # Add a column for the parameters
        df['parameters'] = parameters

        # Append the DataFrame to the all_data list
        all_data.append(df)

# Concatenate all dataframes
all_data = pd.concat(all_data, ignore_index=False)

# Create a dictionary to hold all unique values of each parameter
unique_values = {'alpha': set(), 'maxIter': set(), 'prec': set()}

# Iterate over 'parameters' column in all_data DataFrame
for param_str in all_data['parameters'].unique():
    # Split parameter string into parts
    params = param_str.split(' ')
    # Add the values to the corresponding sets in the dictionary
    unique_values['alpha'].add(params[0])
    unique_values['maxIter'].add(params[1])
    unique_values['prec'].add(params[2])

# Display all unique values of each parameter
for param, values in unique_values.items():
    print(f"{param} unique values: {values}")


# Count how often each parameter configuration is the best
param_counts = all_data.loc[all_data.groupby('file')['avg_time'].idxmin()]['parameters'].value_counts()

# Create a DataFrame from these counts
param_counts_df = param_counts.reset_index()
param_counts_df.columns = ['parameters', 'count']

# Calculate the average improvement for each parameter configuration
avg_improvements = all_data.groupby('parameters')['improvement'].mean()
param_counts_df = param_counts_df.join(avg_improvements, on='parameters')

# Rename the columns for clarity
param_counts_df.columns = ['parameters', 'count', 'avg_improvement_percentage']

# Sort the DataFrame by the count column in descending order
param_counts_df = param_counts_df.sort_values(by='avg_improvement_percentage', ascending=False)

print(param_counts_df)
