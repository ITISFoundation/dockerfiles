FROM node:10.16.3-alpine

LABEL maintainer="oetiker,pcrespov"

ENV DEP_PACKAGES="su-exec git tini jq"
ENV ARM_DEP_PACKAGES="make g++ python2 python make g++"

RUN apk add --no-cache ${DEP_PACKAGES}
RUN if [ "$(uname -m)" = "aarch64" ] || [ "$(uname -m)" = "arm64" ]; then apk add --no-cache ${ARM_DEP_PACKAGES}; fi

# TODO: PATH=/foo:${PATH} invalidates path and append everytime a new /foo!!!
ENV PATH=/home/node/node_modules/.bin:${PATH}
ENV NODE_PATH=/home/node/node_modules

WORKDIR /home/node

COPY --chown=node:node package*.json ./

RUN su - node -c "npm install npm@latest"

RUN if [ "$(uname -m)" = "aarch64" ] || [ "$(uname -m)" = "arm64" ]; then export NPM_OPTIONS="--build-from-source"; else export NPM_OPTIONS=""; fi

RUN su - node -c "npm install ${NPM_OPTIONS}"

COPY --chown=node:node entrypoint.sh .
RUN chmod 755 entrypoint.sh

EXPOSE 8080

ENTRYPOINT [ "/sbin/tini","--","/home/node/entrypoint.sh" ]
CMD ["help"]
