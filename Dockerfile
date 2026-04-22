FROM n8nio/n8n:latest

USER root

# Pacotes do sistema (Alpine)
RUN apk add --no-cache \
    ffmpeg \
    python3 \
    py3-pip \
    ca-certificates

# Python deps
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# Scripts auxiliares
RUN mkdir -p /opt/clipper
COPY scripts/ /opt/clipper/
RUN chmod +x /opt/clipper/*.py

USER node