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

# array of stages which guarantees order of execution
# you can sync from A to B and from B to C
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

  # more advanced usage
  # pulls all sleeper tags from dockerhub and pushes to master
  - from:
      source: "dockerhub"
      repository: "itisfoundation/sleeper"
    to:
      - destination: master
        repository: "simcore/services/comp/sleeper"
        tags: []
  
  # because the previous stage already synced the images
  # pulls all the tag 1.0.0 of sleeper from master syncs to staging (also in a different namespace)
  - from:
      source: "master"
      repository: "simcore/services/comp/sleeper"
    to:
      - destination: staging
        repository: "simcore/services/comp_v4/sleeper"
        tags: ["1.0.0"]

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

By default if an error occurs during the sync of an image the process is not stopped, but the error message is logged.
If you'd like to cause your process to fail the first time an error occurs you are given the following options:
- a command line flag `--exit-on-first-error`
- an environment variable  `SYNC_EXIT_ON_FIRST_ERROR` which if set will have the same effect as the flag

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
      -e SYNC_EXIT_ON_FIRST_ERROR=true \
      -v $(pwd)/dev/dev-sync-cfg.yml:/etc/cfg.yaml \
      itisfoundation/docker-registry-sync

## Development

Use the provided Makefile for all the needs. There are two commands used to start and stop an array of registries:

    make start-dev-registry
    make stop-dev-registry

You can build and run your changes with (this command requires to run in a virtualenv):

    make development-run


## TODOs

- [ ] add unit testing
- [ ] add integration testing