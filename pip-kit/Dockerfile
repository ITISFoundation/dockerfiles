FROM python:3.6-alpine

# TODO create user

LABEL maintainer  = "IT'IS Foundation - pcrespov"
# LABEL description = 


COPY requirements.txt /requirements.txt
RUN pip3 install --user -r /requirements.txt

WORKDIR /work
VOLUME /work
