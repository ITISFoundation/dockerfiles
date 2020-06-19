# About

`action-build-and-push` is a customized github action used to build and publish images to a registry (default is **Docker Hub**).

## Requirements

To configure the action the following inputs are required:

- `REGISTRY_URL`[optional] url of the Docker registry defaults to Docker Hub
- `REGISTRY_USER`[**mandatory**] registry username
- `REGISTRY_PASSWORD`[**mandatory**] registry password or access token
- `TARGET_PROJECT_PATH`[**mandatory**] registry password or access token

Inside the `TARGET_PROJECT_PATH` the action expects to find a Makefile as the following commands will be issued:

- `make github-ci-pull` will attempt to pull a previous image, this command may fail and the action will continue
- `make github-ci-build` builds the image
- `make github-ci-tests` runs the tests packaged with the image
- `make github-ci-push` pushes the image to the registry

