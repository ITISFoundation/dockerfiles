#
#
# Main targets for https://github.com/ITISFoundation/osparc-ops.git
#
#
.DEFAULT_GOAL := help
SHELL         := /bin/bash
# including .env file used for development
-include .env

# Environments
export VCS_URL          := $(shell git config --get remote.origin.url)
export VCS_REF          := $(shell git rev-parse --short HEAD)
export BUILD_DATE       := $(shell date -u +"%Y-%m-%dT%H:%M:%SZ")

# TODO: all folders with a $(folder)/docker-compose.yml or $(folder)/.docker-compose-build.yml inside
PROJECTS := \
	devpi \
	pip-kit \
	qooxdoo-kit \
	rabbitmq \
	docker-registry-sync

docker_compose_configs = $(foreach folder,$(PROJECTS),$(CURDIR)/$(folder)/docker-compose.yml)

## Targets ----
.PHONY: help
help: ## This colourful help
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-.]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.docker-compose-build.yml: $(docker_compose_configs)
	docker compose $(foreach dc,$^,-f $(dc)) config >$@

.PHONY: build
build: .docker-compose-build.yml ## Builds all images (uses cache)
	# building $$(PROJECTS)
	docker compose -f $< build --parallel

.PHONY: build-nc
build-nc: .docker-compose-build.yml ## Builds all images from scratch
	docker compose -f $< build --parallel --no-cache

.PHONY: devenv
devenv: .venv ##  Nuilds python environment and installs some tooling for operations
.venv:
	python3 -m venv .venv
	.venv/bin/pip install --upgrade pip setuptools wheel
	.venv/bin/pip install pip-tools

.PHONY: clean
clean: ## Cleans all unversioned files in project
	@echo -n "Are you sure? [y/N] " && read ans && [ $${ans:-N} = y ]
	@git clean -dxf

.PHONY: info-tools
info-tools: ## displays tools versions
	@echo dev-tools versions -------------------------
	@echo ' awk           : $(shell awk -W version 2>&1 | head -n 1)'
	@echo ' docker        : $(shell docker --version)'
	@echo ' docker buildx : $(shell docker buildx version)'
	@echo ' docker compose: $(shell docker compose version)'
	@echo ' jq            : $(shell jq --version)'
	@echo ' make          : $(shell make --version 2>&1 | head -n 1)'
	@echo ' node          : $(shell node --version 2> /dev/null || echo ERROR nodejs missing)'
	@echo ' python        : $(shell python3 --version)'
	@echo ' uv            : $(shell uv --version 2> /dev/null || echo ERROR uv missing)'
	@echo ' ubuntu        : $(shell lsb_release --description --short 2> /dev/null | tail || echo ERROR Not an Ubuntu OS )'
