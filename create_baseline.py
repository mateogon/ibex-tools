import pandas as pd
import re
import numpy as np
import glob
import os
from datetime import datetime
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--alpha', type=float, required=True)
parser.add_argument('--max_iter', type=int, required=True)
parser.add_argument('--prec', type=float, required=True)
parser.add_argument('--ibex_tools_dir', type=str, required=True)
parser.add_argument('--bench_list', type=str, required=True)
args = parser.parse_args()

alpha = args.alpha
max_iter = args.max_iter
prec = args.prec
ibex_tools_dir = args.ibex_tools_dir
bench_list = args.bench_list
timestamp = datetime.now().strftime('%Y%m%d%H%M')
# Add the parameters to the filename
filename_suffix = f"{timestamp}_alpha{alpha}_maxIter{max_iter}_prec{prec}"

# Open the input file containing the list of file names
with open(bench_list, 'r') as f:
    file_names = f.read().splitlines()

# Initialize dictionary to store the results
results = {'file': [], 'avg_time': [], 'std_time': [], 'avg_cells': [], 'std_cells': [], 'median_time': [], 'median_cells': [], 'min_time': [], 'max_time': [], 'min_cells': [], 'max_cells': []}

# Loop through each file name in the input file
for file_name in file_names:
    # Get a list of all the output files for this bench, sorted by run number
    output_files = sorted(glob.glob(ibex_tools_dir+'/outputs/baseline_{}_*.txt'.format(file_name.split('/')[-1])), 
                          key=lambda x: int(x.rsplit('_', 1)[1].split('.')[0]))

    times = []
    cells = []
    for output_file in output_files:
        # Open the output file for reading
        with open(output_file, 'r') as f:
            file_contents = f.read()

            # Use regular expressions to extract the CPU time and number of cells
            cpu_time_match = re.search(r'cpu time used:\s+(\d+\.\d+?)s', file_contents)
            num_cells_match = re.search(r'number of cells:\s+(\d+)', file_contents)

            # If both matches are found, append the data; otherwise, skip this file
            if cpu_time_match and num_cells_match:
                cpu_time = round(float(cpu_time_match.group(1)), 7)
                num_cells = int(num_cells_match.group(1))
                times.append(cpu_time)
                cells.append(num_cells)
            else:
                print(f"Skipping file: {output_file} due to missing data")

    if len(times) != 0:
        # Calculate statistics for the times and cells
        avg_time = np.mean(times)
        std_time = np.std(times)
        median_time = np.median(times)
        avg_cells = np.mean(cells)
        std_cells = np.std(cells)
        median_cells = np.median(cells)
        min_time = np.min(times)
        max_time = np.max(times)
        min_cells = np.min(cells)
        max_cells = np.max(cells)

        # Append to results
        results['file'].append(file_name)
        results['avg_time'].append(avg_time)
        results['std_time'].append(std_time)
        results['avg_cells'].append(avg_cells)
        results['std_cells'].append(std_cells)
        results['median_time'].append(median_time)
        results['median_cells'].append(median_cells)
        results['min_time'].append(min_time)
        results['max_time'].append(max_time)
        results['min_cells'].append(min_cells)
        results['max_cells'].append(max_cells)
    else:
        print("Warning: Attempted operation on empty array")

# Convert results to DataFrame and set 'file' as index
df = pd.DataFrame(results).set_index('file')
# Write data to CSV
df.to_csv(os.curdir+f'/baseline_bench_data.csv')
