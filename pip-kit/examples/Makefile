.PHONY: all check clean

SHELL = /bin/sh
DOCKER_PIP_TOOLS_IMAGE = itisfoundation/pip-tools:latest
 
objects = $(wildcard *.in)
outputs := $(objects:.in=.txt)

# target: all – pip-compiles all requirements/*.in -> requirements/*.txt
all: $(outputs)


# TODO: all outputs are owned by
%.txt: %.in
	@docker run -it --rm \
		-v "$(CURDIR):/home/scu" \
	"$(DOCKER_PIP_TOOLS_IMAGE)" "$(SHELL)" -c \
		'CUSTOM_COMPILE_COMMAND="make $@" \
		pip-compile -v -o /tmp/requirements.tmp $< && \
		cat /tmp/requirements.tmp > $@'

ci.txt: base.txt

# target: check – Checks whether pip-compile is installed
check:
	@docker run -it --rm "$(DOCKER_PIP_TOOLS_IMAGE)" "$(SHELL)" -c \
	'pip-compile --version'

# target: clean – Cleans all requirements/*.txt
clean: check
	- rm *.txt


