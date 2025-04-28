FROM python:3.7.12-alpine

LABEL maintainer=pcrespov

# itis-user uid=8004(scu) gid=8004(scu) groups=8004(scu)
RUN adduser -D -u 8004 -s /bin/sh -h /home/itis itis

# adds pip installations
ENV PATH "/home/itis/.local/bin:$PATH"

RUN apk add --no-cache \
    su-exec

RUN pip --no-cache install --upgrade pip==19.0.3

WORKDIR /build

USER itis

COPY requirements.txt requirements.txt
RUN pip --no-cache --disable-pip-version-check \
        install --user -r requirements.txt

COPY scripts scripts
COPY README.md README.md

WORKDIR /home/itis/work
VOLUME /home/itis/work

USER root
ENTRYPOINT [ "/bin/sh", "/build/scripts/entrypoint.sh" ]
CMD ["/bin/sh", "/build/scripts/help.sh"]
