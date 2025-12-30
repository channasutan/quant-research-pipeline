#!/usr/bin/env python3
"""
Verification script for Docker-based SSL fix
"""

import subprocess
import sys
import os

def check_docker_available():
    """Check if Docker is installed and running"""
    try:
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ Docker available: {result.stdout.strip()}")
            return True
        else:
            print("❌ Docker command failed")
            return False
    except FileNotFoundError:
        print("❌ Docker not installed")
        return False
    except subprocess.TimeoutExpired:
        print("❌ Docker command timed out")
        return False

def verify_dockerfile():
    """Verify Dockerfile exists and is correct"""
    if not os.path.exists('Dockerfile'):
        print("❌ Dockerfile not found")
        return False
    
    with open('Dockerfile', 'r') as f:
        content = f.read()
    
    required_elements = [
        'python:3.11-slim',
        'requirements.txt',
        'ssl.OPENSSL_VERSION'
    ]
    
    for element in required_elements:
        if element not in content:
            print(f"❌ Dockerfile missing: {element}")
            return False
    
    print("✅ Dockerfile structure correct")
    return True

def show_solution_summary():
    """Show the complete solution"""
    print("\n🐳 DOCKER SOLUTION SUMMARY")
    print("=" * 40)
    
    print("\n📋 Problem:")
    print("   - macOS Python uses LibreSSL 2.8.3")
    print("   - CCXT requires OpenSSL 1.1.1+")
    print("   - All exchanges fail with SSL errors")
    
    print("\n🛠️ Solution:")
    print("   - Docker with python:3.11-slim (OpenSSL 3.x)")
    print("   - Mount project directory")
    print("   - Run pipeline unchanged")
    
    print("\n📁 Files Created:")
    files = ['Dockerfile', 'test_docker_ccxt.py', 'docker_setup.sh']
    for file in files:
        exists = "✅" if os.path.exists(file) else "❌"
        print(f"   {exists} {file}")
    
    print("\n🚀 Usage Commands:")
    print("   1. docker build -t crypto-pipeline .")
    print("   2. docker run --rm -v $(pwd):/app crypto-pipeline python test_docker_ccxt.py")
    print("   3. docker run --rm -v $(pwd):/app crypto-pipeline python -c \"import sys; sys.path.insert(0,'/app/research'); from fetch_raw import fetch_symbol_data; print('Test:', len(fetch_symbol_data('BTC/USDT','4h','toobit',5)))\"")

def main():
    """Main verification"""
    print("🔍 DOCKER SOLUTION VERIFICATION")
    print("=" * 50)
    
    # Check Docker availability
    docker_ok = check_docker_available()
    
    # Check Dockerfile
    dockerfile_ok = verify_dockerfile()
    
    # Show solution
    show_solution_summary()
    
    print(f"\n🎯 STATUS:")
    if docker_ok and dockerfile_ok:
        print("✅ Ready to test Docker solution")
        print("   Run: ./docker_setup.sh")
    elif dockerfile_ok:
        print("⚠️  Docker solution ready, but Docker not installed")
        print("   Install Docker Desktop, then run: ./docker_setup.sh")
    else:
        print("❌ Setup incomplete")

if __name__ == "__main__":
    main()