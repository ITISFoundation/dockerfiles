ARG VERSION
FROM rabbitmq:${VERSION} as build
RUN apt update && \
    apt install -y \
    wget \
    unzip
RUN mkdir -p /home/build && \
    cd /home/build && \ 
    wget https://github.com/gmr/pgsql-listen-exchange/releases/download/0.3.0-v3.5.x/pgsql-listen-exchange-0.3.0-v3.5.x.zip && \
    unzip pgsql-listen-exchange-0.3.0-v3.5.x.zip


FROM rabbitmq:${VERSION} as prod
COPY --from=build /home/build/*.ez /plugins/
# enable plugins
RUN rabbitmq-plugins enable \
    --offline rabbitmq_management \
    rabbitmq_management_agent \
    rabbitmq_web_dispatch \
    rabbitmq_prometheus \
    pgsql_listen_exchange
