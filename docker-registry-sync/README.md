# About

This project is built on top of [dregsy](https://github.com/xelalexv/dregsy) with [skopeo](https://github.com/containers/skopeo) relay.


# Usage

Given a configuration file like[dev/dev-sync-cfg.yml](./dev/dev-sync-cfg.yml) (preview below):

```yaml
# Registries contains access credentials to repositories
# these can be used as input (source) or output (destination)
# env_user and env_password refer to environment variables containing the credentials
registries:
  dockerhub:
    # generally used only as source
    url: index.docker.io # dockerhub
    env_user: ENV_VAR_USERNAME_DOCKERHUB
    env_password: ENV_PASSWORD_DOCKERHUB
  master:
    url: master:5000
    env_user: ENV_VAR_USERNAME_MASTER
    env_password: ENV_PASSWORD_MASTER
    skip-tls-verify: true
  staging:
    url: staging:5000
    env_user: ENV_VAR_USERNAME_STAGING
    env_password: ENV_PASSWORD_STAGING
    skip-tls-verify: true
  aws:
    url: aws:5000
    env_user: ENV_VAR_USERNAME_AWS
    env_password: ENV_PASSWORD_AWS
    skip-tls-verify: true

# the scheduler will try to run all stages in parallel
# if a stage has a depends_on key it will wait for previous stages
# to complete before starting
stages:
  # generic usage
  - from:
      source: "dockerhub" # key comes from above registries definition
      repository: "itisfoundation/sleeper"
    to:
      - destination: master # key comes from above registries definition
        repository: "simcore/services/comp/sleeper"
        tags: [] # will take all available tags
      - destination: staging # key comes from registries
        repository: "simcore/services/comp/sleeper"
        tags: ["1.0.0"] # specify a tag
      - destination: aws # key comes from registries
        repository: "simcore/services/comp_v3/sleeper" # different namespace is also allowed
        tags: ["0.0.1", "1.0.0"] # specify multiple tags
    id: "i-am-not-required" # optional, not needed here

  # more advanced usage
  # pulls all sleeper tags from dockerhub and pushes to master
  # to run this stage before another one, give it an id so it can be 
  # referred by other stages
  - from:
      source: "dockerhub"
      repository: "itisfoundation/sleeper"
    to:
      - destination: master
        repository: "simcore/services/comp/sleeper"
        tags: []
    id: "i-run-before"  # needed for the stage below
  
  # because the depends_on tag was added, this stage will wait for the specified
  # stages to complete before starting
  # Please note: if an error occurs in one of the depends_on stages execution
  # still goes on. Error logs will always be displayed if something went wrong
  # for easy debugging
  - from:
      source: "master"
      repository: "simcore/services/comp/sleeper"
    to:
      - destination: staging
        repository: "simcore/services/comp_v4/sleeper"
        tags: ["1.0.0"]
    depends_on: ["i-run-before"]

```

## Checking configuration

It might important to check the configuration, the following example uses the above example to check it. If configuration is OK 
the program will exit with exit code 0, otherwise an error is raised.

    run-reposync -c dev/dev-sync-cfg.yml --verify-only

The above yaml is converted to json and validated via jsonschema [have a look here](reposync/src/reposync/validation.py).

## Running

When starting the process also inject all the environment variables needed by the different registries.

    ENV_VAR_USERNAME_DOCKERHUB=dockerhub_user \
        ENV_PASSWORD_DOCKERHUB=dockerhub_password \
        ENV_VAR_USERNAME_MASTER=testuser \
        ENV_PASSWORD_MASTER=testpassword \
        ENV_VAR_USERNAME_STAGING=testuser \
        ENV_PASSWORD_STAGING=testpassword \
        ENV_VAR_USERNAME_AWS=testuser \
        ENV_PASSWORD_AWS=testpassword \
    run-reposync -c dev/dev-sync-cfg.yml

By default if an error occurs during the sync of an image the process is not stopped, but the error message is logged and the process will exit with code 1 at the end.

The flag `--parallel-sync-tasks` is available to overwrite the default number of 
parallel tasks, set to 100.

## Running in Docker

The project is packaged as a Docker image and this is the standard way to runt it.

    docker run --rm -it \
      -e ENV_VAR_USERNAME_DOCKERHUB=dockerhub_user \
      -e ENV_PASSWORD_DOCKERHUB=dockerhub_password \
      -e ENV_VAR_USERNAME_MASTER=testuser \
      -e ENV_PASSWORD_MASTER=testpassword \
      -e ENV_VAR_USERNAME_STAGING=testuser \
      -e ENV_PASSWORD_STAGING=testpassword \
      -e ENV_VAR_USERNAME_AWS=testuser \
      -e ENV_PASSWORD_AWS=testpassword \
      -v $(pwd)/dev/dev-sync-cfg.yml:/etc/cfg.yaml \
      itisfoundation/docker-registry-sync

## Development

Use the provided Makefile for all the needs. There are two commands used to start and stop an array of registries:

    make start-dev-registry
    make stop-dev-registry

You can build and run your changes with (this command requires to run in a virtualenv):

    make development-run

Make sure you have defined a `.env` file next to this Makefile containing the following:

    ENV_VAR_USERNAME_DOCKERHUB=_YOUR_DOCKER_HUB_USERNAME_
    ENV_PASSWORD_DOCKERHUB=_YOUR_DOCKER_HUB_PASSWORD_
    ENV_VAR_USERNAME_MASTER=testuser
    ENV_PASSWORD_MASTER=testpassword
    ENV_VAR_USERNAME_STAGING=testuser
    ENV_PASSWORD_STAGING=testpassword
    ENV_VAR_USERNAME_AWS=testuser
    ENV_PASSWORD_AWS=testpassword

## TODOs

- [ ] add unit testing
- [ ] add integration testing
