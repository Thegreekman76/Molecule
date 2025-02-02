FROM python:3.11-slim

WORKDIR /app

# 1. Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    curl \
    git \
    unzip \
    build-essential \
    libssl-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 2. Instalar Node.js y Bun de forma global
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g bun@1.1.4

# 3. Configurar entorno de Reflex
ENV REFLEX_BUN_PATH=/usr/bin/bun
ENV REFLEX_SKIP_BUN_INSTALL=true

# 4. Copiar solo lo esencial
COPY frontend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY frontend/rxconfig.py .
COPY frontend/frontend/ ./frontend/

# 5. Configurar permisos
#RUN chmod -R 755 /root/.cache

EXPOSE 3000

CMD ["reflex", "run"]