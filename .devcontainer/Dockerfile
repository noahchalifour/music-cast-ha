# Use the official Python devcontainer as base
FROM mcr.microsoft.com/devcontainers/python:3.11

# Install Cargo (Rust package manager)
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Set timezone
ENV TZ=UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone