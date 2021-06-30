# reference for building https://github.com/Pennsieve/agent
ARG PYTHON_VERSION="3.8.10"
ARG PENNSIEVE_VERSION="0.3.5"
FROM python:${PYTHON_VERSION}-slim-buster as base

LABEL maintainer=sanderegg

# Sets utf-8 encoding for Python et al
ENV LANG=C.UTF-8

FROM base as build

RUN apt-get update \
    && export DEBIAN_FRONTEND=noninteractive \
    && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    pkgconf \
    libssl-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN curl https://sh.rustup.rs -sSf | bash -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

RUN git clone https://github.com/Pennsieve/agent.git /build/agent

WORKDIR /build/agent

RUN git checkout ${PENNSIEVE_VERSION}

RUN cargo build --release

FROM base AS production
COPY --from=build /build/agent/target/release/pennsieve .
ENTRYPOINT [ "./pennsieve" ]
CMD ["--help"]