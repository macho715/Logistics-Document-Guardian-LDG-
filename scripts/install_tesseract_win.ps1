<#
.SYNOPSIS
  Installs Tesseract-OCR 5.x and Korean traineddata on Windows.

.NOTES
  Requires: Windows 10/11 + Winget (Microsoft Store App Installer)
#>

Write-Host "🔧 Installing Tesseract-OCR via Chocolatey..."
# choco is usually pre-installed on GitHub windows-latest runners
choco install tesseract --yes --no-progress

# Check if installation was successful by testing the command
# This might throw an error if choco failed, which is desired
Write-Host "Verifying tesseract installation..."
tesseract --version

# Download kor.traineddata if needed
$tessdata_dir = "${Env:ProgramFiles}\Tesseract-OCR\tessdata"
$kor_data_path = Join-Path -Path $tessdata_dir -ChildPath "kor.traineddata"

if (!(Test-Path $kor_data_path)) {
    Write-Host "Downloading kor.traineddata..."
    if (!(Test-Path $tessdata_dir)) {
        New-Item -ItemType Directory -Force -Path $tessdata_dir
    }
    $uri = "https://github.com/tesseract-ocr/tessdata/raw/main/kor.traineddata"
    try {
        Invoke-WebRequest -Uri $uri -OutFile $kor_data_path -UseBasicParsing
        Write-Host "kor.traineddata downloaded successfully."
    } catch {
        Write-Error "Failed to download kor.traineddata: $_"
        exit 1 # Exit if download fails
    }
} else {
    Write-Host "kor.traineddata already exists."
}

Write-Host "✅ Tesseract setup completed." 