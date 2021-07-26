from os.path import join
import os
import pandas as pd
# from collections import Counter
import argparse

from repro_hvr.load_and_process_data import load_and_process

# setup paths
parser = argparse.ArgumentParser(description='Simulation with sparse Pi.')
parser.add_argument('--top_dir', default='./', type=str,
                    help='Directory where the data lives and the results should be stored.')

args = parser.parse_args()

args.top_dir = '/Users/iaincarmichael/Dropbox/Research/substance_abuse/homelessness_vs_retention/repro_homelessness_retention'
data_dir = join(args.top_dir, 'data')
save_dir = join(args.top_dir, 'results')
os.makedirs(save_dir, exist_ok=True)
# data_dir = '/Users/iaincarmichael/Dropbox/Research/substance_abuse/homeless_vs_retention/repro_homeless_retention/data/'

# load data
fpath = join(data_dir, 'homeless_database_10-9-20.sav')
covar, cts_cols, cat_cols, ret_intvals = load_and_process(fpath)


#############
# retention #
#############

ret = ret_intvals.join(covar['Homelessness'])

n_homeless = covar.query('Homelessness').shape[0]
n_not_homeless = covar.query('not Homelessness').shape[0]
n_study = covar.shape[0]


dropped_left_counts = \
    {'study': ret['left'].value_counts().sort_index(),

     'homelessness': ret.query("Homelessness")['left'].value_counts().sort_index(),

     'not_homeless': ret.query("not Homelessness")['left'].value_counts().sort_index()}

dropped_left_counts = pd.DataFrame(dropped_left_counts)
dropped_left_counts.index.name = 'drop_out_left_time_point'

dropped_left_props = dropped_left_counts.copy()
dropped_left_props['study'] /= n_study
dropped_left_props['homelessness'] /= n_homeless
dropped_left_props['not_homeless'] /= n_not_homeless

dropped_left_counts.to_csv(join(save_dir, 'dropped_left_time_point_counts.csv'))
dropped_left_props.to_csv(join(save_dir, 'dropped_left_time_point_props.csv'))


def count_dropped_out_by(ret):

    cnts = {}
    for x in [30, 60, 90, 180, 365]:
        cnts[x] = ret.query("left < @x").shape[0]

    cnts = pd.Series(cnts).sort_index()
    cnts.index.name = 'dropped_out_by'
    return cnts


dropped_by_counts = \
    {'study': count_dropped_out_by(ret),

     'homelessness': count_dropped_out_by(ret.query("Homelessness")),

     'not_homeless': count_dropped_out_by(ret.query("not homelessness"))}

dropped_by_counts = pd.DataFrame(dropped_by_counts)

dropped_by_props = dropped_by_counts.copy()
dropped_by_props['study'] /= n_study
dropped_by_props['homelessness'] /= n_homeless
dropped_by_props['not_homeless'] /= n_not_homeless

dropped_by_counts.to_csv(join(save_dir, 'dropped_by_counts.csv'))
dropped_by_props.to_csv(join(save_dir, 'dropped_by_props.csv'))


###########################
# summarize all variables #
###########################

# continuous variables
cts_var_summary = covar[cts_cols].describe()
cts_var_summary.to_csv(join(save_dir, 'continuous_var_summary.csv'))


cts_var_by_homeless_summary = \
    covar[['homelessness'] + cts_cols].groupby('Homelessness').describe().T
cts_var_by_homeless_summary.\
    to_csv(join(save_dir, 'continuous_var_summary_by_homeless.csv'))


# categorical variable summary
covar[cat_cols] = covar[cat_cols].astype(str)  # make sure NaNs are merged

n_tot = covar.shape[0]
n_homeless = covar.query("Homelessness == 'True'").shape[0]
n_not_homeless = covar.query("Homelessness == 'False'").shape[0]

for c in cat_cols:

    cnts = {}
    cnts['study'] = covar[c].value_counts()
    cnts['homelessness'] = covar.query("Homelessness == 'True'")[c].value_counts()
    cnts['not_homeless'] = covar.query("Homelessness == 'False'")[c].value_counts()
    cnts = pd.DataFrame(cnts)

    props = cnts.copy()
    props['study'] /= n_tot
    props['homelessness'] /= n_homeless
    props['not_homeless'] /= n_not_homeless

    print(c)
    print(cnts)
    print()
    print(props)
    print('\n\n\n')

