FROM node:10-alpine

LABEL maintainer=oetiker

# adding these in separate layers since
RUN apk add --no-cache su-exec git tini

WORKDIR /home/node

COPY --chown=node:node entrypoint.sh .

RUN echo {} > package.json ;\
    chmod 755 entrypoint.sh ;\
    apk add --no-cache --virtual .build-deps python2;\
    su - node -c "npm install @qooxdoo/framework @qooxdoo/compiler" ;\
    apk del .build-deps;

EXPOSE 8080

ENTRYPOINT [ "/sbin/tini","--","/home/node/entrypoint.sh" ]
CMD ["help"]
