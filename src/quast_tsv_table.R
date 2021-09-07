#install: gt, webshot,
#webshot::install_phantomjs()

library(dplyr)
library(webshot)
library(scales)
library(gt)
#target_dir,
args <- commandArgs(trailingOnly = TRUE)
target_dir <- sprintf("%s", args[1])
readfile <- read.csv(sprintf("%s%s", target_dir, "quast_output/report.tsv"), sep = "\t")
#readfile <- subset(readfile, select = -c(Assembly, assembly))

gt_tbl <- readfile %>%
  gt()%>%
  tab_header(
    title = md("**Assmebly statistics**")
  ) %>%
  tab_options(
    table.font.size = px(24L)
  )
gtsave(gt_tbl, "quast_table.png", path = target_dir)
