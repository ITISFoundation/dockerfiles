#!/bin/sh
set -e

function initialise_devpi {
    echo "[RUN]: Initialising devpi-server"
    devpi-server --restrict-modify root \
        --start \
        --host 127.0.0.1 --port ${DEVPISERVER_PORT} \
        --serverdir ${DEVPISERVER_SERVERDIR} \
        --init
    devpi-server --status
    devpi use http://localhost:${DEVPISERVER_PORT}
    devpi login root --password=''
    devpi user -m root password="${DEVPISERVER_PASSWORD}"
    devpi index -y -c public pypi_whitelist='*'
    devpi-server --stop
    devpi-server --status
    chown -R ${USERID}:${GROUPID} ${DEVPISERVER_SERVERDIR}
}

export DEVPISERVER_DIR=/data
export DEVPISERVER_PORT=31411

export DEVPISERVER_SERVERDIR=${DEVPISERVER_DIR}
export DEVPISERVER_CLIENTDIR=/client
mkdir /client

USERID=$(stat -c %u ${DEVPISERVER_DIR})
USERNAME=$(getent passwd ${USERID} | cut -d: -f1)
GROUPID=$(stat -c %g ${DEVPISERVER_DIR})
GROUPNAME=$(getent group ${GROUPID} | cut -d: -f1)

if [ "$GROUPNAME" = "" ]; then
    GROUPNAME=appgroup
    addgroup -g $GROUPID $GROUPNAME
fi

if [ "$USERNAME" = "" ]; then
    # alpine uses busybox adduser
    USERNAME=appuser
    adduser -h /client -D -S -u $USERID -G $GROUPNAME -s /bin/sh $USERNAME
else
    adduser $USERNAME $GROUPNAME
fi

echo "[RUN]: running as $USERNAME($USERID):$GROUPNAME($GROUPID)"

# configure ldap
cat <<LDAPCFG_END > /ldapcfg.yaml
devpi-ldap:
  url: ${DEVPISERVER_DEVPI_LDAP_URL}
  user_template: ${DEVPISERVER_DEVPI_USER_TEMPLATE}
  group_search:
    base: ${DEVPISERVER_DEVPI_GROUP_SEARCH_BASE}
    filter: ${DEVPISERVER_DEVPI_GROUP_FILTER}
    attribute_name: ${DEVPISERVER_DEVPI_GROUP_ATTRIBUTE_NAME}
LDAPCFG_END

if [ "$1" = 'devpi' ]; then
    if [ ! -f  $DEVPISERVER_DIR/.serverversion ]; then
        initialise_devpi
    fi

    echo "[RUN]: Launching devpi-server as ${USERNAME}:${GROUPNAME}"
    exec su-exec ${USERNAME}:${GROUPNAME} devpi-server \
        --restrict-modify root \
        --host 0.0.0.0 --port ${DEVPISERVER_PORT} \
        --ldap-config=/ldapcfg.yaml
fi

echo "[RUN]: Builtin command not provided [devpi]"
echo "[RUN]: $@ as ${USERNAME}:${GROUPNAME}"

exec su-exec ${USERNAME}:${GROUPNAME} "$@"
