FROM python:3.7-alpine

LABEL maintainer=oetiker

RUN apk add --no-cache \
    su-exec build-base openssl libffi openssl-dev libffi-dev && \
    pip --no-cache install --upgrade pip==19.0.3 && \
    pip --no-cache install devpi-server==4.8.0 \
        devpi-web==3.5.0 \
        devpi-client==4.2.0 \
        devpi-cleaner==0.2.0 \
        devpi-ldap==1.2.2 && \
    apk del build-base openssl-dev libffi-dev

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

WORKDIR /data
VOLUME /data

EXPOSE 31411

ENTRYPOINT ["/entrypoint.sh"]
CMD ["devpi"]
