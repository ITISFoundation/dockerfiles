FROM python:3.7

# RUN apk add --update --no-cache bash ca-certificates && update-ca-certificates

ENV DEVPI_SERVER_VERSION=4.8.0 \
    DEVPI_WEB_VERSION=3.5.0 \
    DEVPI_CLIENT_VERSION=4.2.0 \
    DEVPI_CLEANER_VERSION=0.2.0 \
    DEVPI_LDAP_VERSION=1.2.2

ENV VIRTUAL_ENV /env
# create a virtual env in $VIRTUAL_ENV, ensure it respects pip version
RUN pip install virtualenv \
    && virtualenv $VIRTUAL_ENV \
    && $VIRTUAL_ENV/bin/pip install pip==$PYTHON_PIP_VERSION
ENV PATH $VIRTUAL_ENV/bin:$PATH

RUN pip install devpi-server==$DEVPI_SERVER_VERSION \
        devpi-web==$DEVPI_WEB_VERSION \
        devpi-client==$DEVPI_CLIENT_VERSION \
        devpi-cleaner==$DEVPI_CLEANER_VERSION \
        devpi-ldap==$DEVPI_LDAP_VERSION

RUN mkdir /data
ENV HOME /data

RUN chown 1001:1001 $HOME/. \
    && addgroup --system --gid 1001 devpi \
    && adduser --disabled-password --system --uid 1001 --home $HOME --shell /sbin/nologin --gid 1001 devpi

COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh
RUN chown 1001:1001 /data

USER devpi

ENV DEVPISERVER_PORT 31411
ENV DEVPISERVER_SERVERDIR "/data/server"
ENV DEVPISERVER_CLIENTDIR "/data/client"

EXPOSE ${DEVPISERVER_PORT}

WORKDIR $HOME

ENTRYPOINT ["/entrypoint.sh"]
CMD ["devpi"]
