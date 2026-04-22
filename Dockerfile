FROM node:20.19.1-bookworm-slim

ENV NODE_ENV=production
WORKDIR /data

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    python3 \
    python3-venv \
    python3-pip \
    ca-certificates \
    build-essential \
  && rm -rf /var/lib/apt/lists/*

# n8n (pode manter fixo; se quiser, dá para testar uma versão mais nova depois)
RUN npm install -g n8n@1.99.0

# Python venv (PEP 668)
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip setuptools wheel \
 && pip install --no-cache-dir -r /tmp/requirements.txt

RUN mkdir -p /opt/clipper
COPY scripts/ /opt/clipper/
RUN chmod +x /opt/clipper/*.py

EXPOSE 5678
CMD ["n8n"]