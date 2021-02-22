# based on https://github.com/xelalexv/dregsy/blob/85b34eb8a0c7ffc1b7c610bc8de1388230a12551/Dockerfile
FROM python:3.8-buster

LABEL maintainer "neagu@itis.swiss"

# Skopeo install https://github.com/containers/skopeo/blob/master/install.md
RUN echo 'deb http://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/Debian_10/ /' > /etc/apt/sources.list.d/devel:kubic:libcontainers:stable.list && \
        curl -L https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/Debian_10/Release.key | apt-key add -

RUN apt-get -y update && \
        apt-get install -y \
        skopeo

RUN pip3 install --upgrade \
        pip \
        setuptools \
        wheel

RUN mkdir -p /app

COPY . /app/reposync

WORKDIR /app/reposync

RUN pip3 install .

# remove install directory
RUN rm -rf /app

CMD ["run-reposync", "-c", "/etc/cfg.yaml"]

