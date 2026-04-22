FROM node:18-bookworm-slim

ENV NODE_ENV=production
WORKDIR /data

# Dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    python3 \
    python3-venv \
    python3-pip \
    ca-certificates \
    build-essential \
  && rm -rf /var/lib/apt/lists/*

# Instala n8n (fixo para evitar problemas com isolated-vm)
RUN npm install -g n8n@1.99.0

# Python: cria venv para evitar erro "externally-managed-environment" (PEP 668)
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Python deps
COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip setuptools wheel \
 && pip install --no-cache-dir -r /tmp/requirements.txt

# Scripts auxiliares
RUN mkdir -p /opt/clipper
COPY scripts/ /opt/clipper/
RUN chmod +x /opt/clipper/*.py

# n8n
EXPOSE 5678
CMD ["n8n"]