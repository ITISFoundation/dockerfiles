# Minimal makefile to confortably build tool
#
# REFERENCE: https://itnext.io/docker-makefile-x-ops-sharing-infra-as-code-parts-ea6fa0d22946
#

# PROJECT_NAME defaults to name of the current directory.
# should not to be changed if you follow GitOps operating procedures.
PROJECT_NAME = $(notdir $(CURDIR))


.PHONY: build clean prune
all: build

build:
	# builds docker image ${PROJECT_NAME}
	@docker build --tag local/${PROJECT_NAME} .

clean:
	# remove created images
	@docker image rm -f local/$(PROJECT_NAME):latest 2>/dev/null \
	&& echo 'Image(s) for "$(PROJECT_NAME)" removed.' \
	|| echo 'Image(s) for "$(PROJECT_NAME)" already removed.'

prune:
	# clean all that is not actively used
	docker system prune -af
