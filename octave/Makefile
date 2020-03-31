.DEFAULT_GOAL := help

export APP_NAME    := $(notdir $(PWD))
export APP_VERSION := $(shell cat VERSION)

DOCKER_REPO = itisfoundation
DOCKER_IMAGE_NAME  = $(DOCKER_REPO)/$(APP_NAME)
DOCKER_IMAGE_VERSION_FULL = $(shell cat VERSION)
DOCKER_IMAGE_VERSION_TWO_DIGITS = $(shell cat VERSION | grep -Eo '^([0-9]+)\.([0-9])+')
DOCKER_IMAGE_VERSION_FIRST_DIGIT = $(shell cat VERSION | grep -Eo '^([0-9]+)')
DOCKER_IMAGE_TAG_COMMIT = $(shell git rev-parse HEAD)

TMPPREFIX := /tmp/$(APP_NAME)
TMPDIR    := $(strip $(shell mktemp -d $(TMPPREFIX)-XXXXX))

# Environments (affect docker-compose.yml)
export VCS_URL     := $(shell git config --get remote.origin.url)
export VCS_REF     := $(shell git rev-parse --short HEAD)
export BUILD_DATE  := $(shell date -u +"%Y-%m-%dT%H:%M:%SZ")
export DOCKER_REPO := $(DOCKER_REPO)


.PHONY: help
# thanks to https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
help: ## this colourful help
	@echo "usage: make [target] ..."
	@echo ""
	@echo "Targets for '$(notdir $(CURDIR))':"
	@echo ""
	@awk --posix 'BEGIN {FS = ":.*?## "} /^[[:alpha:][:space:]_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""


# Build the container
.PHONY: build build-nc

build:  ## Build the container
	docker-compose build $(APP_NAME) 

build-nc:  ## Build the container without caching
	docker-compose build --no-cache $(APP_NAME)

.PHONY: shell
shell: ## opens 
	docker-compose run \
		--volume=$(PWD)/samples:/home/scu \
		--entrypoint /bin/sh \
		$(APP_NAME) 

.PHONY: test
test: _check_version ## Run the tests 
	docker-compose run --detach \
		--volume=$(PWD)/samples:/home/scu \
		$(APP_NAME) script.m

.PHONY: up  down
up: ## Launch the container
	docker-compose up

down: ## Stop the container
	docker-compose down

# Docker tagging
.PHONY: tag 
tag: ## Generate the differents tags from the version. For example 1.2.5 will generate the tags 1, 1.2 and 1.2.5 plus the hash commit.
	docker tag $(DOCKER_IMAGE_NAME):latest $(DOCKER_IMAGE_NAME):$(DOCKER_IMAGE_VERSION_FULL)
	docker tag $(DOCKER_IMAGE_NAME):latest $(DOCKER_IMAGE_NAME):$(DOCKER_IMAGE_VERSION_TWO_DIGITS)
	docker tag $(DOCKER_IMAGE_NAME):latest $(DOCKER_IMAGE_NAME):$(DOCKER_IMAGE_VERSION_FIRST_DIGIT)
	docker tag $(DOCKER_IMAGE_NAME):latest $(DOCKER_IMAGE_NAME):$(DOCKER_IMAGE_TAG_COMMIT)


# Docker publish
.PHONY: release _check_version ## Build, add tags and push everything to ECR
release: _check_version build tag 
	docker push $(DOCKER_IMAGE_NAME):latest
	docker push $(DOCKER_IMAGE_NAME):$(DOCKER_IMAGE_VERSION_FULL)
	docker push $(DOCKER_IMAGE_NAME):$(DOCKER_IMAGE_VERSION_TWO_DIGITS)
	docker push $(DOCKER_IMAGE_NAME):$(DOCKER_IMAGE_VERSION_FIRST_DIGIT)
	docker push $(DOCKER_IMAGE_NAME):$(DOCKER_IMAGE_TAG_COMMIT)

_check_version: # Check if the current version of the app is > to the repository version.
	 ./../check_versions.sh $(DOCKER_IMAGE_VERSION_FULL) $(DOCKER_REPO) $(APP_NAME)

# Misc tools
.PHONY: info
info: ## Shows info
	# Labels in `$(DOCKER_IMAGE_NAME):lastbuild` image (metadata)
	@docker image inspect $(DOCKER_IMAGE_NAME):latest | jq .[0].ContainerConfig.Labels
	# Tagged images 
	@docker images $(DOCKER_IMAGE_NAME)*:*


.PHONY: clean clean-images _check_clean
clean: _check_clean ## Cleans unversioned files/foldersm remove all temporary foleds and close docker compose.
	# cleans unversioned
	@git clean -Xdf
	# removes all temporary folders
	@-rm -rf $(wildcard $(TMPPREFIX)*)
	# cleans close docker-compose
	@-docker-compose down

clean-images: _check_clean ## Remove all images concerning the current app
	$(shell docker rmi -f $$(docker images |grep $(DOCKER_IMAGE_NAME)))

_check_clean:
	@echo -n "Are you sure? [y/N] " && read ans && [ $${ans:-N} = y ]
