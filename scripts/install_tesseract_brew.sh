#!/usr/bin/env bash
set -e
brew update
brew install tesseract
# tessdata-fast 포함 여부 확인
tessdata_dir="$(brew --prefix)/share/tessdata"
[[ -f "${tessdata_dir}/kor.traineddata" ]] || \
  curl -L -o "${tessdata_dir}/kor.traineddata" \
  https://github.com/tesseract-ocr/tessdata/raw/main/kor.traineddata
echo "✅ Tesseract installed in $(brew --prefix)." 