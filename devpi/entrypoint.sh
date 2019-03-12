#!/bin/bash
set -e
function initialise_devpi {
    echo "[RUN]: Initialise devpi-server"
    devpi-server --restrict-modify root --start --host 127.0.0.1 --init
    devpi-server --status
    devpi use http://localhost:${DEVPISERVER_PORT}
    devpi login root --password=''
    devpi user -m root password="${DEVPI_PASSWORD}"
    devpi index -y -c public pypi_whitelist='*'
    devpi-server --stop
    devpi-server --status
}

echo "DEVPISERVER_SERVERDIR is ${DEVPISERVER_SERVERDIR}"
echo "DEVPISERVER_CLIENTDIR is ${DEVPISERVER_CLIENTDIR}"
echo "DEVPISERVER_PORT is ${DEVPISERVER_PORT}"

if [ "$1" = 'devpi' ]; then
    if [ ! -f  $DEVPISERVER_SERVERDIR/.serverversion ]; then
        initialise_devpi
    fi

    echo "[RUN]: Launching devpi-server"
    exec devpi-server --restrict-modify root --host 0.0.0.0 --ldap-config=/data/server/ldapcfg.yaml
fi

echo "[RUN]: Builtin command not provided [devpi]"
echo "[RUN]: $@"

exec "$@"
