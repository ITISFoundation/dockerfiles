DOCKER_REPO        = itisfoundation
APP_NAME           = $(notdir $(PWD))
DOCKER_IMAGE_NAME  = $(DOCKER_REPO)/$(APP_NAME)
VERSION_SNAPSHOT  := $(shell date +0.0.%Y%m%d-%H%M%S)

TMPPREFIX := /tmp/$(APP_NAME)
TMPDIR    := $(strip $(shell mktemp -d $(TMPPREFIX)-XXXXX))

# Environments (affect docker-compose.yml)
export VCS_URL    := $(shell git config --get remote.origin.url)
export VCS_REF    := $(shell git rev-parse --short HEAD)
export BUILD_DATE := $(shell date -u +"%Y-%m-%dT%H:%M:%SZ")



.PHONY: help
# thanks to https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
help: ## This help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help


# Build the container
.PHONY: build build-nc

build: ## Build the container
	export DOCKER_REPO=itisfoundation; \
	export VERSION=lastbuild; \
	docker-compose build $(APP_NAME)

build-nc: ## Build the container without caching
	export DOCKER_REPO=itisfoundation; \
	export VERSION=lastbuild; \
	docker-compose build --no-cache $(APP_NAME)


# Docker tagging
.PHONY: tag tag-latest tag-version

tag: tag-latest tag-version ## Generate container tags for the `{version}` and `latest` tags

tag-latest: ## Generate container `latest` tag
	@echo 'create tag latest'
	docker tag $(DOCKER_IMAGE_NAME):lastbuild $(DOCKER_IMAGE_NAME):latest

tag-version: ## Generate container `{version}` tag
	@echo 'create tag $(VERSION_SNAPSHOT)'
	docker tag $(DOCKER_IMAGE_NAME):lastbuild $(DOCKER_IMAGE_NAME):$(VERSION_SNAPSHOT)
	@echo $(VERSION_SNAPSHOT) >VERSION


# Docker publish
PHONY: publish publish-latest publish-version release

publish: publish-latest publish-version ## Publish the `{version}` and `latest` tagged containers to ECR

publish-latest: tag-latest ## Publish the `latest` tagged container to ECR
	@echo 'publish latest to $(DOCKER_REPO)'
	docker push $(DOCKER_IMAGE_NAME):latest

publish-version: tag-version ## Publish the `{version}` tagged container to ECR
	@echo 'publish $(shell cat VERSION) to $(DOCKER_REPO)'
	docker push $(DOCKER_IMAGE_NAME):$(shell cat VERSION)

release: build-nc publish ## Make a release by building and publishing the `{version}` ans `latest` tagged containers to ECR


# Misc tools
.PHONY: shell
shell: ## opens shell in container
	@echo "Writing '$(TMPDIR)/test-run.sh' ..."
	@echo "qx create myapp -t desktop -I" >>$(TMPDIR)/test-run.sh
	@echo "cd myapp; qx compile -t build" >>$(TMPDIR)/test-run.sh
	@echo "qx serve" >>$(TMPDIR)/test-run.sh
	docker run -it -v $(TMPDIR):/project -p 8080:8080 -w /home/node $(DOCKER_IMAGE_NAME):lastbuild /bin/sh


.PHONY: info
info:
	@echo Installed versions
	@export PROJECT_DIR=$(TMPDIR); \
		docker-compose run -w /home/node --rm $(APP_NAME) jq '.dependencies' package.json
	@echo Labels; \
		docker image inspect $(DOCKER_IMAGE_NAME):lastbuild --format="{{.ContainerConfig.Labels}}"


.PHONY: info
clean:
	@git clean -ndf
	-rm -rf $(wildcard $(TMPPREFIX)*)
	docker image rm -f $(docker images itisfoundation/qooxdoo* -q) 
