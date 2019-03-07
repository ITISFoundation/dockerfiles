.PHONY: all check clean

SHELL = /bin/sh
PIPKIT = itisfoundation/pip-kit:latest
 
objects = $(wildcard *.in)
outputs := $(objects:.in=.txt)

# target: all – pip-compiles all requirements/*.in -> requirements/*.txt
all: $(outputs)


# TODO: all outputs are owned by
%.txt: %.in
	@docker run -it --rm \
		-v "$(CURDIR):/home/scu" \
	"$(PIPKIT)" "$(SHELL)" -c \
		'CUSTOM_COMPILE_COMMAND="make $@" \
		pip-compile -v -o /tmp/requirements.tmp $< && \
		cat /tmp/requirements.tmp > $@'

ci.txt: base.txt

# target: check – Checks whether pip-compile is installed
check:
	@docker run -it --rm "$(PIPKIT)" "$(SHELL)" -c \
	'pip-compile --version'

# target: clean – Cleans all requirements/*.txt
clean: check
	- rm *.txt


