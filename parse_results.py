# ---------------------------------------------
# Script: parse_results.py
# ---------------------------------------------
#
# OVERVIEW
# --------
# This script parses and analyses the output of optimization tasks performed 
# by the 'ibexopt' tool. The output from each task is stored in a text file,
# from which this script extracts, processes and structures the data for further
# analysis. The script takes in a list of files to process and some relevant parameters
# and produces summarized results.
#
# FUNCTIONS
# ---------
# - `extract_data`: This function takes as input the name of an output file, reads the file,
#   extracts the CPU time and number of cells, and returns them. If either value is not found,
#   the function prints a warning message and returns None for both values.
#
# - `process_files`: This function takes as input a list of file names, a directory path, and
#   values for alpha, max_iter and prec. It then processes each file, collects statistics such
#   as the average, standard deviation, median, minimum and maximum of both the CPU times and 
#   the number of cells across the tasks. It returns a pandas DataFrame summarizing the results.
#
# - `main`: This function is the main entry point of the script. It parses command line arguments
#   for the various parameters and file paths, then calls `process_files` to process the files 
#   and summarize the results. Finally, it writes the results to a CSV file.
#
# PARAMETERS
# ----------
# The following parameters are parsed from command line:
# - `--alpha`: One or more alpha values to be used when generating the output file names.
# - `--max_iter`: One or more max_iter values to be used when generating the output file names.
# - `--prec`: One or more precision values to be used when generating the output file names.
# - `--ibex_tools_dir`: Directory where ibex tools are located.
# - `--bench_list`: A text file containing a list of benchmarks to run.
# - `--baseline_params`: A string containing the parameters used in the baseline run, separated by spaces.
#
# EXECUTION
# ---------
# The script extracts CPU times and number of cells from each output file whose name matches
# a pattern generated from the input parameters. It calculates several statistical measures from
# the extracted values and stores them in a pandas DataFrame. The DataFrame is then written to a 
# CSV file. The filename of the CSV file includes a timestamp and the input parameters.
# ---------------------------------------------

import pandas as pd
import re
import numpy as np
import glob
import os
from datetime import datetime
import argparse
import itertools


def extract_data(output_file):
    with open(output_file, 'r') as f:
        file_contents = f.read()

    cpu_time_match = re.search(r'cpu time used:\s+([-\d\.e]+)s', file_contents)
    num_cells_match = re.search(r'number of cells:\s+([-\d\.e]+)', file_contents)
    if cpu_time_match and num_cells_match:
        cpu_time = round(float(cpu_time_match.group(1)), 7)
        num_cells = int(float(num_cells_match.group(1)))
        return cpu_time, num_cells
    else:
        print(f"Skipping file: {output_file} due to missing data")
        print("File contents:")
        print(file_contents)
        return None, None


def process_files(file_names, ibex_tools_dir, alpha, max_iter, prec, is_baseline=False):
    results = {'file': [], 'params': [], 'avg_time': [], 'std_time': [], 'avg_cells': [], 'std_cells': [], 'median_time': [], 'median_cells': [], 'min_time': [], 'max_time': [], 'min_cells': [], 'max_cells': []}
    alpha_str = str(alpha).replace('.', ',')
    max_iter_str = str(max_iter)
    prec_str = str(prec).replace('.', ',')

    for file_name in file_names:
        if is_baseline:
            param_pattern = f"_alpha{alpha_str}_maxIter{max_iter_str}_prec{prec_str}"
            output_file_pattern = 'baseline_' + os.path.basename(file_name) + param_pattern
            output_files = sorted(glob.glob(f"{ibex_tools_dir}/outputs/{output_file_pattern}-*.txt"),
                                  key=lambda x: int(x.rsplit('-', 1)[1].split('.')[0]))
        else:
            param_pattern = f"_alpha{alpha_str}_maxIter{max_iter_str}_prec{prec_str}"
            output_file_pattern = os.path.basename(file_name) + param_pattern
            output_files = sorted(glob.glob(f"{ibex_tools_dir}/outputs/{output_file_pattern}-*.txt"),
                                  key=lambda x: int(x.rsplit('-', 1)[1].split('.')[0]))
        
        times = []
        cells = []
        for output_file in output_files:
            cpu_time, num_cells = extract_data(output_file)
            if cpu_time is not None and num_cells is not None:
                times.append(cpu_time)
                cells.append(num_cells)

        if len(times) != 0:
            results['file'].append(file_name)
            results['params'].append(param_pattern)
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

    return pd.DataFrame(results).set_index(['file', 'params'])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--alpha', nargs='+', type=float, required=True)
    parser.add_argument('--max_iter', nargs='+', type=int, required=True)
    parser.add_argument('--prec', nargs='+', type=float, required=True)
    parser.add_argument('--ibex_tools_dir', type=str, required=True)
    parser.add_argument('--bench_list', type=str, required=True)
    parser.add_argument('--baseline_params', type=str, required=True)
    
    args = parser.parse_args()
    baseline_params = args.baseline_params.split(' ')
    
    # Parse baseline parameters and convert to appropriate types
    baseline_alpha = float(baseline_params[0].replace(',', '.'))
    baseline_max_iter = int(baseline_params[1])
    baseline_prec = float(baseline_params[2].replace(',', '.'))
    
    timestamp = datetime.now().strftime('%Y%m%d%H%M')

    with open(args.bench_list, 'r') as f:
        file_names = f.read().splitlines()

    # Process baseline files
    df_baseline = process_files(file_names, args.ibex_tools_dir, baseline_alpha, baseline_max_iter, baseline_prec, is_baseline=True)
    df_baseline.to_csv(f"{args.ibex_tools_dir}/baseline_bench_data_{timestamp}.csv")

    # Loop over parameter values
    for alpha, max_iter, prec in itertools.product(args.alpha, args.max_iter, args.prec):
        print(f"Processing alpha={alpha}, max_iter={max_iter}, prec={prec}")
        df = process_files(file_names, args.ibex_tools_dir, alpha, max_iter, prec)
        df.to_csv(f"{args.ibex_tools_dir}/bench_data_{timestamp}_alpha_{alpha}_max_iter_{max_iter}_prec_{prec}.csv")


if __name__ == "__main__":
    main()
