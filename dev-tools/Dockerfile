FROM python:3.6-itis

LABEL maintainer = "IT'IS Foundation"
LABEL description = "dev-tools: pip compiler, template renderers, versioning, ..."

RUN apk update && apk add \
    git \
    docker \
    bash \
    openssh \
    openssl

COPY requirements.txt /requirements.txt
RUN pip3 install -r /requirements.txt

WORKDIR /home/scu
VOLUME /home/scu
