FROM python:3.6-alpine3.9

LABEL maintainer=pcrespov

RUN apk add --no-cache --virtual .BUILD-DEPS \
        build-base \
        git \
        gcc \
        wget \
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

RUN rm -rf /var/cache/apk/* &&\
        apk del --no-cache .BUILD-DEPS