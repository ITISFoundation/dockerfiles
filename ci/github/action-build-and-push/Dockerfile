FROM jpetazzo/dind

RUN apt-get update && apt-get install -y \
        make \
        curl \
        git \
        jq

RUN curl -L "https://github.com/docker/compose/releases/download/1.26.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose && \
    chmod +x /usr/local/bin/docker-compose

ADD entrypoint.bash /entrypoint.bash
ADD print_as_header.py /code/print_as_header.py
RUN chmod +x /entrypoint.bash
ENTRYPOINT ["/entrypoint.bash"]