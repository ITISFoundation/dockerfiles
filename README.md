# dockerfiles

A collection of curated dockefiles used to develop great software at the [IT'IS Foundation](https://itis.swiss/)

## Why?

During our development workflow we use a great variety of thirdparty software tools (e.g. compilers, debuggers, package managers, ...) or services (e.g. CI services, artifacts repositories, monitoring services, ...) . Each of these have a very specific setup and version which is tuned to our needs at that point in time. Encapsulating all these tools in containers allows us to *snapshot* the tool/service and using it anytime without having to deal with tedious installation  following some wiki step-by-step instructions.

This repo keeps a curated list of dockerfiles that are continuously deployed into our public [itis-dockerhub](https://hub.docker.com/u/itisfoundation) repo.

## Usage

#### Running tools

```console
$ docker run -it itisfoundation/pip-kit --help
```

#### Developing

```console
$ make help
all – Builds all images
build – Builds all images
clean – Cleans all unversioned files in project
help – Display all callable targets
```

## Guidelines

Here some of the guidelines we have collected so far:

1. Every container MUST be defined on its own folder and in a ``Dockerfile``

   1. ``Dockerfile``s SHALL be written following [best practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)

2. Every image MUST include some of the labels defined in [label-schema.org](http://label-schema.org/rc1/)

3. One of the image names MUST be formatted as ``itisfoundation/${folder-name}:${tag}``

4. Every image MUST build from ``make build`` (see [docker-compose](docker-compose.yaml))

5. Containers SHALL not address many applications at once

   1. One application per container is the prefered setup. E.g. the ``cookiecutter`` containers runs the application with the same name

   2. If this is not the case, they SHALL be refered as toolkits. For instance, ``pip-kit`` is a container with several python package management tools that can run with many applications, namely ``pip-sync``, ``pip-compile``, ``pipdeptree`` and ``pipreqs``

7. Containers with mounted volumes MUST run using the same uid:gid as the mounted volume.

8. Configuration information shall be passed into the container as environment variables prefixed with the name of the container. See `devpi/entrypoint.sh` for inspiration.
