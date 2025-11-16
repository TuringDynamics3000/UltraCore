# UltraCore Operations Portal - Windows Setup Script
# Run this in PowerShell to clone and start the portal

Write-Host "🚀 UltraCore Operations Portal Setup" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check if git is installed
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Git is not installed. Please install Git first." -ForegroundColor Red
    Write-Host "Download from: https://git-scm.com/download/win" -ForegroundColor Yellow
    exit 1
}

# Check if Node.js is installed
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Node.js is not installed. Please install Node.js first." -ForegroundColor Red
    Write-Host "Download from: https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Git version: $(git --version)" -ForegroundColor Green
Write-Host "✅ Node version: $(node --version)" -ForegroundColor Green
Write-Host ""

# Set target directory
$targetDir = "$HOME\UltraCore"

# Clone or pull repository
if (Test-Path $targetDir) {
    Write-Host "📂 Repository exists. Pulling latest changes..." -ForegroundColor Yellow
    Set-Location $targetDir
    git pull origin main
} else {
    Write-Host "📥 Cloning UltraCore repository..." -ForegroundColor Yellow
    git clone https://github.com/TuringDynamics3000/UltraCore.git $targetDir
    Set-Location $targetDir
}

Write-Host "✅ Repository ready" -ForegroundColor Green
Write-Host ""

# Navigate to web-portal
$portalDir = "$targetDir\web-portal"
if (-not (Test-Path $portalDir)) {
    Write-Host "❌ web-portal directory not found!" -ForegroundColor Red
    exit 1
}

Set-Location $portalDir
Write-Host "📂 Working directory: $portalDir" -ForegroundColor Cyan
Write-Host ""

# Install dependencies
Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
npm install

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ npm install failed" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Dependencies installed" -ForegroundColor Green
Write-Host ""

# Prompt for OpenAI API key
Write-Host "🔑 OpenAI API Key Configuration" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
$apiKey = Read-Host "Enter your OpenAI API key (or press Enter to skip)"

if ($apiKey) {
    $env:OPENAI_API_KEY = $apiKey
    Write-Host "✅ OpenAI API key set for this session" -ForegroundColor Green
} else {
    Write-Host "⚠️  No API key provided. Larry AI will not work." -ForegroundColor Yellow
}

# Set JWT secret
$env:JWT_SECRET = "ultracore-dev-secret-$(Get-Random)"
Write-Host "✅ JWT secret generated" -ForegroundColor Green
Write-Host ""

# Start the development server
Write-Host "🚀 Starting Operations Portal..." -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Green
Write-Host "Backend:  http://localhost:3001" -ForegroundColor Green
Write-Host ""
Write-Host "Login credentials:" -ForegroundColor Yellow
Write-Host "  Email: admin@ultracore.com" -ForegroundColor Yellow
Write-Host "  Click 'Login as Admin' button" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

# Run dev server
npm run dev
