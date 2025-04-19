#!/usr/bin/env bash
set -e
echo "🔧 Updating apt cache..."
sudo apt-get update -y

echo "📦 Installing Tesseract & Korean data..."
sudo apt-get install -y tesseract-ocr libtesseract-dev tesseract-ocr-kor
echo "✅ Done." 