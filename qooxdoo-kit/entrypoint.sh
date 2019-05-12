#!/bin/sh
set -e

if [ "$1" = 'help' ]; then
    cat << 'HELLO_END'
Welcome to the OSPARC Qooxdoo Kit
---------------------------------
a qooxdoo compiler and a copy of the qooxdoo sdk.

Use the compiler in the same way as you would use it if you
had a local installation.

 docker run -it -v $(pwd):/project itisfoundation/qx-kit:latest qx create myapp -t desktop -I
 docker run --init -it -v $(pwd)/myapp:/project itisfoundation/qx-kit:latest qx compile
 docker run --init -it -v $(pwd)/myapp:/project itisfoundation/qx-kit:latest -P 8080:8080 qx serve

HELLO_END
exit 1
fi

PROJECT_DIR=/project

export PATH=/home/node/node_modules/.bin:$PATH
USERID=$(stat -c %u ${PROJECT_DIR})
USERNAME=$(getent passwd ${USERID} | cut -d: -f1)
GROUPID=$(stat -c %g ${PROJECT_DIR})
GROUPNAME=$(getent group ${GROUPID} | cut -d: -f1)

if [ "$GROUPNAME" = "" ]; then
    GROUPNAME=appgroup
    addgroup -g $GROUPID $GROUPNAME
fi

if [ "$USERNAME" = "" ]; then
    # alpine uses busybox adduser
    USERNAME=appuser
    adduser -D -S -u $USERID -G $GROUPNAME -s /bin/sh $USERNAME
else
    adduser $USERNAME $GROUPNAME
fi

cd $PROJECT_DIR

echo "[RUN]: Running command ($@) as ${USERNAME}($USERID):${GROUPNAME}($GROUPID)"
exec su-exec ${USERNAME}:${GROUPNAME} "$@"