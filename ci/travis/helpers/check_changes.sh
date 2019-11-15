#
# As this repo is following the Monorepo pattern, we want to avoid that Travis make a build for every projects each time one project is updated
# This script check if one project has been updated.
#
# 1. Get all the arguments of the script
# https://unix.stackexchange.com/a/197794
PATH_TO_SEARCH="$1"

# 3. Get the latest commit
LATEST_COMMIT=$(git rev-parse HEAD)

# 4. Get the latest commit in the searched path
LATEST_COMMIT_IN_PATH=$(git log -1 --format=format:%H --full-diff $PATH_TO_SEARCH)

if [ $LATEST_COMMIT != $LATEST_COMMIT_IN_PATH ]; then
    echo "Exiting this job because code in the following path have not changed:"
    echo $PATH_TO_SEARCH
    travis_terminate 0
fi