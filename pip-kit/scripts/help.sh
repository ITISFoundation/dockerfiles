#!/bin/sh

echo "User    :`id $(whoami)`"
echo "Workdir :`pwd`"
echo "Installed:"
pip list
echo "--------------------------------------"
cat /build/README.md | grep -v "<--"
