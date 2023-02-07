#!/usr/bin/env bash

# This script updates the schemes in the repository to the latest version.
# The script assumes that the current working directory is the root of the
# repository.

# The script requires the following tools:
# - curl
# - jq
# - xcodebuild

wget -O schemes/phenotypes.txt https://bitbucket.org/genomicepidemiology/resfinder_db/raw/HEAD/phenotypes.txt
wget -O schemes/notes.txt https://bitbucket.org/genomicepidemiology/virulencefinder_db/raw/HEAD/notes.txt