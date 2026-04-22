FROM node:18-bookworm-slim

ENV NODE_ENV=production
WORKDIR /data

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    python3 \
    python3-pip \
    ca-certificates \
    build-essential \
  && rm -rf /var/lib/apt/lists/*

# Fixar n8n para evitar incompatibilidade com isolated-vm
RUN npm install -g n8n@1.99.0

COPY requirements.txt /tmp/requirements.txt
RUN python3 -m pip install --upgrade pip setuptools wheel \
 && pip3 install --no-cache-dir -r /tmp/requirements.txt

RUN mkdir -p /opt/clipper
COPY scripts/ /opt/clipper/
RUN chmod +x /opt/clipper/*.py

EXPOSE 5678
CMD ["n8n"]