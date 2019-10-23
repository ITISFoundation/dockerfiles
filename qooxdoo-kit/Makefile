PREDEFINED_VARIABLES := $(.VARIABLES)

DOCKER_REPO        = itisfoundation
APP_NAME           = $(notdir $(PWD))
DOCKER_IMAGE_NAME  = $(DOCKER_REPO)/$(APP_NAME)
DOCKER_IMAGE_TAG  := $(shell date +0.0.%Y%m%d-%H%M%S)

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

.DEFAULT_GOAL := help



.PHONY: update-packages

# TODO: do this with docker instead! See https://github.com/ITISFoundation/dockerfiles/issues/12
package-lock.json: package.json
	# Updating package-lock.json
	npm update --save-dev --package-lock-only

# TODO:  make update-packages (see https://flaviocopes.com/update-npm-dependencies/)
update-packages: ## updates dependencies and recreates package-lock.json
	touch package.json
	$(MAKE) package-lock.json


# Build the container
.PHONY: build build-nc

build: package-lock.json ## Build the container
	export VERSION=lastbuild; \
	docker-compose -f docker-compose.build.yml build $(APP_NAME)

build-nc: package-lock.json ## Build the container without caching
	export VERSION=lastbuild; \
	docker-compose -f docker-compose.build.yml build --no-cache $(APP_NAME)


# Run the container
.PHONY: shell
# TODO: add make shell cmd=''
# TODO: separate test script?
shell: ## opens shell in container
	# starting container $(APP_NAME) shell on `$(TMPDIR)`
	cp -r tests $(TMPDIR)
	@export VERSION=lastbuild; \
	export PROJECT_DIR=$(TMPDIR);\
	docker-compose run $(APP_NAME)


.PHONY: test
test: ## tests 
	# Executes tests/run.sh
	cp -r tests $(TMPDIR)
	@export VERSION=lastbuild; 
	export PROJECT_DIR=$(TMPDIR);\
	docker-compose run $(APP_NAME) /bin/sh ./tests/run.sh


# Docker tagging
.PHONY: tag .tag-latest .tag-version

tag: .tag-latest .tag-version ## Generate container tags for the `{version}` and `latest` tags

.tag-latest: 
	# Generate container `latest` tag
	docker tag $(DOCKER_IMAGE_NAME):lastbuild $(DOCKER_IMAGE_NAME):latest

.tag-version: 
	# Generate container `$(DOCKER_IMAGE_TAG)` tag
	docker tag $(DOCKER_IMAGE_NAME):lastbuild $(DOCKER_IMAGE_NAME):$(DOCKER_IMAGE_TAG)
	@echo $(DOCKER_IMAGE_TAG) >.TAG


# Docker publish
PHONY: publish publish-latest publish-version release

publish: .publish-latest .publish-version ## Publish the `{version}` and `latest` tagged containers to ECR

.publish-latest: .tag-latest 
	# Publish the `latest` tagged container to `$(DOCKER_REPO)`
	docker push $(DOCKER_IMAGE_NAME):latest

.publish-version: .tag-version 
	# Publish the $(shell cat .TAG) tagged to `$(DOCKER_REPO)`
	docker push $(DOCKER_IMAGE_NAME):$(shell cat .TAG)

release: publish ## Tags lastbuild and pushes `{version}` and `latest` to ECR



# Misc tools
.PHONY: info 
info: ## shows info
	# Labels in `$(DOCKER_IMAGE_NAME):lastbuild` image (metadata)
	@docker image inspect $(DOCKER_IMAGE_NAME):lastbuild | jq .[0].ContainerConfig.Labels
	# Tagged images 
	@docker images $(DOCKER_IMAGE_NAME)*:*

info-vars: ## info to debug makefile
	$(info # Variables)
	$(foreach v,                                                                           \
		$(filter-out $(PREDEFINED_VARIABLES) PREDEFINED_VARIABLES, $(sort $(.VARIABLES))), \
		$(info $(v)=$($(v)))                                                               \
	)

.PHONY: clean clean-images .check_clean
clean: .check_clean
	# cleans unversioned
	@git clean -Xdf
	# removes all temporary folders
	@-rm -rf $(wildcard $(TMPPREFIX)*)
	# cleans close docker-compose
	@-docker-compose down

clean-images: .check_clean
	# remove all images
	-docker image rm -f $(shell docker images $(DOCKER_IMAGE_NAME)*:* -q)

.check_clean:
	@echo -n "Are you sure? [y/N] " && read ans && [ $${ans:-N} = y ]
