FROM python:3.11-alpine

LABEL maintainer "neagu@itis.swiss"

ENV VERSION=v0.20.3
ENV OS=Linux
ENV ARCH=x86_64
RUN apk add curl tar &&\
        curl -sL "https://github.com/google/go-containerregistry/releases/download/${VERSION}/go-containerregistry_${OS}_${ARCH}.tar.gz" > go-containerregistry.tar.gz &&\
        tar -zxvf go-containerregistry.tar.gz -C /usr/local/bin/ crane &&\
        crane --help &&\
        apk del curl tar &&\
        apk cache clean

RUN mkdir -p /app

COPY . /app/reposync

WORKDIR /app/reposync

RUN pip3 install .

# remove install directory
RUN rm -rf /app

CMD ["run-reposync", "/etc/cfg.yaml"]

