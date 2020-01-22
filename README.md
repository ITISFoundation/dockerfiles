# dockerfiles

[![Build Status](https://travis-ci.com/ITISFoundation/dockerfiles.svg?branch=master)](https://travis-ci.com/ITISFoundation/dockerfiles)

A collection of curated dockefiles used to develop great software at the [IT'IS Foundation](https://itis.swiss/)

## Why?

During our development workflow we use a great variety of thirdparty software tools (e.g. compilers, debuggers, package managers, ...) or services (e.g. CI services, artifacts repositories, monitoring services, ...) . Each of these have a very specific setup and version which is tuned to our needs at that point in time. Encapsulating all these tools in containers allows us to *snapshot* the tool/service and using it anytime without having to deal with tedious installation  following some wiki step-by-step instructions.

This repo keeps a curated list of dockerfiles that are continuously deployed into our public [itis-dockerhub](https://hub.docker.com/u/itisfoundation) repo.

## Usage

```console
$ make help
help                 This colourful help
build                Builds all images (uses cache)
build-nc             Builds all images from scratch
devenv               Builds python environment and installs some tooling for operations
clean                Cleans all unversioned files in project
```

## Guidelines

Here some of the guidelines we have collected so far:

1. Every container MUST be defined on its own folder and in a ``Dockerfile``

   1. ``Dockerfile``s SHALL be written following [best practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)

2. Every image MUST include some of the labels defined in [label-schema.org](http://label-schema.org/rc1/)

3. One of the image names MUST be formatted as ``itisfoundation/${folder-name}:${tag}``.

4. Releases MUST be tagged according to [semantic versioning](https://semver.org/) and the corresponding alias (e.g. ``latest``, ``X.Y``, etc)

5. Every image MUST build from ``make build``

6. Containers SHALL not address many applications at once

   1. One application per container is the prefered setup. E.g. the ``cookiecutter`` containers runs the application with the same name

   2. If this is not the case, they SHALL be refered as toolkits. For instance, ``pip-kit`` is a container with several python package management tools that can run with many applications, namely ``pip-sync``, ``pip-compile``, ``pipdeptree`` and ``pipreqs``

7. Containers with mounted volumes MUST run using the same uid:gid as the mounted volume.

8. Configuration information SHALL be passed into the container as environment variables prefixed with the name of the container.

9. The "payload" of the container SHALL be run with 'exec' at the end of the `entrypoint.sh` script to make sure signals get passed properly.

10. If the "payload" has no explicit internal signal handling add tini as an init replacement (same effect as when running the docker with --init)
  https://github.com/krallin/tini


## References

Selection of publications worth reading on this topic:

- [Docker & Makefile | X-Ops — sharing infra-as-code parts](https://itnext.io/docker-makefile-x-ops-sharing-infra-as-code-parts-ea6fa0d22946)
- [Auto-documented makefiles](https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html)
