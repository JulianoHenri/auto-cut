FROM node:20-bookworm-slim

ENV NODE_ENV=production
WORKDIR /data

# Dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    python3 \
    python3-pip \
    ca-certificates \
  && rm -rf /var/lib/apt/lists/*

# n8n
RUN npm install -g n8n@latest

# Python deps
COPY requirements.txt /tmp/requirements.txt
RUN python3 -m pip install --upgrade pip setuptools wheel \
 && pip3 install --no-cache-dir -r /tmp/requirements.txt

# Scripts
RUN mkdir -p /opt/clipper
COPY scripts/ /opt/clipper/
RUN chmod +x /opt/clipper/*.py

# n8n usa /data para config; EasyPanel deve montar volume aqui
EXPOSE 5678
CMD ["n8n"]