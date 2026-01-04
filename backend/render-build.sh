#!/usr/bin/env bash
# Render build script for backend

# Install system dependencies (TeX Live for LaTeX compilation)
apt-get update
apt-get install -y texlive-latex-base texlive-fonts-recommended texlive-latex-extra

# Install Python dependencies
pip install -r requirements.txt
