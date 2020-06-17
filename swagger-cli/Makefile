# Minimal makefile to confortably build tool
#
# REFERENCE: https://itnext.io/docker-makefile-x-ops-sharing-infra-as-code-parts-ea6fa0d22946
#

# PROJECT_NAME defaults to name of the current directory.
# should not to be changed if you follow GitOps operating procedures.
PROJECT_NAME = $(notdir $(CURDIR))

test-fixtures:= api-with-examples.yaml link-example.yaml



.PHONY: build clean prune test
all: build

build:
	# builds docker image ${PROJECT_NAME}
	@docker build --tag local/${PROJECT_NAME} .
	# TODO: add swagger-cli version in labels


$(test-fixtures):
	@wget --no-verbose https://raw.githubusercontent.com/OAI/OpenAPI-Specification/master/examples/v3.0/$@


test: $(test-fixtures)
	# test it runs
	@docker run -it local/${PROJECT_NAME}:latest --version
	# bundles $(word 2,$^)
	@docker run \
		-v $(CURDIR):/specs \
		local/${PROJECT_NAME}:latest \
		bundle --dereference --type yaml --outfile /specs/bundled.yaml /specs/$(word 2,$^)
	# validates $<
	@docker run \
		-v $(CURDIR):/specs \
		local/${PROJECT_NAME}:latest \
		validate --debug /specs/$<

clean:
	git clean -Xdf
	# remove created images
	@docker image rm -f $(PROJECT_NAME):latest 2>/dev/null \
	&& echo 'Image(s) for "$(PROJECT_NAME)" removed.' \
	|| echo 'Image(s) for "$(PROJECT_NAME)" already removed.'

prune:
	# clean all that is not actively used
	docker system prune -af
