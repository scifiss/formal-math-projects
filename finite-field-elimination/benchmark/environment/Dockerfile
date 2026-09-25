FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      ca-certificates \
      python3 \
      singular && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Build context is the project root (one level above benchmark/).
COPY data/ /app/data/
