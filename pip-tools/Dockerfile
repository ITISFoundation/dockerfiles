FROM python:3.6-alpine

LABEL maintainer = "IT'IS Foundation - pcrespov"
LABEL description = "Tools to manage, compile and sync pip requirements"

RUN apk update && apk add \
    git \
    docker \
    bash \
    openssh \
    openssl

COPY requirements.txt /requirements.txt
RUN pip3 install -u -r /requirements.txt

WORKDIR /home/scu
VOLUME /home/scu
