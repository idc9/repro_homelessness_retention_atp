import pandas as pd
import numpy as np


def load_and_process(fpath, use_display_names=True):
    """
    Loads and processes the raw data. This includes subsetting to interesting variables, renaming variables to more interpretable names, getting retention intervals, etc.

    Parameters
    ----------
    fpath: str
        Path to raw data file.

    use_display_names: bool
        Return data frames with the more human readable display variable names.

    Output
    ------
    covariates, cts_cols, cat_cols, retention_intervals

    covariates: pd.DataFrame (n_subjects, n_features)
        The covariates indexed by  EncPatientID.

    cts_cols: list of str
        The column names of the continuous covariates.

    cat_cols: list of str
        The column names of the categorical covariates.

    retention_intervals: pd.DataFrame, (n_subjects, 2)
        The retention intervals.
    """
    # load in data
    df = pd.read_spss(fpath)

    # subset to columns of interest and set index
    # df = df[cols2keep]
    df['EncPatientID'] = df['EncPatientID'].astype(int)
    df = df.set_index('EncPatientID')

    # subset to house or shelter
    df['shelter'] = df['shelter'].astype(bool)
    df['house'] = df['house'].astype(bool)
    df = df[df['house'] | df['shelter']]
    assert (df['shelter'] & df['house']).sum() == 0

    # rename shelter to homelessness
    df = df.rename(columns={'shelter': 'homelessness'})

    # change race to white vs. non-white
    assert df['race'].isna().sum() == 0
    df['race_white'] = df['race'] == 'White'

    # is hispanic
    df['is_hispanic'] = df['hispanic'] == 'hispanic'

    # change school to HS or more vs not
    assert df['school'].isna().sum() == 0
    df['hs_or_more'] = df['school'] >= 3

    # student lasat 30 days
    df['student_last_30'] = df['student'].replace({0: np.nan,
                                                   1: 'yes',
                                                   2: 'no'})

    # rename no_one
    assert df['no_one'].isna().sum() == 0
    df = df.rename(columns={'no_one': 'no_support'})
    df['no_support'] = df['no_support'].astype(bool)

    # format work
    df['work'] = df['work'].replace({0: np.nan,
                                     1.0: 'no',
                                     2.0: '1_10',
                                     3.0: '11_30',
                                     4.0: 'at_least_30'})

    # marital status
    df['ever_married'] = 'no'
    df.loc[df['marital'] == 1, 'ever_married'] = 'yes'
    df.loc[df['marital'] == 0, 'ever_married'] = np.nan

    # any volunteering
    assert df['volunteer'].isna().sum() == 0
    df['any_volunteer'] = df['volunteer'] >= 2.0

    # any benefits
    ben_cols = ['benefits_1', 'benefits_2', 'benefits_3', 'benefits_4']
    assert df[ben_cols].isna().sum().sum() == 0
    df[ben_cols] = df[ben_cols].astype(bool)
    df['any_benefits'] = df['benefits_2'] | df['benefits_3'] | df['benefits_4']

    # format PAPAS
    df = df.rename(columns={'PAPAS1': 'pain_3_months_ever'})
    df['pain_3_months_ever'] = df['pain_3_months_ever'].replace({0.0: 'no'})
    df['pain_3_months_ever'] = df['pain_3_months_ever'].replace({1.0: 'yes'})

    df = df.rename(columns={'PAPAS2': 'pain_3_months_current'})
    df['pain_3_months_current'] = df['pain_3_months_current'].\
        replace({0.0: 'no'})
    df['pain_3_months_current'] = df['pain_3_months_current'].\
        replace({1.0: 'yes'})

    # reformat SA
    assert df['SA'].isna().sum() == 0
    df['sexual_abuse'] = df['SA'] == 'yes'

    # reformat PA
    assert df['PA'].isna().sum() == 0
    df['physical_abuse'] = df['PA'] == 'yes'

    # smoking every day last 30 days
    df['smoke_every_last_30'] = 'no'
    df.loc[df['ATQ2'] == 1, 'smoke_every_last_30'] = 'yes'
    df.loc[df['ATQ2'].isna(), 'smoke_every_last_30'] = np.nan

    # any marijuana last 30 days
    df['marijuana_last_30'] = 'no'
    df.loc[df['ATQ4e'] == 1, 'marijuana_last_30'] = 'yes'
    df.loc[df['ATQ4e'].isna(), 'marijuana_last_30'] = np.nan

    # ecig every day last 30
    df['ecig_every_last_30'] = 'no'
    df.loc[df['ATQ6'] == 1, 'ecig_every_last_30'] = 'yes'
    df.loc[df['ATQ6'].isna(), 'ecig_every_last_30'] = np.nan

    # get retention data
    ret_cols = ['Ret30', 'Ret60', 'Ret90', 'Ret180', 'Ret365']
    retention = df[ret_cols]  # 1 means retained
    retention.columns = [30, 60, 90, 180, 365]
    retention = retention.astype(bool)
    retention_intervals = get_intervals_from_retention(retention)

    cts_cols = ['subabuse', 'overall', 'age']
    # 'depres', 'relation', 'selfharm', 'emotlab', 'psychosis',

    # -1 codes for nan
    for c in cts_cols:
        df[c] = df[c].replace(-1, np.nan)

    cat_cols = ['homelessness',

                'sex', 'ever_married', 'is_hispanic', 'student_last_30',
                'race_white', 'hs_or_more',
                'no_support', 'work', 'any_volunteer', 'any_benefits',

                'pain_3_months_ever', 'pain_3_months_current',

                'sexual_abuse', 'physical_abuse',

                'smoke_every_last_30', 'ecig_every_last_30',
                'marijuana_last_30'
                ]

    covariates = df[cat_cols + cts_cols]

    display_var_names = {'subabuse': 'Substance use',

                         'overall': 'Overall psychological distress', # TODO

                         'age': 'Age',

                         'homelessness': 'Homelessness',

                         'sex': 'Sex', # TODO: this should be M or F

                         'ever_married': 'Ever married',

                         'is_hispanic': 'Hispanic',

                         'student_last_30': 'Recent student',

                         'race_white': 'White/Caucasian', # TODO

                         'hs_or_more': 'At least high school',

                         'no_support': 'No social support',

                         'work': 'Recent employment',

                         'any_volunteer': 'Recent volunteering',

                         'any_benefits': 'Received benefits',

                         'pain_3_months_ever': 'Lifetime chronic pain',

                         'pain_3_months_current': 'Current chronic pain',

                         'sexual_abuse': 'Sexual assault',

                         'physical_abuse': 'Physical assault',

                         'smoke_every_last_30': 'Recent tobacco use',

                         'ecig_every_last_30': 'Recent electronic cigarette',

                         'marijuana_last_30': 'Recent cannabis use'
                         }

    if use_display_names:
        covariates = covariates.rename(columns=display_var_names)
        cts_cols = [display_var_names[c] for c in cts_cols]
        cat_cols = [display_var_names[c] for c in cat_cols]

    return covariates, cts_cols, cat_cols, retention_intervals


def get_intervals_from_retention(retention, verbose=True):
    """
    Gets the retention intervals.
    """
    back_and_forth_subj = find_back_and_forth_subj(retention)

    if verbose:
        print(len(back_and_forth_subj), 'subjects went back and forth')

    # process survival interval data
    surv_interval = pd.DataFrame(index=retention.index,
                                 columns=['left', 'right'])
    check_in_times = retention.columns
    for subj, row in retention.iterrows():

        if sum(row) == 0:  # left before first check in
            surv_interval.loc[subj, 'left'] = 0
            surv_interval.loc[subj, 'right'] = check_in_times[0]

        elif all(row):  # stayed for all check ins
            surv_interval.loc[subj, 'left'] = 365

        else:
            idx_depart = np.where(~row.values)[0].min()

            if idx_depart == 0:
                surv_interval.loc[subj, 'left'] = 0
                surv_interval.loc[subj, 'right'] = check_in_times[0]
            else:
                surv_interval.loc[subj, 'left'] = check_in_times[idx_depart - 1]
                surv_interval.loc[subj, 'right'] = check_in_times[idx_depart]

    return surv_interval


def find_back_and_forth_subj(retention):
    """
    Finds subjects that left and re-entered
    """
    # check for bad survival
    back_and_forth_subj = []
    for subj, row in retention.iterrows():

        for i in range(len(row) - 1):

            if not row.iloc[i]:  # left at earlier time point
                # assert not row.iloc[i + 1]
                if row.iloc[i + 1]:  # back at later time point
                    back_and_forth_subj.append(subj)

    return back_and_forth_subj
