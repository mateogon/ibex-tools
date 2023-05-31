#!/bin/bash

# Variable definitions


ibex_dir="/home/mateo/Desktop/ibex-lib"          # Directory of ibex-lib
tools_dir=$(dirname "$(realpath "$0")")       # Directory of ibex-tools
input_file="${tools_dir}/bench_list"                  # Name of the input file
python_interpreter="/usr/bin/python3"    # Python interpreter location
python_script="${tools_dir}/create_baseline.py" # Python script location
ibexopt="${ibex_dir}/__build__/src/ibexopt" # ibexopt location
header_file="${ibex_dir}/src/loup/ibex_LoupFinderIterative.h" # Header file location

num_runs=10                              # Number of runs
alpha_values=(0.9) #(0.8 0.9 1.0)0.9,int max_iter=10, double prec=1e-3
max_iter_values=(10) #(5 10 15)
prec_values=(1e-3) #(1e-4 1e-3 1e-2)


# Maximum number of parallel jobs, adjust this to the number of CPU cores on your machine
max_jobs=$(nproc) #$(getconf _NPROCESSORS_ONLN) #

loop_number=1

for alpha in "${alpha_values[@]}"; do
    for max_iter in "${max_iter_values[@]}"; do
        for prec in "${prec_values[@]}"; do
	    echo "Starting loop $loop_number for parameters alpha=$alpha, max_iter=$max_iter, prec=$prec"
	    sed -i "s|\(double alpha=\)[^,]*|\1${alpha}|" "$header_file"
	    sed -i "s|\(int max_iter=\)[^,]*|\1${max_iter}|" "$header_file"
	    sed -i "s|\(double prec=\)[^)]*|\1${prec}|" "$header_file"



            cd ${ibex_dir} && ./waf install > waf_install.log 2>/dev/null
	    tail -1 waf_install.log

            for run in $(seq 1 $num_runs); do
                echo "Starting run $run out of $num_runs"
                counter=1

                while read -r file_path; do
                    file_name=$(basename "${file_path}")
                    echo "Starting execution for: $file_name ($counter out of $(wc -l < "$input_file"))"

                    while (( $(jobs | wc -l) >= max_jobs )); do
                        sleep 1
                    done

                    "${ibexopt}" "${ibex_dir}/benchs/optim/${file_path}.bch" > "${tools_dir}/outputs/baseline_${file_name}_${run}.txt" && echo "Finished execution for: $file_name" &

                    ((counter++))
                done < "$input_file"

                wait

            done
            echo "Running python script"
            "$python_interpreter" "$python_script" --alpha "$alpha" --max_iter "$max_iter" --prec "$prec" --ibex_tools_dir "$tools_dir" --bench_list "$input_file"

            ((loop_number++))
        done
    done
done

