.DEFAULT_GOAL   := help
export PYTHON_VERSION :=3.8.10
export PENNSIEVE_VERSION  :=0.3.5
export DOCKER_REGISTRY ?=itisfoundation

export VCS_URL         := $(shell git config --get remote.origin.url)
export VCS_REF         := $(shell git rev-parse --short HEAD)
export BUILD_DATE      := $(shell date -u +"%Y-%m-%dT%H:%M:%SZ")

.PHONY: help
help: ## displays targets
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "%-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: build
build: ## builds image
	@docker buildx bake --file docker-compose.yml

.PHONY: push
push: ## pushes image to Dockerhub
	@docker push $(DOCKER_REGISTRY)/pennsieve-agent:${PYTHON_VERSION}-${PENNSIEVE_VERSION}

.PHONY: pull
pull: ## pulls image from Dockerhub
	@docker pull $(DOCKER_REGISTRY)/pennsieve-agent:${PYTHON_VERSION}-${PENNSIEVE_VERSION}

.PHONY: run
run: ## runs the image
	@docker run $(DOCKER_REGISTRY)/pennsieve-agent:${PYTHON_VERSION}-${PENNSIEVE_VERSION}

define show-meta
	$(foreach iid,$(shell docker images */$(1):* -q | sort | uniq),\
		docker image inspect $(iid) | jq '.[0] | .RepoTags, .ContainerConfig.Labels';)
endef

.PHONY: info
info: ## gives some information about the docker image
	@docker images */pennsieve-agent:*;\
	$(call show-meta,pennsieve-agent)
