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

# Set timezone
ENV TZ=UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Create workspace directory
WORKDIR /workspace

# Copy requirements if they exist
COPY requirements.txt* ./
RUN if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

# Install Home Assistant and development dependencies
RUN pip install \
    homeassistant \
    pytest \
    pytest-homeassistant-custom-component \
    black \
    flake8 \
    pylint \
    isort \
    pre-commit