

# load packages  -----------------------------------------------------------------


# install required packages
# borrowed from https://stackoverflow.com/questions/9341635/check-for-installed-packages-before-running-install-packages
requiredPackages = c('mgm','tidyverse')
for(p in requiredPackages){
    if(!require(p,character.only = TRUE)) install.packages(p)
    library(p,character.only = TRUE)
}

library(mgm)
library(tidyverse)


# setup paths -------------------------------------------------------------
args = commandArgs(trailingOnly=TRUE)
if (length(args)==0) {
    # stop("At least one argument must be supplied", call.=FALSE)
    top_dir <- './'
    top_dir <- '/Users/iaincarmichael/Dropbox/Research/substance_abuse/homelessness_vs_retention/repro_homelessness_retention/'
} else{
    top_dir <- args[1]
}
print(top_dir)

temp_save_dir = str_c(top_dir, 'temp_data/')
save_dir = str_c(top_dir, 'results/')


# cov_fpath = str_c(temp_save_dir, 'covariates.csv')  # raw covariates with NaNs
cov_fpath = str_c(temp_save_dir, 'covariates_imputed.csv')

surv_int_fpath = str_c(temp_save_dir, 'ret_intvals.csv')
cat_cols_fpath = str_c(temp_save_dir, 'cat_cols.csv')

# load data ---------------------------------------------------------------

covar <- read_csv(cov_fpath) %>%  select(-EncPatientID)  # drop subject ids
cat_cols <- read_csv(cat_cols_fpath)[[1]]
surv_interval <- read_csv(surv_int_fpath) %>%  select(-EncPatientID)  # drop subject ids
dim(covar)

var_names <- colnames(covar)

# TODO: what to do about this
# covar <- covar %>% filter(work != '0.0')

# code missing with a string
for (col in cat_cols){
    values <- covar[, col][[1]] %>% as.character
    print(str_c(col, ' has ', sum(is.na(values)), ' missing values'))
    values[is.na(values)] <- 'missing'
    covar[, col] <- values %>%  as.factor
}


# format data for input to mgm
n_features <- dim(covar)[2]
col_types <- map(covar, class)
dtypes <- rep('g', n_features)
n_levels <- rep(1, n_features)
X <- matrix(NA, nrow=dim(covar)[1], ncol=n_features)
for(j in 1:n_features){
    if(col_types[[j]] == 'factor'){
        dtypes[j] <- 'c'
        n_levels[j] <- covar[, j][[1]] %>% levels %>% length

        X[, j] <- as.numeric(covar[, j][[1]]) - 1

        print(colnames(covar)[j])
        for(l in 0:(n_levels[j]-1)){

            print(str_c(l, ' ', sum(X[, j] == l)))
        }
        print('')
        print('')
    } else{
        X[, j] <- covar[, j][[1]]
    }
}
colnames(X) <- colnames(covar)


# fit graphical model -----------------------------------------------------


covar_gm <- mgm(data=X, type=dtypes, level=n_levels)


# output results ----------------------------------------------------------


A <- round(covar_gm$pairwise$wadj, 2)
rownames(A) <- colnames(covar)
colnames(A) <- colnames(covar)
A[1, ]
names(A[1, ][A[1, ] > 0 ])


# Visualize using qgraph()
library(qgraph)

png(file=str_c(save_dir, 'graphical_model.png'),
    width=2000, height=1600, # res=5000,
    pointsize=15)
qgraph(covar_gm$pairwise$wadj,
       edge.color = covar_gm$pairwise$edgecolor,
       layout = "spring",
       lty=covar_gm$pairwise$edge_lty,
       labels =  colnames(covar))


dev.off()

# save adjacency matrix
adj_mat <- covar_gm$pairwise$wadj
rownames(adj_mat) <- colnames(covar)
colnames(adj_mat) <- colnames(covar)
write.csv(adj_mat, file=str_c(save_dir, 'graphical_model_adj_mat.csv'))



