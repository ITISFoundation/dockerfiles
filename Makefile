SHELL = /bin/bash

##
# Definitions.

.SUFFIXES:

VCS_REF:=$(shell git rev-parse --short HEAD)
BUILD_DATE:=$(shell date -u +"%Y-%m-%dT%H:%M:%SZ")

export VCS_REF
export BUILD_DATE


## Tools.

tools =

ifeq ($(shell uname -s),Darwin)
	SED = gsed
else
	SED = sed
endif

DOCKER = docker
DOCKER_COMPOSE = docker-compose


## Targets .

.PHONY: all
# target: all – Builds all images
all:
	${DOCKER_COMPOSE} build --no-cache



.PHONY: clean
# target: clean – Cleans all unversioned files in project
clean:
	@git clean -dxf -e .vscode/


.PHONY: help
# target: help – Display all callable targets
help:
	@echo
	@egrep "^\s*#\s*target\s*:\s*" [Mm]akefile \
	| $(SED) -r "s/^\s*#\s*target\s*:\s*//g"
	@echo