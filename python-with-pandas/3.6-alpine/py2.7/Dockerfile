FROM python:3.6-alpine3.9

LABEL maintainer=pcrespov

RUN apk add  --no-cache --virtual  .BUILD-DEPS  \
        build-base \
        git \
        gcc \
        libc-dev \
        python-dev \
        musl-dev \
        libffi-dev \
        postgresql-dev 
        
RUN python2 -m ensurepip && \
        rm -r /usr/lib/python*/ensurepip

RUN pip2 --no-cache \
        --disable-pip-version-check install \
        --upgrade pip

WORKDIR /build

COPY requirements.txt requirements.txt
RUN umask 022 && \
        pip2 --no-cache --disable-pip-version-check install \
        -r requirements.txt

        
RUN apk del --no-cache \
        .build-deps \
        .build-deps-py2 