.DEFAULT_GOAL   := help
export RABBIT_VERSION  :=3.13.7-management
export DOCKER_REGISTRY ?=itisfoundation
DOCKER_TARGET_PLATFORMS ?= linux/amd64
comma := ,

export VCS_URL         := $(shell git config --get remote.origin.url)
export VCS_REF         := $(shell git rev-parse --short HEAD)
export BUILD_DATE      := $(shell date -u +"%Y-%m-%dT%H:%M:%SZ")

.PHONY: help
help: ## displays targets
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "%-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: build
build: ## builds image
	@docker buildx bake \
	--set *.platform=$(DOCKER_TARGET_PLATFORMS) \
	$(if $(findstring $(comma),$(DOCKER_TARGET_PLATFORMS)),, --load)
	

.PHONY: shell
shell: ## builds image
	@docker run -it $(DOCKER_REGISTRY)/rabbitmq:$(RABBIT_VERSION) bash

.PHONY: push
push: ## pushes multi-arch image to Dockerhub
	docker buildx bake --set *.platform=linux/amd64,linux/arm64 --push

.PHONY: pull
pull: ## pulls image from Dockerhub
	@docker pull $(DOCKER_REGISTRY)/rabbitmq:$(RABBIT_VERSION)

define show-meta
	$(foreach iid,$(shell docker images */$(1):* -q | sort | uniq),\
		docker image inspect $(iid) | jq '.[0] | .RepoTags, .ContainerConfig.Labels';)
endef

.PHONY: info
info: ## gives some information about the docker image
	@docker images */rabbitmq:*;\
	$(call show-meta,rabbitmq)
