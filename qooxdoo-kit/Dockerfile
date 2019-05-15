FROM node:10-alpine

LABEL maintainer=oetiker

# adding these in separate layers since
RUN apk add --no-cache su-exec git tini

WORKDIR /home/node

RUN su - node -c "echo {} > package.json" ;\
    apk add --no-cache --virtual .build-deps python2;\
    su - node -c "npm install @qooxdoo/framework" ;\
    su - node -c "npm install @qooxdoo/compiler" ;\
    apk del .build-deps;

COPY --chown=node:node entrypoint.sh .
RUN chmod 755 entrypoint.sh

EXPOSE 8080

ENTRYPOINT [ "/sbin/tini","--","/home/node/entrypoint.sh" ]
CMD ["help"]
