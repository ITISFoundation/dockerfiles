FROM python:3.6-alpine

LABEL maintainer=pcrespov

RUN apk add --virtual .build-deps \
        git \
        gcc \
        libc-dev \
        python-dev \
        musl-dev \
        libffi-dev \
        postgresql-dev 

RUN apk add --virtual .build-deps-py2 \ 
        python2 \
        python2-dev
        
RUN python2 -m ensurepip && \
        rm -r /usr/lib/python*/ensurepip

RUN pip2 --no-cache \
        --disable-pip-version-check install \
        --upgrade pip

WORKDIR /build

RUN umask 022 && \
    pip2 --no-cache --disable-pip-version-check install \
        pandas~=0.24.0
        
RUN apk del --no-cache \
        .build-deps \
        .build-deps-py2 