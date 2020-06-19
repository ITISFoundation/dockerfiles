.DEFAULT_GOAL := help

IMAGE_NAME := docker-registry-sync
BRIDGE_NETWORK_NAME := dev_sync_net

current_dir = $(shell pwd)


.PHONY: help
help: ## help on rule's targets
	@awk 'BEGIN {FS = ":.*?## "} /^[[:alpha:][:space:]_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

##### PYTHON PACKAGE -START

.PHONY: _ensure-in-venv
_ensure-in-venv:
	@python3 -c "import os; os.environ['VIRTUAL_ENV']" || (echo "\n>>>> You are not in a virtualenv. Activate one <<<<\n"; exit 1)


.PHONY: dev-dependencies
dev-dependencies: _ensure-in-venv ## install development depenencies in your venv
	@pip install pip-tools black rope


.PHONY: compile-dependencies
compile-dependencies: _ensure-in-venv ## snapshot dependencies
	@pip-compile --build-isolation $(current_dir)/reposync/requirements/base.in --output-file $(current_dir)/reposync/requirements/base.txt 
	@pip-compile --build-isolation $(current_dir)/reposync/requirements/test.in --output-file $(current_dir)/reposync/requirements/test.txt 


.PHONY: install-dependencies
install-dependencies: _ensure-in-venv ## install package dependencies
	@pip install -r $(current_dir)/reposync/requirements/base.txt 


.PHONY: install-py-package
install-py-package: _ensure-in-venv ## install package dependencies
	@pip install -e reposync

##### PYTHON PACKAGE - END

.PHONY: start-dev-registry
start-dev-registry: ## starts development registries used by development-run
	@docker network create ${BRIDGE_NETWORK_NAME}
	@docker-compose -f dev/docker-compose.dev.yaml up -d

.PHONY: stop-dev-registry
stop-dev-registry: ## stops development registries used by development-run
	@docker-compose -f dev/docker-compose.dev.yaml down
	@docker network rm ${BRIDGE_NETWORK_NAME}
	@sudo rm -rf dev/data_*

.PHONY: development-run
development-run: _ensure-in-venv build ## used to test out changes during developmen
	@docker run --rm -it \
		-e ENV_VAR_USERNAME_DOCKERHUB=dockerhub_user \
		-e ENV_PASSWORD_DOCKERHUB=dockerhub_password \
		-e ENV_VAR_USERNAME_MASTER=testuser \
		-e ENV_PASSWORD_MASTER=testpassword \
		-e ENV_VAR_USERNAME_STAGING=testuser \
		-e ENV_PASSWORD_STAGING=testpassword \
		-e ENV_VAR_USERNAME_AWS=testuser \
		-e ENV_PASSWORD_AWS=testpassword \
		-e SYNC_EXIT_ON_FIRST_ERROR=true \
		-v $(current_dir)/dev/dev-sync-cfg.yml:/etc/cfg.yaml \
		--network=${BRIDGE_NETWORK_NAME} \
		${IMAGE_NAME}


.PHONY: build
build: ## build and tag the iamge
	@docker run --rm --entrypoint cat xelalex/dregsy@sha256:9b0fe252cb8bf88f67871efd6559ef89b76013c46dfbc49b961d396a4b8d1887  /usr/local/bin/dregsy > dregsy
	@docker build -t ${IMAGE_NAME} . --progress=plain
