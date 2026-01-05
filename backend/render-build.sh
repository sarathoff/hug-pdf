#!/usr/bin/env bash
# Render build script for backend
set -e  # Exit on error

echo "=== Starting Render Build ==="
echo "=== Installing system dependencies ==="

# Update package list
apt-get update

# Install TeX Live packages for LaTeX compilation
# Including latex-extra for commonly used packages (geometry, hyperref, amsmath, etc.)
echo "Installing TeX Live packages..."
apt-get install -y \
    texlive-latex-base \
    texlive-fonts-recommended \
    texlive-latex-extra \
    texlive-fonts-extra

# Clean up apt cache to save space
apt-get clean
rm -rf /var/lib/apt/lists/*

echo "=== Verifying pdflatex installation ==="
which pdflatex
pdflatex --version

echo "=== Installing Python dependencies ==="
pip install --upgrade pip
pip install -r requirements.txt

echo "=== Build complete ==="
