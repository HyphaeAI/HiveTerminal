# HiveTerminal One-Line Installer for Windows
# Usage: irm https://raw.githubusercontent.com/HyphaeAI/HiveTerminal/master/install.ps1 | iex

Write-Host "🐝 Installing HiveTerminal..." -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "⚠️  Not running as Administrator" -ForegroundColor Yellow
    Write-Host "   Some features may require elevated privileges" -ForegroundColor Yellow
    Write-Host ""
}

# Check Python version
Write-Host "Checking Python installation..." -ForegroundColor White
$pythonCmd = $null
$pythonVersion = $null

# Try python3 first, then python
foreach ($cmd in @("python3", "python")) {
    try {
        $version = & $cmd --version 2>&1
        if ($version -match "Python (\d+)\.(\d+)") {
            $major = [int]$matches[1]
            $minor = [int]$matches[2]
            if ($major -ge 3 -and $minor -ge 10) {
                $pythonCmd = $cmd
                $pythonVersion = "$major.$minor"
                break
            }
        }
    } catch {
        continue
    }
}

if (-not $pythonCmd) {
    Write-Host "❌ Python 3.10+ not found" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Python 3.10 or higher:" -ForegroundColor Yellow
    Write-Host "  1. Visit: https://www.python.org/downloads/" -ForegroundColor White
    Write-Host "  2. Download Python 3.13 (recommended)" -ForegroundColor White
    Write-Host "  3. During installation, check 'Add Python to PATH'" -ForegroundColor White
    Write-Host "  4. Restart PowerShell and run this installer again" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host "✓ Using Python: $pythonCmd ($pythonVersion)" -ForegroundColor Green

# Check Git
Write-Host "Checking Git installation..." -ForegroundColor White
try {
    $gitVersion = git --version 2>&1
    Write-Host "✓ Git installed: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Git not found" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Git:" -ForegroundColor Yellow
    Write-Host "  1. Visit: https://git-scm.com/download/win" -ForegroundColor White
    Write-Host "  2. Download and install Git for Windows" -ForegroundColor White
    Write-Host "  3. Restart PowerShell and run this installer again" -ForegroundColor White
    Write-Host ""
    exit 1
}

# Check if Ollama is installed (optional)
Write-Host "Checking Ollama installation..." -ForegroundColor White
try {
    $ollamaVersion = ollama --version 2>&1
    Write-Host "✓ Ollama detected" -ForegroundColor Green
} catch {
    Write-Host ""
    Write-Host "ℹ️  Ollama not found (optional for local AI models)" -ForegroundColor Cyan
    Write-Host "   To install Ollama later, visit: https://ollama.ai" -ForegroundColor White
}

# Set installation directory
$installDir = "$env:USERPROFILE\.hiveterminal"

if (Test-Path $installDir) {
    Write-Host ""
    Write-Host "⚠️  HiveTerminal already installed at $installDir" -ForegroundColor Yellow
    $response = Read-Host "Do you want to reinstall? (y/N)"
    if ($response -ne "y" -and $response -ne "Y") {
        Write-Host "Installation cancelled." -ForegroundColor Yellow
        exit 0
    }
    Remove-Item -Path $installDir -Recurse -Force
}

# Clone repository
Write-Host ""
Write-Host "📦 Cloning HiveTerminal..." -ForegroundColor Cyan
try {
    git clone https://github.com/HyphaeAI/HiveTerminal.git $installDir
    Set-Location $installDir
} catch {
    Write-Host "❌ Failed to clone repository" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

Write-Host "✓ Repository cloned" -ForegroundColor Green

# Create virtual environment
Write-Host ""
Write-Host "🔧 Creating virtual environment..." -ForegroundColor Cyan
try {
    & $pythonCmd -m venv .venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

# Activate virtual environment and install dependencies
Write-Host ""
Write-Host "📚 Installing dependencies..." -ForegroundColor Cyan
Write-Host "   This may take a few minutes..." -ForegroundColor White

$venvPython = Join-Path $installDir ".venv\Scripts\python.exe"

try {
    # Upgrade pip
    & $venvPython -m pip install --upgrade pip --quiet
    
    # Install HiveTerminal
    & $venvPython -m pip install -e . --quiet
    
    # Install Vibe
    & $venvPython -m pip install -e Vibe\ --quiet
    
    Write-Host "✓ Dependencies installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

# Create wrapper script
Write-Host ""
Write-Host "🔗 Creating hive command..." -ForegroundColor Cyan

$wrapperScript = @"
@echo off
cd /d "$installDir"
call .venv\Scripts\activate.bat
python -m hiveterminal.cli.entrypoint %*
"@

$wrapperPath = Join-Path $installDir "hive.bat"
$wrapperScript | Out-File -FilePath $wrapperPath -Encoding ASCII

Write-Host "✓ Wrapper script created" -ForegroundColor Green

# Add to PATH
Write-Host ""
Write-Host "🔗 Adding to PATH..." -ForegroundColor Cyan

$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($currentPath -notlike "*$installDir*") {
    try {
        [Environment]::SetEnvironmentVariable(
            "Path",
            "$currentPath;$installDir",
            "User"
        )
        Write-Host "✓ Added to PATH" -ForegroundColor Green
        Write-Host "   You'll need to restart PowerShell for this to take effect" -ForegroundColor Yellow
    } catch {
        Write-Host "⚠️  Could not add to PATH automatically" -ForegroundColor Yellow
        Write-Host "   Add manually: $installDir" -ForegroundColor White
    }
} else {
    Write-Host "✓ Already in PATH" -ForegroundColor Green
}

# Run initial setup
Write-Host ""
Write-Host "⚙️  Running initial setup..." -ForegroundColor Cyan
Write-Host ""
Write-Host "You'll be prompted to:" -ForegroundColor White
Write-Host "  1. Choose your AI provider (Ollama recommended for local/free)" -ForegroundColor White
Write-Host "  2. Select or enter your model name" -ForegroundColor White
Write-Host ""

try {
    & $venvPython -m hiveterminal.cli.entrypoint --setup
} catch {
    Write-Host "⚠️  Setup encountered an issue, but installation is complete" -ForegroundColor Yellow
    Write-Host "   You can run 'hive --setup' later" -ForegroundColor White
}

# Installation complete
Write-Host ""
Write-Host "✅ Installation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "🎉 HiveTerminal is ready to use!" -ForegroundColor Cyan
Write-Host ""
Write-Host "📝 Next steps:" -ForegroundColor White
Write-Host "  1. Restart PowerShell (to refresh PATH)" -ForegroundColor White
Write-Host "  2. Install Ollama if you haven't: https://ollama.ai" -ForegroundColor White
Write-Host "  3. Download an AI model (see recommendations below)" -ForegroundColor White
Write-Host "  4. Type: hive" -ForegroundColor White
Write-Host ""
Write-Host "🤖 Recommended AI Models:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  For best results (7B+ parameters):" -ForegroundColor White
Write-Host "    ollama pull qwen2.5-coder:7b        # 4.7GB - Best for coding" -ForegroundColor Gray
Write-Host "    ollama pull deepseek-coder:6.7b     # 3.8GB - Fast & capable" -ForegroundColor Gray
Write-Host ""
Write-Host "  For faster/smaller (may struggle with tools):" -ForegroundColor White
Write-Host "    ollama pull qwen2.5-coder:1.5b      # 986MB - Fastest" -ForegroundColor Gray
Write-Host "    ollama pull qwen2.5:3b              # 1.9GB - Balanced" -ForegroundColor Gray
Write-Host ""
Write-Host "Quick commands:" -ForegroundColor White
Write-Host "  hive              - Start HiveTerminal" -ForegroundColor Gray
Write-Host "  hive --setup      - Run setup again" -ForegroundColor Gray
Write-Host "  hive --help       - Show help" -ForegroundColor Gray
Write-Host ""
Write-Host "Happy coding! 🐝" -ForegroundColor Cyan
