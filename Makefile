SHELL = /bin/bash

# Environments
export VCS_URL          := $(shell git config --get remote.origin.url)
export VCS_REF          := $(shell git rev-parse --short HEAD)
export BUILD_DATE       := $(shell date -u +"%Y-%m-%dT%H:%M:%SZ")


## Targets ----

.PHONY: help
help: ## This help.
	@sort $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-.]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' 

.DEFAULT_GOAL := help

.PHONY: build
build:  ## Builds all images (uses cache)
	docker-compose build

.PHONY: build-nc
build-nc: ## Builds all images from scratch
	docker-compose build --no-cache

.PHONY: deploy
publish:  ## TODO: Tags images and pushes to dockerhub's registry
	echo TODO: tagging images and pushing to dockerhub ...
	#docker-compose push

.venv: ## builds python environment and installs tooling for this repo
	python3 -m venv .venv
	.venv/bin/pip install --upgrade pip setuptools wheel
	.venv/bin/pip install pip-tools

.PHONY: clean
clean: ## Cleans all unversioned files in project
	@git clean -dxf