import os
import pandas as pd
import re

# Define the path where your CSVs are located
csv_directory = '/home/mateo/Desktop/ibex-tools/'  # Replace with the path to your CSV files

# Initialize list to hold all data
all_data = []

# Iterate over CSVs in the directory
for filename in os.listdir(csv_directory):
    if filename.endswith(".csv"):
        # Extract parameter configuration from the filename
        raw_parameters = re.search('alpha.*', filename).group()
        
        # Process parameters to make them more readable
        parameters = raw_parameters.replace('_', ' ').replace('.csv', '')
        
        # Read the CSV
        df = pd.read_csv(os.path.join(csv_directory, filename))
        
        # Add a column for the parameters
        df['parameters'] = parameters
        
        # Append the DataFrame to the all_data list
        all_data.append(df)

# Concatenate all dataframes
all_data = pd.concat(all_data, ignore_index=True)

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

# Find the parameters that resulted in the minimum average time for each file
best_params_per_file = all_data.loc[all_data.groupby('file')['avg_time'].idxmin()][['file', 'parameters']]

# Count how often each parameter configuration is the best
param_counts = best_params_per_file['parameters'].value_counts()

# Create a DataFrame from these counts
param_counts_df = param_counts.reset_index()
param_counts_df.columns = ['parameters', 'count']

# Add a percentage column
total = param_counts_df['count'].sum()
param_counts_df['percentage'] = (param_counts_df['count'] / total) * 100

# Sort the DataFrame by the count column in descending order
param_counts_df = param_counts_df.sort_values(by='count', ascending=False)

print(param_counts_df)