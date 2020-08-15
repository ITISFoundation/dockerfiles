#!/bin/bash
# http://redsymbol.net/articles/unofficial-bash-strict-mode/
set -euo pipefail
IFS=$'\n\t'

#
# As this repo follows the Monorepo pattern, we want to avoid that Travis make a build for every projects each time one project is updated
# This script checks if one project has been updated. Thanks to https://travis-ci.community/t/how-to-skip-jobs-based-on-the-files-changed-in-a-subdirectory/2979/11
#

PATH_TO_SEARCH="$1"

# 3. Get the latest commit
LATEST_COMMIT=$(git rev-parse HEAD)

# 4. Get the latest commit in the searched path
LATEST_COMMIT_IN_PATH=$(git log -1 --format=format:%H --full-diff $PATH_TO_SEARCH)

if [ $LATEST_COMMIT != $LATEST_COMMIT_IN_PATH ]; then
    echo "Exiting this job because code in the following path have not changed:"
    echo $PATH_TO_SEARCH
    exit 1
fi

echo "Paths have changed, the build will be deployed"
exit 0