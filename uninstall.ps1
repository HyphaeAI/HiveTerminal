# HiveTerminal Uninstaller for Windows
# Run from PowerShell: irm https://raw.githubusercontent.com/YOUR_REPO/main/uninstall.ps1 | iex

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "HiveTerminal Uninstaller for Windows" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Detect installation directory
$InstallDir = $null
$PossibleDirs = @(
    "$env:USERPROFILE\hiveterminal",
    "$env:USERPROFILE\.hiveterminal",
    "$(Get-Location)\hiveterminal"
)

foreach ($dir in $PossibleDirs) {
    if (Test-Path $dir) {
        $InstallDir = $dir
        break
    }
}

# Confirm uninstall
Write-Host "This will remove:" -ForegroundColor Yellow
Write-Host "  - HiveTerminal installation directory"
Write-Host "  - Configuration files (~/.vibe/)"
Write-Host "  - Environment files (~/.vibe/.env)"
Write-Host "  - Memory database (.hive_memory/)"
Write-Host "  - Environment variables"
Write-Host "  - PATH entries"
Write-Host ""
Write-Host "WARNING: This action cannot be undone!" -ForegroundColor Red
Write-Host ""

$confirmation = Read-Host "Are you sure you want to uninstall HiveTerminal? (y/N)"
if ($confirmation -ne 'y' -and $confirmation -ne 'Y') {
    Write-Host "Uninstall cancelled." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "Starting uninstall..." -ForegroundColor Green
Write-Host ""

# 1. Remove installation directory
if ($InstallDir -and (Test-Path $InstallDir)) {
    Write-Host "[1/7] Removing installation directory: $InstallDir" -ForegroundColor Green
    Remove-Item -Path $InstallDir -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "      ✓ Removed" -ForegroundColor Green
} else {
    Write-Host "[1/7] Installation directory not found (already removed?)" -ForegroundColor Yellow
}

# 2. Remove configuration directory
$ConfigDir = "$env:USERPROFILE\.vibe"
if (Test-Path $ConfigDir) {
    Write-Host "[2/7] Removing configuration directory: $ConfigDir" -ForegroundColor Green
    Remove-Item -Path $ConfigDir -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "      ✓ Removed" -ForegroundColor Green
} else {
    Write-Host "[2/7] Configuration directory not found" -ForegroundColor Yellow
}

# 3. Remove memory database (if in current directory)
if (Test-Path ".hive_memory") {
    Write-Host "[3/7] Removing memory database: .hive_memory/" -ForegroundColor Green
    Remove-Item -Path ".hive_memory" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "      ✓ Removed" -ForegroundColor Green
} else {
    Write-Host "[3/7] Memory database not found in current directory" -ForegroundColor Yellow
}

# 4. Remove backups and logs (if in current directory)
if (Test-Path ".hive_backups") {
    Write-Host "[4/7] Removing backups: .hive_backups/" -ForegroundColor Green
    Remove-Item -Path ".hive_backups" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "      ✓ Removed" -ForegroundColor Green
}

if (Test-Path ".hive_logs") {
    Write-Host "[4/7] Removing logs: .hive_logs/" -ForegroundColor Green
    Remove-Item -Path ".hive_logs" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "      ✓ Removed" -ForegroundColor Green
}

# 5. Remove environment variables
Write-Host "[5/7] Removing environment variables..." -ForegroundColor Green
try {
    [Environment]::SetEnvironmentVariable("XIAOMI_MIMO_API_KEY", $null, "User")
    [Environment]::SetEnvironmentVariable("HIVE_MODE", $null, "User")
    Write-Host "      ✓ Removed environment variables" -ForegroundColor Green
} catch {
    Write-Host "      ⚠ Could not remove environment variables" -ForegroundColor Yellow
}

# 6. Remove from PATH
Write-Host "[6/7] Removing from PATH..." -ForegroundColor Green
try {
    $currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
    $newPath = ($currentPath -split ';' | Where-Object { $_ -notlike "*hiveterminal*" }) -join ';'
    [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
    Write-Host "      ✓ Cleaned PATH" -ForegroundColor Green
} catch {
    Write-Host "      ⚠ Could not clean PATH" -ForegroundColor Yellow
}

# 7. Remove wrapper scripts
Write-Host "[7/7] Removing wrapper scripts..." -ForegroundColor Green
$WrapperPaths = @(
    "$env:USERPROFILE\hiveterminal\hive.bat",
    "$env:USERPROFILE\.local\bin\hive.bat",
    "$env:USERPROFILE\AppData\Local\Microsoft\WindowsApps\hive.bat"
)

foreach ($wrapper in $WrapperPaths) {
    if (Test-Path $wrapper) {
        Remove-Item -Path $wrapper -Force -ErrorAction SilentlyContinue
        Write-Host "      ✓ Removed $wrapper" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "✓ HiveTerminal has been completely uninstalled" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Removed:" -ForegroundColor Green
Write-Host "  ✓ Installation directory"
Write-Host "  ✓ Configuration files"
Write-Host "  ✓ Memory database"
Write-Host "  ✓ Environment variables"
Write-Host "  ✓ PATH entries"
Write-Host ""
Write-Host "Note: Please restart PowerShell for changes to take effect" -ForegroundColor Yellow
Write-Host ""
Write-Host "Thank you for using HiveTerminal!" -ForegroundColor Cyan
Write-Host ""
