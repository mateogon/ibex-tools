import pandas as pd
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--file', type=str, required=True)
parser.add_argument('--time', type=float, required=True)
args = parser.parse_args()

df = pd.read_csv(args.file, index_col='file')

under_threshold = df[df['avg_time'] < args.time]

print("Files with an average time of less than {} seconds:".format(args.time))
for file_name in under_threshold.index:
    print(file_name)
    
#python /home/mateo/Desktop/ibex-tools/filter_by_time.py --file /home/mateo/Desktop/ibex-tools/bench_data_202305171757_alpha0.8_maxIter5_prec0.0001.csv --time 2