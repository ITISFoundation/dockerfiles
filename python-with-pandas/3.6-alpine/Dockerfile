
ARG PYTHON_VERSION=3.6-alpine3.9
FROM python:${PYTHON_VERSION} as builder

LABEL maintainer=pcrespov

ENV PYTHONUNBUFFERED 1

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

WORKDIR /wheels
COPY requirements.txt /wheels/requirements.txt
RUN pip install -U pip \
   && pip wheel -r ./requirements.txt

FROM python:${PYTHON_VERSION} as runtime-image

COPY --from=builder /wheels /wheels
RUN pip install -U pip \
       && umask 022 \
       && pip install -r /wheels/requirements.txt \
                      -f /wheels \
       && rm -rf /wheels \
       && rm -rf /root/.cache/pip/* 