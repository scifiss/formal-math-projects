FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PATH="/root/.elan/bin:${PATH}"

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    ca-certificates \
    python3 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy only the agent-visible environment.
COPY environment/ /app/

RUN curl https://elan.lean-lang.org/elan-init.sh -sSf | sh -s -- -y

RUN elan toolchain install "$(cat lean-toolchain)" && \
    elan default "$(cat lean-toolchain)"

RUN lake exe cache get
RUN lake build