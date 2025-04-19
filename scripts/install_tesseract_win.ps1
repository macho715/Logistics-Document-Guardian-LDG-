<#
.SYNOPSIS
  Installs Tesseract-OCR 5.x and Korean traineddata on Windows.

.NOTES
  Requires: Windows 10/11 + Winget (Microsoft Store App Installer)
#>

Write-Host "🔧 Checking for Winget..."
winget --version | Out-Null

Write-Host "📦 Installing Tesseract-OCR..."
winget install --id=UB-Mannheim.TesseractOCR --source=winget --exact --accept-package-agreements --accept-source-agreements

# kor.traineddata 저장 위치 찾기
$dest = "C:\Program Files\Tesseract-OCR\tessdata\kor.traineddata"
if (-Not (Test-Path $dest))
{
    Write-Host "🌐 Downloading Korean traineddata..."
    Invoke-WebRequest -Uri "https://github.com/tesseract-ocr/tessdata/raw/main/kor.traineddata" -OutFile $dest
}

Write-Host "✅ Tesseract installation complete." 