# ============================================================
# Minimal & secure Docker environment for crypto ML pipeline
# Fixes CA / SSL issues for CCXT on python:slim
# ============================================================
FROM python:3.11-slim

# ----------------------------
# System dependencies + CA
# ----------------------------
RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    build-essential \
 && update-ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# ----------------------------
# Environment variables
# ----------------------------
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt \
    REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

# ----------------------------
# Working directory
# ----------------------------
WORKDIR /app

# ----------------------------
# Python dependencies
# ----------------------------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ----------------------------
# Sanity check (non-fatal)
# ----------------------------
RUN python - <<'PY'
import ssl
print("✅ OpenSSL:", ssl.OPENSSL_VERSION)
PY

# ----------------------------
# Default command
# ----------------------------
CMD ["python", "-c", "print('🐳 Crypto ML Pipeline Docker Environment Ready')"]
