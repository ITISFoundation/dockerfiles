FROM python:3.6-alpine

LABEL maintainer = "IT'IS Foundation"
LABEL description = "Light Python base image for tooling and development"

ENV HOME /home/scu

# non-root user 'scu'
RUN adduser -D -u 8004 scu

RUN apk update &&\ 
    apk add --no-cache \
        su-exec \
        postgresql-dev \
        gcc \
        libc-dev \
        libffi-dev \ 
        python3-dev

RUN python3 -m ensurepip &&\ 
    pip3 install --no-cache --upgrade \
        pip \
        wheel \
        setuptools

