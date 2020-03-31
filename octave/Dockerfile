FROM ubuntu:18.04

ENV DEBIAN_FRONTEND noninteractive

LABEL maintainer=pcrespov

# simcore-user uid=8004(${SC_USER_NAME}) gid=8004(${SC_USER_NAME}) groups=8004(${SC_USER_NAME})
ENV SC_USER_ID 8004
ENV SC_USER_NAME scu

RUN adduser --uid ${SC_USER_ID} \
    --disabled-password --gecos "" \
    --shell /bin/bash \
    --home /home/${SC_USER_NAME} \
    ${SC_USER_NAME}

RUN apt-get update && \
    apt-get install -y \
        software-properties-common \
        octave && apt-get remove -y software-properties-common && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean

WORKDIR /home/${SC_USER_NAME}

ENTRYPOINT ["octave"]
