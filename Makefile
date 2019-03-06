SHELL = /bin/bash

##
# Definitions.
.SUFFIXES:



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
all: build


.PHONY: build
# target: build – Builds all images
build: .env 
	${DOCKER_COMPOSE} build --no-cache


.PHONY: .env
.env:
	@echo VCS_REF=$(shell git rev-parse --short HEAD)           >.env
	@echo VCS_URL=$(shell git config --get remote.origin.url)  >>.env
	@echo BUILD_DATE=$(shell date -u +"%Y-%m-%dT%H:%M:%SZ")    >>.env


.PHONY: clean
# target: clean – Cleans all unversioned files in project
clean:
	@git clean -dxf


.PHONY: help
# target: help – Display all callable targets
help:
	@echo
	@egrep "^\s*#\s*target\s*:\s*" [Mm]akefile \
	| $(SED) -r "s/^\s*#\s*target\s*:\s*//g"
	@echo