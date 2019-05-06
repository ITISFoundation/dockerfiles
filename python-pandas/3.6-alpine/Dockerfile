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

RUN pip --no-cache \
        --disable-pip-version-check install \
        --upgrade pip~=19.1.0

WORKDIR /build

COPY requirements.txt requirements.txt
RUN umask 022 && \
    pip --no-cache --disable-pip-version-check install \
        -r requirements.txt
        #pandas~=0.24.0
        
RUN apk del --no-cache \
        .build-deps