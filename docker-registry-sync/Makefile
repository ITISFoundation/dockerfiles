.DEFAULT_GOAL := help

BRIDGE_NETWORK_NAME := dev_sync_net

export IMAGE_NAME := docker-registry-sync
export DOCKER_REG_SYNC_VERSION := 0.3.1
export DOCKER_REGISTRY ?=itisfoundation

export VCS_URL         := $(shell git config --get remote.origin.url)
export VCS_REF         := $(shell git rev-parse --short HEAD)
export BUILD_DATE      := $(shell date -u +"%Y-%m-%dT%H:%M:%SZ")

current_dir = $(shell pwd)


.PHONY: help
help: ## help on rule's targets
	@awk 'BEGIN {FS = ":.*?## "} /^[[:alpha:][:space:]_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# DEPENDENCIES

.PHONY: _ensure-in-venv
_ensure-in-venv:
	@python3 -c "import os; os.environ['VIRTUAL_ENV']" || (echo "\n>>>> You are not in a virtualenv. Activate one <<<<\n"; exit 1)

.PHONY: compile-dependencies
compile-dependencies: _ensure-in-venv ## snapshot dependencies
	@uv pip compile --build-isolation reposync/requirements/base.in --output-file reposync/requirements/base.txt 
	@uv pip compile --build-isolation reposync/requirements/test.in --output-file reposync/requirements/test.txt 
	@uv pip compile --build-isolation reposync/requirements/tools.in --output-file reposync/requirements/tools.txt 


.PHONY: install-test
install-test: _ensure-in-venv ## install package test dependencies
	@cd reposync/requirements; uv pip sync test.txt 

.PHONY: install-dev
install-dev: _ensure-in-venv ## install package test dependencies
	@cd reposync/requirements; uv pip sync dev.txt

.PHONY: install-ci
install-ci: _ensure-in-venv ## install package test dependencies
	@cd reposync/requirements; uv pip sync ci.txt


.PHONY: install-py-package
install-py-package: _ensure-in-venv ## install package dependencies
	@pip install -e reposync

.PHONY: tests
tests: _ensure-in-venv ## install package dependencies
	@tox -r -c reposync/tox.ini


##### DEVELOPMENT UTILS

.PHONY: setup-env
setup-env: ## creates the .env still need to change your credentials
	cp .env.default .env

.PHONY: start-dev-registry
start-dev-registry: ## starts development registries used by development-run
	@docker network create ${BRIDGE_NETWORK_NAME}
	@docker compose -f dev/docker-compose.dev.yaml up -d

.PHONY: stop-dev-registry
stop-dev-registry: ## stops development registries used by development-run
	@docker compose -f dev/docker-compose.dev.yaml down
	@docker network rm ${BRIDGE_NETWORK_NAME}
	@sudo rm -rf dev/data_*

.PHONY: shell
shell: _ensure-in-venv build ## check internals of image
	@docker run --rm -it \
		--env-file .env \
		--network=${BRIDGE_NETWORK_NAME} \
		--entrypoint /bin/sh \
		${DOCKER_REGISTRY}/${IMAGE_NAME}:${DOCKER_REG_SYNC_VERSION}

.PHONY: development-run
development-run: _ensure-in-venv build ## used to test out changes during development
	@docker run --rm -it \
		--env-file .env \
		-v $(current_dir)/dev/dev-sync-cfg.yml:/etc/cfg.yaml \
		--network=${BRIDGE_NETWORK_NAME} \
		${DOCKER_REGISTRY}/${IMAGE_NAME}:${DOCKER_REG_SYNC_VERSION} \
		run-reposync -c /etc/cfg.yaml

# CI & RELEASE

.PHONY: build
build: ## build and tag the iamge
	@docker compose build

.PHONY: push
push: ## Pushes image to Docker Hub only if the tag does not exist
	@echo "Checking if tag ${DOCKER_REG_SYNC_VERSION} exists in ${DOCKER_REGISTRY}/${IMAGE_NAME}..."
	@if [ "$(shell curl -s -o /dev/null -w "%{http_code}" https://hub.docker.com/v2/repositories/${DOCKER_REGISTRY}/${IMAGE_NAME}/tags/${DOCKER_REG_SYNC_VERSION}/)" = "404" ]; then \
		echo "Tag does not exist. Pushing image..."; \
		docker push ${DOCKER_REGISTRY}/${IMAGE_NAME}:${DOCKER_REG_SYNC_VERSION}; \
	else \
		echo "Tag already exists. Skipping push."; \
	fi

.PHONY: tests-isolated
tests-isolated:	## reserved for Git Hub CI to start testsuite
	echo "Running tests in isolation"
	docker run --rm \
		-v $(current_dir):/code \
		-w /code \
		python:3.11-buster \
		sh -c ' export VIRTUAL_ENV=1 && \
				cd /code && \
				make install-ci \
				make tests'
