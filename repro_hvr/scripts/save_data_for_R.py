from os.path import join
import pandas as pd
from collections import Counter
import numpy as np
import os
import argparse

from repro_hvr.load_and_process_data import load_and_process
from repro_hvr.impute import impute_with_cats

# setup paths
parser = argparse.ArgumentParser(description='Simulation with sparse Pi.')
parser.add_argument('--top_dir', default='../../', type=str,
                    help='Directory where the data lives and the results should be stored.')

args = parser.parse_args()
data_dir = join(args.top_dir, 'data')
temp_save_dir = join(args.top_dir, 'temp_data')
os.makedirs(data_dir, exist_ok=True)
os.makedirs(temp_save_dir, exist_ok=True)


# load processed data
fpath = join(data_dir, 'homeless_database_10-9-20.sav')
covar, cts_cols, cat_cols, ret_intvals = load_and_process(fpath)


# impute missing
covar_imputed = impute_with_cats(df=covar,
                                 cat_cols=cat_cols,
                                 cts_cols=cts_cols,
                                 n_neighbors=5)[0]

# save to disk
covar.to_csv(join(temp_save_dir, 'covariates.csv'))
covar_imputed.to_csv(join(temp_save_dir, 'covariates_imputed.csv'))
ret_intvals.to_csv(join(temp_save_dir, 'ret_intvals.csv'))
pd.Series(cat_cols).to_csv(join(temp_save_dir, 'cat_cols.csv'), index=False)

# summarize imputation results
for c in covar.columns:
    print('\n\n', c)
    if c in cat_cols:
        print(Counter(covar[c]))
    else:
        print(covar[c].describe())
        print(np.isnan(covar[c]).sum(), 'nans')
