FROM python:3.6-alpine3.9

LABEL maintainer=pcrespov

WORKDIR /build
COPY requirements.txt requirements.txt

RUN apk add --no-cache --virtual .BUILD-DEPS \
        build-base \
        git \
        gcc \
        wget \
        libc-dev \
        python-dev \
        musl-dev \
        libffi-dev \
        postgresql-dev && \
    pip --no-cache \
        --disable-pip-version-check install \
        --upgrade pip~=19.1.0 &&\
    umask 022 && \
    pip --no-cache --disable-pip-version-check install \
        -r requirements.txt && \
    rm -rf /var/cache/apk/* && \
        apk del --no-cache .BUILD-DEPS