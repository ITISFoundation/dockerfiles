# based on https://github.com/xelalexv/dregsy/blob/85b34eb8a0c7ffc1b7c610bc8de1388230a12551/Dockerfile
FROM xelalex/dregsy@sha256:9b0fe252cb8bf88f67871efd6559ef89b76013c46dfbc49b961d396a4b8d1887

LABEL maintainer "neagu@itis.swiss"

RUN apk add python3
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

