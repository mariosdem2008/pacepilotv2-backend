#!/usr/bin/env bash
echo "Starting build script..."
apt-get update && apt-get install -y tesseract-ocr
echo "Tesseract installed."
