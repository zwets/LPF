#! /usr/bin/env RScript
dir.create(Sys.getenv("R_LIBS_USER"), recursive = TRUE)  # create personal library
.libPaths(Sys.getenv("R_LIBS_USER"))  # add to the path
install.packages(c('gt', 'webshot', 'dplyr'))
webshot::install_phantomjs()