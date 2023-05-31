'''
---------------------------------------------------------------------------
Python script: parse_results.py
---------------------------------------------------------------------------

OVERVIEW
--------
This script processes the output of optimization tasks run by the Ibex library's 'ibexopt' tool. It extracts the CPU time
used and the number of cells created during the optimization process from the output files, computes basic statistics 
(average, standard deviation, median, minimum, maximum), and writes these results to a CSV file.

FUNCTIONS
---------
- `extract_data`: Reads an output file and uses regular expressions to extract the CPU time used and the number of cells.
- `process_files`: Iterates over a list of file names, calls `extract_data` for each file, collects the results, 
  computes the statistics and returns a DataFrame with the results.
- `main`: Parses command-line arguments, reads the list of benchmarks from a file, calls `process_files`, 
  and writes the results to a CSV file.

PARAMETERS
----------
- `alpha`: Parameter value for alpha used in the optimization tasks.
- `max_iter`: Parameter value for max_iter used in the optimization tasks.
- `prec`: Parameter value for prec used in the optimization tasks.
- `ibex_tools_dir`: Directory of Ibex tools.
- `bench_list`: Name of the input file containing the list of benchmarks to run.

EXECUTION
---------
The script expects the output files to be in the 'outputs' subdirectory of `ibex_tools_dir`, with file names in the 
format '{benchmark_file_name}_{run_number}.txt'. It reads the list of benchmarks from a file whose name is passed via 
the `bench_list` argument.

The output CSV file is written to `ibex_tools_dir` and its name contains the timestamp, the parameters alpha, max_iter,
and prec in the format: 'bench_data_{timestamp}_alpha{alpha}_maxIter{max_iter}_prec{prec}.csv'.

It should be called from the command line with the appropriate arguments, for example:
python process_ibex_results.py --alpha 0.5 --max_iter 1000 --prec 0.01 --ibex_tools_dir /path/to/ibex/tools --bench_list benchmarks.txt

---------------------------------------------------------------------------
'''


import pandas as pd
import re
import numpy as np
import glob
import os
from datetime import datetime
import argparse

def extract_data(output_file):
    with open(output_file, 'r') as f:
        file_contents = f.read()
    cpu_time_match = re.search(r'cpu time used:\s+(\d+\.\d+?)s', file_contents)
    num_cells_match = re.search(r'number of cells:\s+(\d+)', file_contents)

    if cpu_time_match and num_cells_match:
        cpu_time = round(float(cpu_time_match.group(1)), 7)
        num_cells = int(num_cells_match.group(1))
        return cpu_time, num_cells
    else:
        print(f"Skipping file: {output_file} due to missing data")
        return None, None

def process_files(file_names, ibex_tools_dir):
    results = {'file': [], 'avg_time': [], 'std_time': [], 'avg_cells': [], 'std_cells': [], 'median_time': [], 'median_cells': [], 'min_time': [], 'max_time': [], 'min_cells': [], 'max_cells': []}

    for file_name in file_names:
        output_files = sorted(glob.glob(ibex_tools_dir+'/outputs/{}_*.txt'.format(file_name.split('/')[-1])), 
                            key=lambda x: int(x.rsplit('_', 1)[1].split('.')[0]))

        times = []
        cells = []
        for output_file in output_files:
            cpu_time, num_cells = extract_data(output_file)
            if cpu_time is not None and num_cells is not None:
                times.append(cpu_time)
                cells.append(num_cells)
        
        if len(times) != 0:
            results['file'].append(file_name)
            results['avg_time'].append(np.mean(times))
            results['std_time'].append(np.std(times))
            results['avg_cells'].append(np.mean(cells))
            results['std_cells'].append(np.std(cells))
            results['median_time'].append(np.median(times))
            results['median_cells'].append(np.median(cells))
            results['min_time'].append(np.min(times))
            results['max_time'].append(np.max(times))
            results['min_cells'].append(np.min(cells))
            results['max_cells'].append(np.max(cells))
        else:
            print("Warning: Attempted operation on empty array")

    return pd.DataFrame(results).set_index('file')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--alpha', type=float, required=True)
    parser.add_argument('--max_iter', type=int, required=True)
    parser.add_argument('--prec', type=float, required=True)
    parser.add_argument('--ibex_tools_dir', type=str, required=True)
    parser.add_argument('--bench_list', type=str, required=True)
    args = parser.parse_args()

    timestamp = datetime.now().strftime('%Y%m%d%H%M')
    filename_suffix = f"{timestamp}_alpha{args.alpha}_maxIter{args.max_iter}_prec{args.prec}"

    with open(args.bench_list, 'r') as f:
        file_names = f.read().splitlines()

    df = process_files(file_names, args.ibex_tools_dir)
    df.to_csv(args.ibex_tools_dir+f'/bench_data_{filename_suffix}.csv')

if __name__ == "__main__":
    main()
