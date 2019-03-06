FROM python:3.6-alpine

LABEL maintainer  = "IT'IS Foundation"
LABEL description = "Base python3 image for development"

ENV HOME /home/scu
# TODO: added workaround for pip --no-cache-dir bug
ENV MY_PIP pip3 --no-cache-dir

# Adds non-root user 'scu'
RUN adduser -D -u 8004 scu

# Intalls basic dev libraries for python
# TODO: pin versions ???
RUN apk update &&\ 
    apk add --no-cache \
        su-exec \
        postgresql-dev \
        gcc \
        libc-dev \
        libffi-dev \ 
        python3-dev

# Installs pip 
# TODO: pin versions ???
RUN $MY_PIP install --upgrade \
        pip \
        wheel \
        setuptools &&\
    $MY_PIP list &&\
    rm -rf /pipcache

