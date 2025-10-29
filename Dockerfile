FROM ghcr.io/input-output-hk/cardano-node:latest

# Install Python and build tooling
RUN apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    ca-certificates \
    curl \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy project files
COPY pyproject.toml README.md /app/
COPY src /app/src
COPY main.py /app/
COPY docker/entrypoint.sh /app/entrypoint.sh

# Install the package
RUN pip3 install --no-cache-dir .

# Ensure entrypoint is executable
RUN chmod +x /app/entrypoint.sh

# Default environment
ENV PYTHONUNBUFFERED=1 \
    PATH="/root/.local/bin:${PATH}"

ENTRYPOINT ["/app/entrypoint.sh"]


