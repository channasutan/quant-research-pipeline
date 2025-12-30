#!/bin/bash
# Docker setup script for crypto ML pipeline environment fix

echo "🐳 DOCKER ENVIRONMENT SETUP"
echo "================================"

echo "1. Build Docker image:"
echo "   docker build -t crypto-pipeline ."
echo ""

echo "2. Test SSL environment:"
echo "   docker run --rm crypto-pipeline python -c \"import ssl; print('OpenSSL:', ssl.OPENSSL_VERSION)\""
echo ""

echo "3. Test CCXT functionality:"
echo "   docker run --rm -v \$(pwd):/app crypto-pipeline python test_docker_ccxt.py"
echo ""

echo "4. Test our pipeline module:"
echo "   docker run --rm -v \$(pwd):/app crypto-pipeline python -c \"import sys; sys.path.insert(0,'/app/research'); from fetch_raw import fetch_symbol_data; data=fetch_symbol_data('BTC/USDT','4h','toobit',limit=5); print('✅ Pipeline:', len(data), 'rows')\""
echo ""

echo "5. Run full pipeline:"
echo "   docker run --rm -v \$(pwd):/app crypto-pipeline python -c \"import sys; sys.path.insert(0,'/app/research'); exec(open('/app/test_pipeline.py').read())\""
echo ""

echo "📋 EXPECTED RESULTS:"
echo "   - OpenSSL 3.x (not LibreSSL 2.8.3)"
echo "   - CCXT exchanges work without SSL errors"
echo "   - fetch_symbol_data returns real market data"
echo "   - Pipeline code remains unchanged"

# Make executable
chmod +x docker_setup.sh