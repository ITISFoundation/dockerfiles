FROM docker:dind

RUN apk update && apk add \
        make \
        curl \
        git \
        jq \
        bash \
        python3 \
        docker-compose

ADD print_as_header.py /code/print_as_header.py

ADD entrypoint.bash /entrypoint.bash
RUN chmod +x /entrypoint.bash

ENTRYPOINT ["/entrypoint.bash"]