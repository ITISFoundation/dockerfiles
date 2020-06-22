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
docker login -u "$INPUT_REGISTRY_USER" -p "$INPUT_REGISTRY_PASSWORD" $INPUT_REGISTRY_URL

python3 /code/print_as_header.py "Switching to project directory '$INPUT_TARGET_PROJECT_PATH'"
cd $INPUT_TARGET_PROJECT_PATH

python3 /code/print_as_header.py "Trying to pull existing image to enable caching"
DOCKER_REGISTRY=$INPUT_REGISTRY_USER make github-ci-pull  || true

python3 /code/print_as_header.py "Building image"
DOCKER_REGISTRY=$INPUT_REGISTRY_USER make github-ci-build

python3 /code/print_as_header.py "Running tests"
DOCKER_REGISTRY=$INPUT_REGISTRY_USER make github-ci-tests

python3 /code/print_as_header.py "Pushing image"
DOCKER_REGISTRY=$INPUT_REGISTRY_USER make github-ci-push

python3 /code/print_as_header.py "Completed without errors"
