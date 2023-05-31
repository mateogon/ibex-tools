# ---------------------------------------------
# Script: run.py
# ---------------------------------------------
#
# OVERVIEW
# --------
# This Python script automates the running and benchmarking of optimization tasks using the Ibex 
# library's `ibexopt` tool. It first runs a baseline benchmark for comparison, then conducts 
# multiple test runs with a variety of parameter combinations. It then analyzes the results 
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
# - `python_script_baseline`: Location of the Python script used to create the baseline
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
#    - Runs the Python script to parse the results.
#    - Increments the loop counter and starts again with the next parameter combination.
#
# The output of each `ibexopt` execution is saved to a text file in the `outputs` directory. The filename contains the 
# name of the benchmark file and the run number, and for baseline runs, it is prefixed with `baseline_`.
# ---------------------------------------------

import os
import subprocess
import time
import itertools
from multiprocessing import Pool, cpu_count
from concurrent.futures import ThreadPoolExecutor, as_completed

# Variable definitions
ibex_dir="/home/mateo/Desktop/ibex-lib"  # Directory of ibex-lib
tools_dir="/home/mateo/Desktop/ibex-tools"  # Directory of ibex-tools
input_file=f"{tools_dir}/bench_list"  # Name of the input file
python_interpreter="/usr/bin/python3"  # Python interpreter location
python_script=f"{tools_dir}/parse_results.py"  # Python script location
python_script_baseline=f"{tools_dir}/create_baseline.py"  # Python script location for baseline
ibexopt=f"{ibex_dir}/__build__/src/ibexopt"  # ibexopt location
header_file=f"{ibex_dir}/src/loup/ibex_LoupFinderIterative.h"  # Header file location

num_runs=10  # Number of runs
# Maximum number of parallel jobs, adjust this to the number of CPU cores on your machine
max_jobs=cpu_count()  # cpu_count()
# Parameter combinations to test
alpha_values=[0.8, 0.75, 0.85]
max_iter_values=[4, 5, 6]
prec_values=[1e-4, 5e-5, 2e-4]

num_combinations = len(alpha_values) * len(max_iter_values) * len(prec_values)

# Baseline parameters
baseline_alpha=0.9
baseline_max_iter=10
baseline_prec=1e-3
baseline_num_runs=5


def execute_ibexopt(file_path, run, loop_number, is_baseline):
    file_name = os.path.basename(file_path)
    output_prefix = "baseline_" if is_baseline else ""
    output_file = f"{tools_dir}/outputs/{output_prefix}{file_name}_{run}.txt"
    cmd = f"{ibexopt} {ibex_dir}/benchs/optim/{file_path}.bch --random-seed={loop_number} > {output_file}"
    subprocess.Popen(cmd, shell=True)


def wait_for_jobs():
    while True:
        if len(subprocess.check_output("jobs -p", shell=True).splitlines()) < max_jobs:
            return
        time.sleep(1)


def run_python_script(alpha, max_iter, prec, script):
    cmd = f"{python_interpreter} {script} --alpha {alpha} --max_iter {max_iter} --prec {prec} --ibex_tools_dir {tools_dir} --bench_list {input_file}"
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
    for file_path in file_paths:
        wait_for_jobs()
        execute_ibexopt(file_path, run, 1, True)

run_python_script(baseline_alpha, baseline_max_iter, baseline_prec, python_script_baseline)

# Now proceed with the main loop for other parameter combinations
loop_number=1

for alpha, max_iter, prec in itertools.product(alpha_values, max_iter_values, prec_values):
    print(f"Starting loop {loop_number} out of {num_combinations}: parameters alpha={alpha}, max_iter={max_iter}, prec={prec}")
    apply_params(alpha, max_iter, prec)

    for run in range(1, num_runs + 1):
        print(f"Starting run {run} out of {num_runs}")
        for file_path in file_paths:
            wait_for_jobs()
            execute_ibexopt(file_path, run, loop_number, False)
    run_python_script(alpha, max_iter, prec, python_script)

    loop_number += 1
