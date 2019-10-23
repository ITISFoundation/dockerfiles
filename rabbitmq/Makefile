.DEFAULT_GOAL   := help
RABBIT_VERSION  :=3.8.0-management
DOCKER_REGISTRY ?=itisfoundation

VCS_URL         := $(shell git config --get remote.origin.url)
VCS_REF         := $(shell git rev-parse --short HEAD)
BUILD_DATE      := $(shell date -u +"%Y-%m-%dT%H:%M:%SZ")

.PHONY: help
help: ## displays targets
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "%-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: build
build: ## builds image
	@docker build --build-arg VERSION=$(RABBIT_VERSION) \
		--label org.label-schema.schema-version=1.0 \
        --label org.label-schema.build-date=${BUILD_DATE} \
        --label org.label-schema.vcs-url=${VCS_URL} \
        --label org.label-schema.vcs-ref=${VCS_REF} \
		--tag $(DOCKER_REGISTRY)/rabbitmq:$(RABBIT_VERSION) \
		$(CURDIR)

.PHONY: push
push: ## pushes image to Dockerhub
	@docker push $(DOCKER_REGISTRY)/rabbitmq:$(RABBIT_VERSION)

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
