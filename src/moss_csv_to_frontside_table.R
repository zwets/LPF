#install: gt, webshot,
#webshot::install_phantomjs()

library(dplyr)
library(webshot)
library(scales)
library(gt)
#target_dir,
args <- commandArgs(trailingOnly = TRUE)
target_dir <- sprintf("%s", args[1])
readfile <- read.csv(sprintf("%s%s", target_dir, "amr.csv"))
readfile <- subset(readfile, select = -c(Class, Match))
readfile$Resistance <- gsub("No resistance", 'S', readfile$Resistance)
readfile$Resistance <- gsub("Resistant", 'R', readfile$Resistance)

gt_tbl <- readfile %>% 
  gt()%>%
  tab_header(
    title = md("**Antimicrobial resistance**")
  ) %>%
  tab_options(
    table.font.size = px(24L)
  )
gtsave(gt_tbl, "amr_table.png", path = target_dir)

