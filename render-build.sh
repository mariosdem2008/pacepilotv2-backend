#!/usr/bin/env bash
# Install Tesseract during the build phase
apt-get update && apt-get install -y tesseract-ocr

# Proceed with Python dependencies
pip install -r requirements.txt
