#!/bin/bash
# http://redsymbol.net/articles/unofficial-bash-strict-mode/
set -euo pipefail
IFS=$'\n\t'

#
# This script compare the version given in parameter to the latest version present in the repository. Fail if the given version <= repository version
#

#
# Compare two versions in the format X.X.X. Return $1 >= $2
# Thanks to http://ask.xmodulo.com/compare-two-version-numbers.html
#

function version_gt() 
{
     test "$(echo "$@" | tr " " "\n" | sort -V | head -n 1)" != "$1"     
}


# Variables
APP_USER_VERSION=$1
DOCKER_REPO=$2
APP_NAME=$3

LAST_DIGEST=$(curl -s "https://hub.docker.com/v2/repositories/$DOCKER_REPO/$APP_NAME/tags/latest" | jq '.images[0].digest')

# List of tags based on the last digest
TAGS_LAST_DIGEST=$(curl -s "https://hub.docker.com/v2/repositories/$DOCKER_REPO/$APP_NAME/tags" | jq -c ".results | map(select( any(.images[]; .digest==$LAST_DIGEST)))")
LAST_VERSION=$( echo $TAGS_LAST_DIGEST | jq -c '.[] | select(.name|test("^([0-9]+).([0-9]+).([0-9]+)")) | .name' | tr -d \")

echo "The last version on the repo is currently : $LAST_VERSION"


if $(version_gt $APP_USER_VERSION $LAST_VERSION); then
     echo "A release would update from $LAST_VERSION to $APP_USER_VERSION on Dockerhub."
     exit 0;
else
     echo "There is a problem in your versionning, the last version on the repository is $LAST_VERSION and you are trying to push the version $APP_USER_VERSION" >&2
     exit 1;
fi