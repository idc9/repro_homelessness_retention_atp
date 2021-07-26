#!/bin/sh

#########
# setup #
#########

conda environment
conda create -n repro_hvr python=3.6
conda activate repro_hvr
conda install jupyter
conda install nb_conda
conda install ipykernel

pip install repro_hvr/

# Manually install the explore package
pip install git+https://github.com/idc9/explore.git@v0.1


script_dir="scripts/"
top_dir="/Users/iaincarmichael/Dropbox/Research/substance_abuse/homelessness_vs_retention/repro_homelessness_retention/"

#####################
# run analysis code #
#####################
python "$script_dir"save_data_for_R.py --top_dir "$top_dir"
python "$script_dir"homelessness_vs_covariates.py --top_dir "$top_dir"

Rscript "$script_dir"surivival_analysis.R
Rscript "$script_dir"fit_graphical_model.R
