#!/bin/bash

# reference http://redsymbol.net/articles/unofficial-bash-strict-mode/
set -euo pipefail
IFS=$'\n\t'

python3 /code/print_as_header.py "Listing tooling versions"

python3 --version
make --version
docker --version
docker-compose --version

python3 /code/print_as_header.py "Logging into registry"
echo "--$INPUT_REGISTRY_URL--$INPUT_REGISTRY_USER--"
echo "$INPUT_REGISTRY_PASSWORD" | docker login "$INPUT_REGISTRY_URL" --username "$INPUT_REGISTRY_USER" --password-stdin

python3 /code/print_as_header.py "Switching to project directory '$INPUT_TARGET_PROJECT_PATH_IN_GIT_REPO'"
cd $INPUT_TARGET_PROJECT_PATH_IN_GIT_REPO

python3 /code/print_as_header.py "Trying to pull existing image to enable caching"
DOCKER_REGISTRY=$INPUT_TARGET_REGISTRY_NAME make github-ci-pull  || true

python3 /code/print_as_header.py "Building image"
DOCKER_REGISTRY=$INPUT_TARGET_REGISTRY_NAME make github-ci-build

python3 /code/print_as_header.py "Running tests"
DOCKER_REGISTRY=$INPUT_TARGET_REGISTRY_NAME make github-ci-tests

python3 /code/print_as_header.py "Pushing image"
DOCKER_REGISTRY=$INPUT_TARGET_REGISTRY_NAME make github-ci-push

python3 /code/print_as_header.py "Completed without errors"
