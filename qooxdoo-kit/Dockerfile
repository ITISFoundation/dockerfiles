FROM node:10.16.3-alpine

LABEL maintainer="oetiker,pcrespov"

ENV DEP_PACKAGES="su-exec git tini jq patch"
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

# Apply local patches to the third-party packages installed above.
# Each *.patch is applied (with -p1) from the root of the package it targets.
# --forward keeps the build idempotent; a patch that no longer applies fails the
# build so the carried fix gets re-verified against the upgraded dependency.
COPY --chown=node:node patches/ /home/node/patches/
RUN cd /home/node/node_modules/@qooxdoo/compiler && \
    for patchfile in /home/node/patches/*.patch; do \
      echo "Applying ${patchfile}" && \
      patch -p1 --forward < "${patchfile}"; \
    done

COPY --chown=node:node entrypoint.sh .
RUN chmod 755 entrypoint.sh

EXPOSE 8080

ENTRYPOINT [ "/sbin/tini","--","/home/node/entrypoint.sh" ]
CMD ["help"]
