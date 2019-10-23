ARG VERSION
FROM rabbitmq:${VERSION}
RUN rabbitmq-plugins enable --offline rabbitmq_management rabbitmq_management_agent rabbitmq_web_dispatch rabbitmq_prometheus
