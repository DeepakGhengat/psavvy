#!/usr/bin/env bash
# PSAVVY AI - Additional Installation Script for AI Features
# Run this after the main install.sh

echo "========================================"
echo "  PSAVVY AI - Installing AI Dependencies"
echo "========================================"

# Install Python AI dependencies
echo "[*] Installing Python AI packages..."
pip3 install --break-system-packages anthropic openai requests pyyaml

# Verify installations
echo ""
echo "[*] Verifying AI package installations..."

python3 -c "import anthropic; print('[+] anthropic installed')" 2>/dev/null || echo "[-] anthropic not installed"
python3 -c "import openai; print('[+] openai installed')" 2>/dev/null || echo "[-] openai not installed"
python3 -c "import requests; print('[+] requests installed')" 2>/dev/null || echo "[-] requests not installed"
python3 -c "import yaml; print('[+] pyyaml installed')" 2>/dev/null || echo "[-] pyyaml not installed"

echo ""
echo "========================================"
echo "  AI Dependencies Installation Complete"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Copy config.yaml.example to config.yaml"
echo "2. Add your API keys:"
echo "   - ANTHROPIC_API_KEY (Claude)"
echo "   - PERPLEXITY_API_KEY"
echo "   - OPENAI_API_KEY (ChatGPT)"
echo ""
echo "Usage examples:"
echo "  # Full scan with AI analysis"
echo "  python3 psavvy_ai.py -d target.com --ai-analyze"
echo ""
echo "  # Generate AI report"
echo "  python3 psavvy_ai.py -d target.com --ai-report"
echo ""
echo "  # AI payload generation"
echo "  python3 psavvy_ai.py --ai-payloads xss"
echo ""
echo "  # Research CVE"
echo "  python3 psavvy_ai.py --ai-research CVE-2024-1234"
echo ""
echo "  # Interactive AI mode"
echo "  python3 psavvy_ai.py --ai-interactive"
echo ""
