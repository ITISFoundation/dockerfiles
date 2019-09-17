#!/bin/sh
set -e

echo "# Creating qx app"
qx create myapp -t desktop -I

cd myapp

echo "# Building build version"
qx compile --machine-readable --target=build

echo "# Building source version"
qx serve --machine-readable --target=source  --listen-port=8080 &
SERVER_PID=$!

echo "# Waiting for build to complete"
while ! nc -z localhost 8080; do
    sleep 1 # wait for 10 second before check again
done

wget --spider http://localhost:8080/testtapper/
kill $SERVER_PID