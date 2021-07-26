# load packages ------------------------------------------------------------------

# BiocManager::install("Icens")

# install required packages
# borrowed from https://stackoverflow.com/questions/9341635/check-for-installed-packages-before-running-install-packages
requiredPackages = c('tidyverse','interval', 'ALassoSurvIC')
for(p in requiredPackages){
    if(!require(p,character.only = TRUE)) install.packages(p)
    library(p,character.only = TRUE)
}

library(tidyverse)
library(interval)
library(ALassoSurvIC)

# setup paths -------------------------------------------------------------

# setup directories
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

# cov_fpath = str_c(temp_save_dir, 'covariates.csv')
cov_fpath = str_c(temp_save_dir, 'covariates_imputed.csv')

surv_int_fpath = str_c(temp_save_dir, 'ret_intvals.csv')
cat_cols_fpath = str_c(temp_save_dir, 'cat_cols.csv')


# load data ---------------------------------------------------------------

covar <- read_csv(cov_fpath) %>%  select(-EncPatientID)  # drop subject ids
cat_cols <- read_csv(cat_cols_fpath)[[1]]
surv_interval <- read_csv(surv_int_fpath) %>%  select(-EncPatientID)  # drop subject ids

covariates <- colnames(covar)
covar[, 'left'] <- surv_interval[, 'left']
covar[, 'right'] <- surv_interval[, 'right']


# format data -------------------------------------------------------------

# code 'NA' as their own category for categegorical variables
for (col in cat_cols){
    values <- covar[, col][[1]] %>% as.character
    print(str_c(col, ' has ', sum(is.na(values)), ' missing values'))
    values[is.na(values)] <- 'missing'
    covar[, col] <- values %>%  as.factor
}

# standardize continuous columns
# impute missing values with mean for continuous variables
n_features <- dim(covar)[2]
for (j in 1:n_features){
    col_name <- colnames(covar)[j]
    if (!(col_name %in% cat_cols) & !(col_name %in% c('left', 'right'))){
        print(str_c('standarizing ', col_name))

        # standardize
        values <- covar[, j][[1]]
        values <- (values - mean(values, na.rm=T)) / sd(values, na.rm=T)

        # mean impute i.e. replace with 0 since we standardized
        nan_mask <- is.na(values)
        print(str_c(col_name, ' has ', sum(nan_mask), ' missinig values'))
        values[nan_mask] <- 0.0

        covar[, j] <- values
    }
}


# survival vs. homelessness, marginal analysis -----------------------------------------------

homlelessness_surv_curves <- icfit(Surv(left, right, type='interval2')~Homelessness, data=covar)


png(file=str_c(save_dir, 'homelessness_vs_retention_survival_curve.png'),
    width=500, height=400)
plot(homlelessness_surv_curves,
     COL=c('red', 'blue'),
     YLAB='Retention', XLAB='Days',
     shade=FALSE)

dev.off()


homelessness_vs_surv_test <- ictest(Surv(left, right, type='interval2')~Homelessness, data=covar)
print(homelessness_vs_surv_test)

capture.output(print(homelessness_vs_surv_test), file=str_c(save_dir, 'homelessness_vs_retention_log_rank.txt'))


# survival regression -------------------------------------------------------------------

lowerIC <- covar[, 'left'][[1]]
upperIC <- covar[, 'right'][[1]]
upperIC[is.na(upperIC)] = Inf

covar <- covar %>% select(-left, -right)
X <- model.matrix(~., covar)
X <- X[, -1] # remove intercept
dim(X)


mle_reg <- unpencoxIC(lowerIC=lowerIC, upperIC=upperIC, X=X, normalize.X = F)
mle_reg


capture.output(print(mle_reg), file=str_c(save_dir, 'survival_regression_output.txt'))


coef <- mle_reg$b
se <- mle_reg$se
z <- coef/se
p_value_raw <- pnorm(abs(z), lower.tail = FALSE)
ci <- cbind(coef - qnorm(0.975) * se, coef + qnorm(0.975) * se)

p_value_adj <- p.adjust(p_value_raw, method='BH') # 'bonferroni', 'bh'
rej_adj <- p_value_adj < 0.05
var_names <- mle_reg$xnames

results <- tibble(variable=var_names,
                  hazard_ratio=exp(mle_reg$b),
                  hazard_lower_ci=exp(ci[, 1]),
                  hazard_upper_ci=exp(ci[, 2]),
                  p_value_adj=p_value_adj,
                  reject_adj=rej_adj,
                  coef=coef,
                  coef_lower_ci=ci[, 1],
                  coef_upper_ci=ci[, 2],
                  p_raw=p_value_raw) %>% arrange(p_value_raw)

results

write_csv(results, str_c(save_dir, 'survival_regresion.csv'))
