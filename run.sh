#!/bin/bash
# ---------------------------------------------
# Script: run.sh
# ---------------------------------------------
#
# OVERVIEW
# --------
# This script automates the running and benchmarking of optimization tasks using the Ibex 
# library's `ibexopt` tool. It first runs a baseline benchmark for comparison, then conducts 
# multiple test runs with a variety of parameter combinations. It then analyzes the results 
# using a Python script. By running tasks in parallel, the script efficiently leverages 
# system resources for improved performance.
#
# PARAMETERS
# ----------
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
# - `alpha_values`, `max_iter_values`, `prec_values`: Arrays of parameter combinations to test
# - `baseline_alpha`, `baseline_max_iter`, `baseline_prec`, `baseline_num_runs`: Parameters for the baseline run
#
# FUNCTIONS
# ---------
# - `execute_ibexopt`: Executes the `ibexopt` tool with a given benchmark and stores the output in a text file. 
#    It is run in the background, allowing for parallel execution.
# - `wait_for_jobs`: Waits until the number of background jobs is below the maximum limit before returning.
# - `run_python_script`: Runs the Python script to parse the results of the `ibexopt` executions.
# - `apply_params`: Applies the parameters to the Ibex header file.
#
# EXECUTION
# ---------
# 1. The script first runs the baseline benchmark with defined baseline parameters.
# 2. Next, it proceeds with the main loop for other parameter combinations, which includes the following steps:
#    - Updates the Ibex header file with the new parameter values.
#    - Rebuilds the Ibex library.
#    - Executes the `ibexopt` tool for each benchmark in the input file, up to `num_runs` times each. 
#      These executions are done in parallel, up to `max_jobs` concurrent jobs.
#    - Waits for all `ibexopt` executions to finish.
#    - Runs the Python script to parse the results.
#    - Increments the loop counter and starts again with the next parameter combination.
#
# The output of each `ibexopt` execution is saved to a text file in the `outputs` directory. The filename contains the 
# name of the benchmark file and the run number, and for baseline runs, it is prefixed with `baseline_`.
# ---------------------------------------------

# Variable definitions
ibex_dir="/home/mateo/Desktop/ibex-lib"         # Directory of ibex-lib
tools_dir="/home/mateo/Desktop/ibex-tools"       # Directory of ibex-tools
input_file="${tools_dir}/bench_list"                  # Name of the input file
python_interpreter="/usr/bin/python3"    # Python interpreter location
python_script="${tools_dir}/parse_results.py" # Python script location
python_script_baseline="${tools_dir}/create_baseline.py" # Python script location for baseline
ibexopt="${ibex_dir}/__build__/src/ibexopt" # ibexopt location
header_file="${ibex_dir}/src/loup/ibex_LoupFinderIterative.h" # Header file location

num_runs=10                                  # Number of runs
# Maximum number of parallel jobs, adjust this to the number of CPU cores on your machine
max_jobs=50 #$(nproc) 
# Parameter combinations to test
alpha_values=(0.8 0.75 0.85)
max_iter_values=(4 5 6)
prec_values=(1e-4 5e-5 2e-4)


#obtain the number of combinations
num_combinations=$(( ${#alpha_values[@]} * ${#max_iter_values[@]} * ${#prec_values[@]} ))

# Baseline parameters
baseline_alpha=0.9
baseline_max_iter=10
baseline_prec=1e-3
baseline_num_runs=5

# Function definition
execute_ibexopt() {
    local file_path=$1
    local run=$2
    local loop_number=$3
    local is_baseline=$4
    local file_name=$(basename "${file_path}")
    
    local output_prefix=""
    if [ "${is_baseline}" = "true" ]; then
        output_prefix="baseline_"
    fi

    "${ibexopt}" "${ibex_dir}/benchs/optim/${file_path}.bch" "--random-seed=${loop_number}" > "${tools_dir}/outputs/${output_prefix}${file_name}_${run}.txt" &
}



wait_for_jobs() {
    while (( $(jobs | wc -l) >= max_jobs )); do
        sleep 1
    done
}

run_python_script() {
    local alpha=$1
    local max_iter=$2
    local prec=$3
    local tools_dir=$4
    local input_file=$5
    local script=$6
    "$python_interpreter" "$script" --alpha "$alpha" --max_iter "$max_iter" --prec "$prec" --ibex_tools_dir "$tools_dir" --bench_list "$input_file"
}

apply_params(){
    local alpha=$1
    local max_iter=$2
    local prec=$3
    local header_file=$4
    sed -i "s|\(double alpha=\)[^,]*|\1${alpha}|" "$header_file"
	sed -i "s|\(int max_iter=\)[^,]*|\1${max_iter}|" "$header_file"
	sed -i "s|\(double prec=\)[^)]*|\1${prec}|" "$header_file"
}

# Run the baseline benchmark
echo "Running baseline benchmark with parameters alpha=$baseline_alpha, max_iter=$baseline_max_iter, prec=$baseline_prec"
apply_params $baseline_alpha $baseline_max_iter $baseline_prec $header_file
cd ${ibex_dir} && ./waf install > waf_install.log 2>/dev/null
#tail -1 waf_install.log
for run in $(seq 1 $baseline_num_runs); do
    echo "Starting run $run out of $baseline_num_runs"
    counter=1
    while read -r file_path; do
        wait_for_jobs
        execute_ibexopt_baseline $file_path $run 1 "true"
        ((counter++))
    done < "$input_file"
    wait
done
run_python_script $baseline_alpha $baseline_max_iter $baseline_prec $tools_dir $input_file $python_script_baseline

# Now proceed with the main loop for other parameter combinations
loop_number=1
for alpha in "${alpha_values[@]}"; do
    for max_iter in "${max_iter_values[@]}"; do
        for prec in "${prec_values[@]}"; do
	    echo "Starting loop $loop_number out of $num_combinations: parameters alpha=$alpha, max_iter=$max_iter, prec=$prec"
            apply_params $alpha $max_iter $prec $header_file
            cd ${ibex_dir} && ./waf install > waf_install.log 2>/dev/null
	    #tail -1 waf_install.log
            for run in $(seq 1 $num_runs); do
                echo "Starting run $run out of $num_runs"
                counter=1
                while read -r file_path; do
                    wait_for_jobs
                    execute_ibexopt $file_path $run $loop_number "false"
                    ((counter++))
                done < "$input_file"
                wait
            done
            run_python_script $alpha $max_iter $prec $tools_dir $input_file $python_script
            ((loop_number++))
        done
    done
done