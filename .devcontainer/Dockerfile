# Use the official Python devcontainer as base
FROM mcr.microsoft.com/devcontainers/python:3.11

# Install additional system dependencies for Home Assistant development
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libssl-dev \
    libjpeg-dev \
    zlib1g-dev \
    autoconf \
    build-essential \
    libopenjp2-7 \
    libtiff5 \
    libturbojpeg0 \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# Install Cargo (Rust package manager)
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y

# Set timezone
ENV TZ=UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone