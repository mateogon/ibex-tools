# ---------------------------------------------
# Script: run.py
# ---------------------------------------------
#
# OVERVIEW
# --------
# This Python script automates the running and benchmarking of optimization tasks using the Ibex 
# library's `ibexopt` tool. It first runs a baseline benchmark for comparison, then conducts 
# multiple test runs with a variety of parameter combinations. Finally, it analyzes the results 
# using a Python script. By running tasks in parallel, the script efficiently leverages 
# system resources for improved performance.
#
# PARAMETERS
# ----------
# The following variables need to be set at the beginning of the script:
# - `ibex_dir`: Directory of Ibex library
# - `tools_dir`: Directory of Ibex tools
# - `input_file`: Name of the input file containing the list of benchmarks to run
# - `python_interpreter`: Location of the Python interpreter
# - `python_script`: Location of the Python script used to parse the results
# - `ibexopt`: Location of the `ibexopt` executable
# - `header_file`: Location of the Ibex header file where the parameters are defined
# - `num_runs`: Number of runs
# - `max_jobs`: Maximum number of parallel jobs, adjust this to the number of CPU cores on your machine
# - `alpha_values`, `max_iter_values`, `prec_values`: Lists of parameter combinations to test
# - `baseline_alpha`, `baseline_max_iter`, `baseline_prec`, `baseline_num_runs`: Parameters for the baseline run
#
# FUNCTIONS
# ---------
# - `execute_ibexopt`: Executes the `ibexopt` tool with a given benchmark and stores the output in a text file. 
#    It is run as a subprocess, allowing for parallel execution.
# - `wait_for_jobs`: Waits until the number of subprocesses is below the maximum limit before returning.
# - `run_python_script`: Runs the Python script to parse the results of the `ibexopt` executions.
# - `apply_params`: Applies the parameters to the Ibex header file.
# - `generate_results()`: Reads all the CSV files in the script directory, finds the baseline benchmark CSV file,
#     extracts the parameter configurations from each CSV file name, merges the data from all CSVs into one DataFrame,
#     calculates the improvement for each file, identifies the best parameters per file, counts how often each
#     parameter configuration yields the best results, and writes the results to a new CSV file 'combined_results_data.csv'.
#
# EXECUTION
# ---------
# The script performs the following steps:
# 1. It first runs the baseline benchmark with defined baseline parameters.
# 2. Next, it proceeds with the main loop for other parameter combinations, which includes the following steps:
#    - Updates the Ibex header file with the new parameter values.
#    - Rebuilds the Ibex library.
#    - Executes the `ibexopt` tool for each benchmark in the input file, up to `num_runs` times each. 
#      These executions are done as subprocesses, up to `max_jobs` concurrent subprocesses.
#    - Waits for all `ibexopt` subprocesses to finish.
#    - Increments the loop counter and starts again with the next parameter combination.
# 3. After all parameter combinations have been tested, the Python script to parse the results is run.
# 4. Calls the `generate_results()` function to generate a combined CSV file of the results.
#
# The output of each `ibexopt` execution is saved to a text file in the `outputs` directory. The filename contains the 
# name of the benchmark file, the run number, the parameter combination, and for baseline runs, it is prefixed with `baseline_`.
# ---------------------------------------------



import os
import subprocess
import time
import itertools
from multiprocessing import Pool, cpu_count
from concurrent.futures import ThreadPoolExecutor, as_completed
from generate_results_csv import generate_results
# Variable definitions
ibex_dir="/home/mateo/Desktop/ibex-lib"  # Directory of ibex-lib
tools_dir="/home/mateo/Desktop/ibex-tools"  # Directory of ibex-tools
input_file=f"{tools_dir}/bench_list"  # Name of the input file
python_interpreter="/usr/bin/python3"  # Python interpreter location
python_script=f"{tools_dir}/parse_results.py"  # Python script location
ibexopt=f"{ibex_dir}/__build__/src/ibexopt"  # ibexopt location
header_file=f"{ibex_dir}/src/loup/ibex_LoupFinderIterative.h"  # Header file location

num_runs=3  # Number of runs per parameter combination
# Maximum number of parallel jobs, adjust this to the number of CPU cores on your machine
max_jobs= cpu_count()
# Parameter combinations to test
alpha_values=[0.8, 0.75, 0.85]
max_iter_values=[4, 6, 8 , 10]
prec_values=[1e-4, 5e-5, 2e-4]

num_combinations = len(alpha_values) * len(max_iter_values) * len(prec_values)

# Baseline parameters
baseline_alpha=0.9
baseline_max_iter=10
baseline_prec=1e-3
baseline_num_runs=5
baseline_params = (baseline_alpha, baseline_max_iter, baseline_prec)


def execute_ibexopt(file_path, run, loop_number, is_baseline, alpha, max_iter, prec):
    file_name = os.path.basename(file_path)
    output_prefix = "baseline_" if is_baseline else ""
    alpha_str = str(alpha).replace(".", ",")
    max_iter_str = str(max_iter)
    prec_str = str(prec).replace(".", ",")
    output_params = f"_alpha{alpha_str}_maxIter{max_iter_str}_prec{prec_str}"
    output_file = f"{tools_dir}/outputs/{output_prefix}{file_name+output_params}-{run}.txt"
    cmd = f"{ibexopt} {ibex_dir}/benchs/optim/{file_path}.bch --random-seed={loop_number} > {output_file}"
    return subprocess.Popen(cmd, shell=True)


def wait_for_jobs():
    while True:
        if len(subprocess.check_output("jobs -p", shell=True).splitlines()) < max_jobs:
            return
        time.sleep(1)


def run_python_script(script):
    alpha_str = ' '.join(map(str, alpha_values))
    max_iter_str = ' '.join(map(str, max_iter_values))
    prec_str = ' '.join(map(str, prec_values))
    baseline_str = ' '.join(map(str, baseline_params))
    cmd = f"{python_interpreter} {script} --alpha {alpha_str} --max_iter {max_iter_str} --prec {prec_str} --baseline_params \"{baseline_str}\" --ibex_tools_dir {tools_dir} --bench_list {input_file}"
    subprocess.run(cmd, shell=True)

def apply_params(alpha, max_iter, prec):
    with open(header_file, "r") as file:
        filedata = file.read()

    filedata = filedata.replace("double alpha=", f"double alpha={alpha}")
    filedata = filedata.replace("int max_iter=", f"int max_iter={max_iter}")
    filedata = filedata.replace("double prec=", f"double prec={prec}")

    with open(header_file, "w") as file:
        file.write(filedata)

    subprocess.run(f"cd {ibex_dir} && ./waf install > waf_install.log 2>/dev/null", shell=True)


# Run the baseline benchmark
print(f"Running baseline benchmark with parameters alpha={baseline_alpha}, max_iter={baseline_max_iter}, prec={baseline_prec}")
apply_params(baseline_alpha, baseline_max_iter, baseline_prec)

with open(input_file, "r") as file:
    file_paths = file.read().splitlines()

for run in range(1, baseline_num_runs + 1):
    print(f"Starting run {run} out of {baseline_num_runs}")
    processes = []
    for file_path in file_paths:
        wait_for_jobs()
        p = execute_ibexopt(file_path, run, 1, True, baseline_alpha, baseline_max_iter, baseline_prec)
        processes.append(p)
    # Wait for all processes to finish
    for p in processes:
        p.wait()
        
# Now proceed with the main loop for other parameter combinations
loop_number=1

for alpha, max_iter, prec in itertools.product(alpha_values, max_iter_values, prec_values):
    print(f"Starting loop {loop_number} out of {num_combinations}: parameters alpha={alpha}, max_iter={max_iter}, prec={prec}")
    apply_params(alpha, max_iter, prec)

    for run in range(1, num_runs + 1):
        print(f"Starting run {run} out of {num_runs}")
        processes = []
        for file_path in file_paths:
            wait_for_jobs()
            p = execute_ibexopt(file_path, run, loop_number, False, alpha, max_iter, prec)
            processes.append(p)
        # Wait for all processes to finish
        for p in processes:
            p.wait()
    loop_number += 1
    
run_python_script(python_script)
generate_results(num_runs,baseline_num_runs)