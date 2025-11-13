FROM python:3.9-slim

RUN apt-get update && \
    apt-get install -y \
    iproute2 \
    iputils-ping \
    net-tools \
    tcpdump \
    procps \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY src/*.py /app/

COPY cfg /app/cfg

COPY docker/entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

RUN mkdir -p /app/logs

ENV ID=1
ENV INF=16

ENTRYPOINT ["/app/entrypoint.sh"]
