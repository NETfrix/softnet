FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# System deps + graph-tool PPA
RUN apt-get update && apt-get install -y --no-install-recommends \
        software-properties-common gpg curl ca-certificates && \
    echo "deb [ arch=amd64 ] https://downloads.skewed.de/apt noble main" \
        > /etc/apt/sources.list.d/graph-tool.list && \
    curl -fsSL https://keys.openpgp.org/vks/v1/by-fingerprint/793CEFE14DBC851A2BFB1222612DEFB798507F25 \
        | gpg --dearmor -o /etc/apt/trusted.gpg.d/graph-tool.gpg && \
    apt-get update && apt-get install -y --no-install-recommends \
        python3 python3-pip python3-venv python3-dev \
        python3-graph-tool \
        nodejs npm && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Frontend deps (cached layer)
COPY frontend/package.json frontend/package-lock.json* frontend/
RUN cd frontend && npm install

# Copy full source
COPY . .

# Build frontend
RUN cd frontend && npm run build

# Install Python package
RUN pip install --break-system-packages -e .

EXPOSE 10000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "10000"]
