#!/bin/bash
# Setup script for BioFinder Finder MCP

set -e

echo "=== BioFinder Finder MCP Setup ==="
echo

# Check Python version
echo "Checking Python version..."
python3 --version

# Install dependencies
echo "Installing dependencies..."
pip install --break-system-packages -r requirements.txt

# Make scripts executable
echo "Making scripts executable..."
chmod +x biofinder_server.py
chmod +x biofinder_client.py
chmod +x biofinder

echo
echo "✓ Setup complete!"
echo
echo "Usage examples:"
echo "  biofinder # interactive mode"
echo "  ./biofinder_client.py find fastqc"
echo "  ./biofinder_client.py search 'quality control'"
echo "  ./biofinder_client.py interactive"
echo
