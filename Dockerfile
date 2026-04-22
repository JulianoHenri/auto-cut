FROM n8nio/n8n:stable-debian

USER root

# Debian buster (EOL): usar archive.debian.org
RUN sed -i 's|http://deb.debian.org/debian|http://archive.debian.org/debian|g' /etc/apt/sources.list \
 && sed -i 's|http://deb.debian.org/debian-security|http://archive.debian.org/debian-security|g' /etc/apt/sources.list \
 && echo 'Acquire::Check-Valid-Until "false";' > /etc/apt/apt.conf.d/99no-check-valid-until

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    python3 \
    python3-pip \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN python3 -m pip install --upgrade pip setuptools wheel
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

RUN mkdir -p /opt/clipper
COPY scripts/ /opt/clipper/
RUN chmod +x /opt/clipper/*.py

USER node