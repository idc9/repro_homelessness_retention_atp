from sklearn.impute import KNNImputer
import numpy as np
import pandas as pd
from itertools import product


def impute_with_cats(df, cat_cols=None, cts_cols=None, sep='___', **kws):
    """
    Parameters
    ----------
    df: pd.DataFrame
        The raw data frame with missing values.

    cat_cols: None, list
        List of the categorical columns that should be imputed.

    cts_cols: None, list
        List of continuous columns that should be imputed.

    sep: str
        Used internally. Should not be included in any of the column names of df.
    kws:
        Key work arguments tosklearn.impute.KNNImputer

    Output
    ------
    df_imputed, imputed_values

    df_imputed: pd.DataFrame
        df but with missing values imptued.

    imputed_values: list of tuples
        The (subj, var, value) tuple for the missing values that were imputed.
    """
    df = pd.DataFrame(df)

    assert not any(sep in c for c in df.columns)

    # get numercal data frame with dummy variables and nans
    X_num, blah = get_dummies_with_nans(df, sep=sep, cat_cols=cat_cols)

    # impute missing values
    X_num_imputed = KNNImputer(**kws).fit_transform(X_num)
    X_num_imputed = pd.DataFrame(X_num_imputed, index=X_num.index,
                                 columns=X_num.columns)

    # get categorical values from imputed values
    df_imputed = df.copy()
    imputed_values = []
    for c in blah.keys():
        is_na_mask = np.isnan(X_num[c])

        cols = blah[c]

        Z = X_num_imputed.loc[is_na_mask, cols]

        for subj, row in Z.iterrows():
            y_hat = row.idxmax()

            var = sep.join(y_hat.split(sep)[:-1])
            value = y_hat.split(sep)[-1]

            df_imputed.loc[subj, var] = value

            imputed_values.append((subj, var, value))

    if cts_cols is not None:
        for subj, col in product(df.index, cts_cols):
            df_imputed.loc[subj, col] = X_num_imputed.loc[subj, col]

    return df_imputed, imputed_values


def is_nan_col(c, sep='__'):
    s = c.split(sep)

    if len(s) == 1:
        return False

    last = s[-1]
    return 'nan' == last


def get_dummies_with_nans(X, sep='___', cat_cols=None):

    X_num = pd.get_dummies(X, dummy_na=True,
                           columns=cat_cols, prefix_sep=sep)

    blah = {}
    for c in X_num.columns:
        if is_nan_col(c, sep=sep):
            blah[c] = []
            stub = c[:-4]
            for col in X_num.columns:
                if stub in col and not is_nan_col(col, sep=sep):
                    blah[c].append(col)

    for c in list(blah.keys()):
        is_na_mask = X_num[c] == 1
        X_num.loc[is_na_mask, c] = np.nan

        for col in blah[c]:
            X_num.loc[is_na_mask, col] = np.nan

        if is_na_mask.sum() == 0:
            X_num = X_num.drop(columns=c)
            del blah[c]

    return X_num, blah
