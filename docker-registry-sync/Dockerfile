# based on https://github.com/xelalexv/dregsy/blob/0.5.1/hack/dregsy.alpine.Dockerfile
FROM xelalex/dregsy:0.5.1-alpine@sha256:1adb89b1310128367a55dbbe6b0656c36558986e893fa96e610303069d966578

LABEL maintainer "neagu@itis.swiss"

RUN apk add python3 py-pip
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

