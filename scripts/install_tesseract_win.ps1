<#
.SYNOPSIS
  Installs Tesseract-OCR 5.x and Korean traineddata on Windows.

.NOTES
  Requires: Windows 10/11 + Winget (Microsoft Store App Installer)
#>

# Ensure Chocolatey is available (optional, usually present on GH runners)
# choco --version

Write-Host "🍫 Installing Tesseract-OCR using Chocolatey..."
try {
    # Install Tesseract using Chocolatey. Adjust parameters as needed.
    # -y confirms prompts.
    # /UseSystemPath adds Tesseract to the system PATH.
    choco install tesseract-ocr --params "'/UseSystemPath'" -y --force --no-progress -r --log-file C:\tesseract_install.log

    # Verify installation path (adjust if needed based on choco version/defaults)
    $tesseractPath = "C:\Program Files\Tesseract-OCR"
    $tessdataDir = Join-Path $tesseractPath "tessdata"

    if (-not (Test-Path $tessdataDir)) {
        Write-Error "Tesseract installation seems to have failed or the path is incorrect: $tesseractPath"
        exit 1
    }

    Write-Host "🌍 Downloading Korean traineddata..."
    # Using tessdata_best for potentially better accuracy
    $korDataUrl = "https://github.com/tesseract-ocr/tessdata_best/raw/main/kor.traineddata"
    $korDataPath = Join-Path $tessdataDir "kor.traineddata"

    # Ensure the tessdata directory exists before downloading
    if (Test-Path $tessdataDir) {
        Invoke-WebRequest -Uri $korDataUrl -OutFile $korDataPath -UseBasicParsing
        Write-Host "✅ Korean traineddata downloaded to $korDataPath"
    } else {
        Write-Error "❌ tessdata directory not found at $tessdataDir after installation attempt."
        exit 1
    }

    Write-Host "✅ Tesseract installation and language data setup complete."

} catch {
    Write-Error "❌ Failed to install Tesseract or download language data: $($_.Exception.Message)"
    # Optional: Output install log for debugging
    if (Test-Path C:\tesseract_install.log) { 
        Write-Host "--- Tesseract Install Log (C:\tesseract_install.log) ---"
        Get-Content C:\tesseract_install.log | Write-Host 
    }
    exit 1
} 