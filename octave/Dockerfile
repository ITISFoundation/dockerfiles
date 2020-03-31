FROM ubuntu:18.04

ENV DEBIAN_FRONTEND noninteractive

LABEL maintainer=pcrespov

ENV ITIS_USER_ID 8004
ENV ITIS_USER_NAME itis

RUN adduser --uid ${ITIS_USER_ID} \
    --disabled-password --gecos "" \
    --shell /bin/bash \
    --home /home/${ITIS_USER_NAME} \
    ${ITIS_USER_NAME}

RUN apt-get update \
    && apt-get install -y \
        software-properties-common \
        octave \
    && apt-get remove -y software-properties-common \
    && rm -rf /var/lib/apt/lists/*  \
    && apt-get clean

WORKDIR /home/${ITIS_USER_NAME}

ENTRYPOINT ["octave"]
