#!/bin/sh

echo "  User    :`id $(whoami)`"
echo "  Workdir :`pwd`"

# container's ----
USERNAME=itis
MOUNT_VOLUME=/home/itis/work


stat $MOUNT_VOLUME &> /dev/null || \
    (echo "ERROR: You must mount '$MOUNT_VOLUME' to deduce user and group ids" && exit 1) # FIXME: exit does not stop script

USERID=$(stat -c %u $MOUNT_VOLUME)
GROUPID=$(stat -c %g $MOUNT_VOLUME)
GROUPNAME=$(getent group ${GROUPID} | cut -d: -f1)

if [[ $USERID -eq 0 ]]
then
    addgroup $USERNAME root
else
    # take host's credentials in container's $USERNAME
    if [[ -z "$GROUPNAME" ]]
    then
        GROUPNAME=$USERNAME
        addgroup -g $GROUPID $GROUPNAME
    else
        addgroup $USERNAME $GROUPNAME
    fi
    
    deluser $USERNAME &> /dev/null
    adduser -u $USERID -G $GROUPNAME -D -s /bin/sh $USERNAME
fi

echo "Starting boot ..."
# TODO: su-exec $USERNAME "python -m $@"
su-exec $USERNAME "$@"