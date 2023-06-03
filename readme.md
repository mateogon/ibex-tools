# Ibex Optimization Benchmark Automation

This project automates the running and benchmarking of optimization tasks using the Ibex library's `ibexopt` tool. The project includes two main scripts: `run.py`, which orchestrates the running of the optimization tasks, and `parse_results.py`, a script which processes the output of the tasks to extract relevant statistics.

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

After all runs are completed, the script will call the specified Python script (parse_results.py) to parse the output files and consolidate the results into a single CSV file. Subsequently, it invokes the generate_results() function to create a comprehensive CSV file 'combined_results_data.csv' which includes improvement statistics and identifies the best parameters per file.
