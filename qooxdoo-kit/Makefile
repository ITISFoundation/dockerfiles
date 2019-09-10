
APP_NAME    = $(notdir $(PWD))
DOCKER_REPO = itisfoundation
VERSION    := $(shell date +0.0.%Y%m%d-%H%M%S)

# Environments
export VCS_URL    := $(shell git config --get remote.origin.url)
export VCS_REF    := $(shell git rev-parse --short HEAD)
export BUILD_DATE := $(shell date -u +"%Y-%m-%dT%H:%M:%SZ")

TMPDIR := $(strip $(shell mktemp -d /tmp/$(APP_NAME)-XXXXX))

.PHONY: help build build-nc test release publish publish-latest publish-version tag tag-latest tag-version

# thanks to https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
help: ## This help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help


# Build the container
build: ## Build the container
	docker-compose build $(APP_NAME)

build-nc: ## Build the container without caching
	docker-compose build --no-cache $(APP_NAME)

release: build-nc publish ## Make a release by building and publishing the `{version}` ans `latest` tagged containers to ECR


.PHONY: shell .script

.script:
	@echo "Writing '$(TMPDIR)/test-run.sh' ..."
	@echo "qx create myapp -t desktop -I" >>$(TMPDIR)/test-run.sh
	@echo "cd myapp; qx compile -t build" >>$(TMPDIR)/test-run.sh
	@echo "qx serve" >>$(TMPDIR)/test-run.sh

shell: .script
	docker run -it -v $(TMPDIR):/project -p 8080:8080 -w /project $(DOCKER_REPO)/$(APP_NAME):latest /bin/sh



# Docker publish
publish: publish-latest publish-version ## Publish the `{version}` ans `latest` tagged containers to ECR

publish-latest: tag-latest ## Publish the `latest` taged container to ECR
	@echo 'publish latest to $(DOCKER_REPO)'
	docker push $(DOCKER_REPO)/$(APP_NAME):latest

publish-version: tag-version ## Publish the `{version}` taged container to ECR
	@echo 'publish $(VERSION) to $(DOCKER_REPO)'
	docker push $(DOCKER_REPO)/$(APP_NAME):$(VERSION)


# Docker tagging
tag: tag-latest tag-version ## Generate container tags for the `{version}` ans `latest` tags

tag-latest: ## Generate container `{version}` tag
	@echo 'create tag latest'
	docker tag $(APP_NAME) $(DOCKER_REPO)/$(APP_NAME):latest

tag-version: ## Generate container `latest` tag
	@echo 'create tag $(VERSION)'
	docker tag $(APP_NAME) $(DOCKER_REPO)/$(APP_NAME):$(VERSION)


clean:
	- rm -rf $(TMPDIR)