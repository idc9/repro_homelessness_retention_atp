from os.path import join
import os
import argparse

from explore.BlockBlock import BlockBlock

from repro_hvr.load_and_process_data import load_and_process
from repro_hvr.utils import get_results_df

# setup paths
parser = argparse.ArgumentParser(description='Simulation with sparse Pi.')
parser.add_argument('--top_dir', default='./', type=str,
                    help='Directory where the data lives and the results should be stored.')

args = parser.parse_args()
data_dir = join(args.top_dir, 'data')
save_dir = join(args.top_dir, 'results')
os.makedirs(save_dir, exist_ok=True)


# load data
fpath = join(data_dir, 'homeless_database_10-9-20.sav')
covar, cts_cols, cat_cols, ret_intvals = load_and_process(fpath)
print(covar.shape)
print(covar)


# run comparisonts between homeless and all other covariates
bb = BlockBlock(alpha=0.05,
                multi_test='fdr_bh',  # how to handle multiple comparisons
                nan_how='drop',  # drop nans
                cat_test='auc')  # permutation test for cat vs cts
bb.fit(covar['Homelessness'],
       covar.drop(columns=['Homelessness']))
bb.correct_multi_tests()


results = get_results_df(bb)
results.to_csv(join(save_dir, 'homelessness_vs_covariates_results.csv'))
