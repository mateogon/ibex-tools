# Ibex Optimization Benchmark Automation

This project automates the running and benchmarking of optimization tasks using the Ibex library's `ibexopt` tool. The project includes three main scripts: `run.py`, which orchestrates the running of the optimization tasks, `parse_results.py`, a script which processes the output of the tasks to extract relevant statistics, and `generate_results_csv.py`, a script that generates a combined CSV file containing the results of different test cases and their respective improvements over a baseline.

## Requirements

- [Ibex library](http://www.ibex-lib.org/) installed and built
- Python 3 installed, along with the [Pandas](https://pandas.pydata.org/) library

## Instructions

### Setup

Modify the `run.py` script to set the correct paths for your environment:

- `ibex_dir`: Directory where ibex-lib is located.
- `tools_dir`: Directory where ibex-tools and your output files are located.
- `input_file`: Name of the input file containing the list of benchmarks to run.
- `python_interpreter`: Location of your Python 3 interpreter. (Run `where python3` to find out)
- `python_script`: Location of the Python script used to parse the results (`parse_results.py`).
- `ibexopt`: Location of the `ibexopt` executable.
- `header_file`: Location of the Ibex header file where the parameters are defined.
- `num_runs`: Number of runs for each benchmark.
- `max_jobs`: Maximum number of parallel jobs. Adjust this to the number of CPU cores on your machine.
- `alpha_values`, `max_iter_values`, `prec_values`: Arrays of parameter combinations to test in your optimization tasks.
- `baseline_alpha`, `baseline_max_iter`, `baseline_prec`, `baseline_num_runs`: Parameters for the baseline run.

Once the paths and parameters are correctly set up, you are ready to run the script.

### Execution

The script `run.py` is a Python script, so it does not need to be made executable like a shell script.

To start the benchmark tests, run:

```bash
sudo /bin/python3 /path/to/your/run.py

```

Replace /path/to/your/run.py with the actual path to your run.py script.

The script will print its progress to the console and create output files for each benchmark run in the outputs directory of your tools_dir.

After all runs are completed, the script will call the specified Python script (parse_results.py) to parse the output files and consolidate the results into a single CSV file for each parameter combination. Subsequently, it invokes the generate_results() function to create a comprehensive CSV file `combined_results_data.csv` which includes improvement statistics and identifies the best parameters per file.

## Output CSV File Columns Explanation

The script `generate_results_csv.py` generates a combined CSV file `combined_results_data.csv` containing two main sections: `Best Parameters per File` and `All Parameter Configurations`.

### Best Parameters per File

This section contains the following columns:

- `file`: The file name of the test case.
- `parameters`: The configuration parameters extracted from the file name.
- `avg_time_best`: The average time of the best performing configuration for the test case.
- `avg_time_baseline`: The average time of the baseline for the test case.
- `improvement_best`: The improvement percentage of the best configuration over the baseline for the test case.

### All Parameter Configurations

This section contains the following columns:

- `parameters`: The configuration parameters.
- `count_best`: The number of times the parameters configuration was the best.
- `mean_improvement_best`: The mean improvement of the best cases for this configuration.
- `std_dev_improvement_best`: The standard deviation of the improvement of the best cases for this configuration.
- `min_improvement_best`: The minimum improvement of the best cases for this configuration.
- `max_improvement_best`: The maximum improvement of the best cases for this configuration.
- `mean_improvement_all`: The mean improvement of all cases for this configuration.
- `std_dev_improvement_all`: The standard deviation of the improvement of all cases for this configuration.
- `min_improvement_all`: The minimum improvement of all cases for this configuration.
- `max_improvement_all`: The maximum improvement of all cases for this configuration.
- `total_time_improvement`: The total time improvement for this configuration.

These metrics are used to analyze and compare the performance of different parameter configurations and to identify the best performing configurations for different optimization tasks.
