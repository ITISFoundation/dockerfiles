FROM node:10.16.3-alpine

LABEL maintainer="oetiker,pcrespov"

# adding these in separate layers since
RUN apk add --no-cache \
    su-exec \
    git \
    tini \
    jq

ENV PATH=/home/node/node_modules/.bin:${PATH}
ENV NODE_PATH=/home/node/node_modules

WORKDIR /home/node

COPY --chown=node:node package*.json ./

# TODO: latest or fix?? or a variable?
RUN su - node -c "npm install npm@latest" && \
    su - node -c "npm install"

# RUN su - node -c "echo {} > package.json" ;\
#     apk add --no-cache --virtual .build-deps python2;\
#     su - node -c "npm install @qooxdoo/framework" ;\
#     su - node -c "npm install @qooxdoo/compiler" ;\
#     apk del .build-deps;

COPY --chown=node:node entrypoint.sh .
RUN chmod 755 entrypoint.sh

EXPOSE 8080

ENTRYPOINT [ "/sbin/tini","--","/home/node/entrypoint.sh" ]
CMD ["help"]
