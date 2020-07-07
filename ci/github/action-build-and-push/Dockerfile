FROM jpetazzo/dind

RUN apt-get update && apt-get install -y \
        make \
        curl \
        git \
        jq \
        python3 \
        python3-pip

RUN pip install --upgrade pip setuptools

RUN curl -L "https://github.com/docker/compose/releases/download/1.26.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose && \
    chmod +x /usr/local/bin/docker-compose

ADD print_as_header.py /code/print_as_header.py

ADD entrypoint.bash /entrypoint.bash
RUN chmod +x /entrypoint.bash

ENTRYPOINT ["/entrypoint.bash"]