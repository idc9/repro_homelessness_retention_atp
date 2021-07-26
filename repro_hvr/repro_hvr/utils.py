import pandas as pd

from explore.ContCat import ContCat
from explore.ContBinCat import ContBinCat
from explore.CatCat import CatCat


def get_results_df(comp):
    """
    Saves the results of an explore object to a csv file.

    Parameters
    ----------
    comp: explore.BlockBlock
        A fit block vs. block comparison object.

    Output
    ------
    results: pd.DataFrame
        A csv version of the results.
    """
    results = []
    for var in comp.comparisons_.columns:
        tst = comp.comparisons_.iloc[0, :][var]

        if isinstance(tst, ContCat):
            tst = tst.comparisons_

        if isinstance(tst, CatCat):
            stat = tst.chi2_
            stat_name = 'chi2'

        elif isinstance(tst, ContBinCat):
            stat = tst.stat_
            stat_name = 'AUC'

        results.append({'variable': var,
                        'p_adj': tst.pval_adj_,
                        'is_stat_sig': tst.pval_adj_ < 0.05,
                        'stat_value': stat,
                        'stat_name': stat_name,
                        'p_raw': tst.pval_raw_})

    return pd.DataFrame(results).set_index('variable')
