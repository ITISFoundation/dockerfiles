# About

`action-build-and-push` is a customized github action used to build and publish images to a registry (default is **Docker Hub**).

## Requirements

To configure the action the following inputs are required:

- `REGISTRY_URL`[optional] url of the Docker registry defaults to Docker Hub
- `REGISTRY_USER`[**mandatory**] registry username
- `REGISTRY_PASSWORD`[**mandatory**] registry password or access token
- `TARGET_REGISTRY_NAME`[**mandatory**] identifies the final namespace where to push the image (might be different from the login name)
- `TARGET_PROJECT_PATH_IN_GIT_REPO`[**mandatory**] name of the folder and project name to be uploaded to Docker Hub

Inside the folder pointed by `TARGET_PROJECT_PATH_IN_GIT_REPO` the action expects to find a Makefile as the following commands will be issued:

- `make github-ci-pull` will attempt to pull a previous image (used as caching stage), this command may fail and the action will continue
- `make github-ci-build` builds the image
- `make github-ci-tests` runs the tests packaged with the image
- `make github-ci-push` pushes the image to the registry

