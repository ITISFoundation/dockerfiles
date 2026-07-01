#
# qooxdoo-kit
#
.DEFAULT_GOAL := help

export DOCKER_REPO ?= itisfoundation
APP_NAME           = $(notdir $(PWD))
DOCKER_IMAGE_NAME  = $(DOCKER_REPO)/$(APP_NAME)

# Multi-architecture build settings
DOCKER_TARGET_PLATFORMS ?= linux/amd64
# Image version is derived from the bundled qooxdoo compiler (same scheme as rabbitmq pinning RABBIT_VERSION)
DOCKER_IMAGE_VERSION    := $(shell jq -r '.dependencies."@qooxdoo/compiler".version' package-lock.json)
DOCKER_IMAGE_DATE       := $(shell date +0.0.%Y%m%d-%H%M%S)
DOCKER_IMAGE_TAGS       ?= latest $(DOCKER_IMAGE_VERSION) $(DOCKER_IMAGE_DATE)
DIGESTS_DIR             ?= /tmp/$(APP_NAME)-digests
comma := ,

TMPPREFIX := /tmp/$(APP_NAME)
TMPDIR    := $(strip $(shell mktemp -d $(TMPPREFIX)-XXXXX))

# Environments (affect docker-compose.yml)
export VCS_URL    := $(shell git config --get remote.origin.url)
export VCS_REF    := $(shell git rev-parse --short HEAD)
export BUILD_DATE := $(shell date -u +"%Y-%m-%dT%H:%M:%SZ")

# Installed versions
export QOOXDOO_COMPILER_VERSION  := $(shell jq '.dependencies."@qooxdoo/compiler".version'  package-lock.json)
export QOOXDOO_FRAMEWORK_VERSION := $(shell jq '.dependencies."@qooxdoo/compiler".dependencies."@qooxdoo/framework".version'  package-lock.json)
export PUPPETEER_VERSION := $(shell jq '.dependencies."puppeteer".version'  package-lock.json)


.PHONY: help
# thanks to https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
help: ## This help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)


.PHONY: update-packages

# TODO: do this with docker instead! See https://github.com/ITISFoundation/dockerfiles/issues/12
package-lock.json: package.json
	# Updating package-lock.json
	npm update --save-dev --package-lock-only

# TODO:  Requires installing and running npm! make update-packages (see https://flaviocopes.com/update-npm-dependencies/)
update-packages: ## updates dependencies and recreates package-lock.json
	touch package.json
	$(MAKE) package-lock.json

# Build the container
.PHONY: build build-nc

build: package-lock.json ## Build the image for DOCKER_TARGET_PLATFORMS (loaded locally when single-platform)
	docker buildx bake -f docker-compose.build.yml \
	--set *.platform=$(DOCKER_TARGET_PLATFORMS) \
	$(if $(findstring $(comma),$(DOCKER_TARGET_PLATFORMS)),, --load)

build-nc: package-lock.json ## Build the image without caching
	docker buildx bake --no-cache -f docker-compose.build.yml \
	--set *.platform=$(DOCKER_TARGET_PLATFORMS) \
	$(if $(findstring $(comma),$(DOCKER_TARGET_PLATFORMS)),, --load)


# Run the container
.PHONY: shell
# TODO: add make shell cmd=''
# TODO: separate test script?
shell: ## opens shell in container
	# starting container $(APP_NAME) shell on `$(TMPDIR)`
	cp -r tests $(TMPDIR)
	@export VERSION=lastbuild; \
	export PROJECT_DIR=$(TMPDIR);\
	docker compose run $(APP_NAME)


.PHONY: test
test: ## tests
	# Executes tests/run.sh
	cp -r tests $(TMPDIR)
	@export VERSION=lastbuild;
	export PROJECT_DIR=$(TMPDIR);\
	docker compose run $(APP_NAME) /bin/sh ./tests/run.sh


# Docker publish (multi-architecture)
#
# A multi-arch image is produced in two stages so each architecture can be built
# natively (no QEMU emulation):
#   1. `push-digest` is run once per platform/runner. It builds a single-arch
#      image, pushes it to the registry by digest (no tag) and records the digest
#      as an empty file under DIGESTS_DIR.
#   2. `create-manifest` collects every digest in DIGESTS_DIR and combines them
#      into a single multi-arch manifest list tagged with DOCKER_IMAGE_TAGS.
.PHONY: push-digest create-manifest

push-digest: package-lock.json ## Build a single-arch image and push it to the registry by digest
	@mkdir -p $(DIGESTS_DIR)
	BUILDX_NO_DEFAULT_ATTESTATIONS=1 docker buildx bake -f docker-compose.build.yml \
	--set *.platform=$(DOCKER_TARGET_PLATFORMS) \
	--set *.output=type=image,name=$(DOCKER_IMAGE_NAME),push-by-digest=true,name-canonical=true,push=true \
	--metadata-file metadata.json
	@digest=$$(jq -r '."$(APP_NAME)"."containerimage.digest" // empty' metadata.json); \
	test -n "$${digest}" || { echo "ERROR: could not extract image digest from metadata.json"; exit 1; }; \
	touch "$(DIGESTS_DIR)/$${digest#sha256:}"; \
	echo "Pushed $(DOCKER_IMAGE_NAME) by digest $${digest}"

create-manifest: ## Combine per-arch digests from DIGESTS_DIR into a multi-arch manifest list
	@test -n "$$(ls -A $(DIGESTS_DIR) 2>/dev/null)" || { echo "No digests found in $(DIGESTS_DIR)"; exit 1; }
	cd $(DIGESTS_DIR) && docker buildx imagetools create \
	$(foreach tag,$(DOCKER_IMAGE_TAGS),-t $(DOCKER_IMAGE_NAME):$(tag)) \
	$$(printf '$(DOCKER_IMAGE_NAME)@sha256:%s ' *)
	docker buildx imagetools inspect $(DOCKER_IMAGE_NAME):$(firstword $(DOCKER_IMAGE_TAGS))



# Misc tools
.PHONY: info
info: ## shows info
	# Labels in `$(DOCKER_IMAGE_NAME):lastbuild` image (metadata)
	@docker image inspect $(DOCKER_IMAGE_NAME):lastbuild | jq .[0].ContainerConfig.Labels
	# Tagged images
	@docker images $(DOCKER_IMAGE_NAME)*:*

.PHONY: clean
clean:
	@git clean -nXdf
	@echo -n "Are you sure? [y/N] " && read ans && [ $${ans:-N} = y ]
	# cleaning unversioned
	@git clean -Xdf
	# removes all temporary folders
	@-rm -rf $(wildcard $(TMPPREFIX)*)
	# cleans close docker compose
	@-docker compose down

.PHONY: clean-images
clean-images:
	# remove all images as $(DOCKER_IMAGE_NAME)*:*
	@echo -n "Are you sure? [y/N] " && read ans && [ $${ans:-N} = y ]
	-docker image rm -f $(shell docker images $(DOCKER_IMAGE_NAME)*:* -q)

