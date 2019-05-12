FROM node:10-alpine

LABEL maintainer=oetiker

# adding these in separate layers since
RUN apk add --no-cache su-exec git python2 tini

USER node
WORKDIR /home/node

COPY --chown=node:node entrypoint.sh .

RUN echo {} > package.json ;\
    chmod 755 entrypoint.sh ;\
    npm install @qooxdoo/framework @qooxdoo/compiler

USER root
EXPOSE 8080

ENTRYPOINT [ "/sbin/tini","--","/home/node/entrypoint.sh" ]
CMD ["help"]
