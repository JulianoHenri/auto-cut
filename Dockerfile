FROM n8nio/n8n:latest

USER root

# Pacotes do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    python3 \
    python3-pip \
    python3-venv \
    ca-certificates \
  && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# Scripts auxiliares
RUN mkdir -p /opt/clipper
COPY scripts/ /opt/clipper/
RUN chmod +x /opt/clipper/*.py

USER node