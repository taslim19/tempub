# PowerShell script to stop multi_client_v2.py and all Ultroid clients

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Stopping Multi-Client Ultroid Processes" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host

# Function to get command line from process
function Get-ProcessCommandLine {
    param($ProcessId)
    $wmiProcess = Get-CimInstance Win32_Process -Filter "ProcessId = $ProcessId"
    return $wmiProcess.CommandLine
}

# Stop multi_client_v2.py
Write-Host "Looking for multi_client_v2.py..." -ForegroundColor Yellow
$multiClientProcesses = Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    $cmdLine = Get-ProcessCommandLine $_.Id
    $cmdLine -like "*multi_client_v2*"
}

if ($multiClientProcesses) {
    $multiClientProcesses | Stop-Process -Force -ErrorAction SilentlyContinue
    Write-Host "✓ Stopped multi_client_v2.py launcher" -ForegroundColor Green
} else {
    Write-Host "✗ multi_client_v2.py not running" -ForegroundColor Red
}

Start-Sleep -Seconds 1

# Stop pyUltroid processes
Write-Host "Looking for pyUltroid processes..." -ForegroundColor Yellow
$ultroidProcesses = Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    $cmdLine = Get-ProcessCommandLine $_.Id
    $cmdLine -like "*pyUltroid*"
}

if ($ultroidProcesses) {
    $count = ($ultroidProcesses | Measure-Object).Count
    $ultroidProcesses | Stop-Process -Force -ErrorAction SilentlyContinue
    Write-Host "✓ Stopped $count Ultroid client(s)" -ForegroundColor Green
} else {
    Write-Host "✗ No Ultroid clients running" -ForegroundColor Red
}

Start-Sleep -Seconds 1

# Verify everything is stopped
Write-Host
Write-Host "Verifying all processes stopped..." -ForegroundColor Yellow
$remaining = Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    $cmdLine = Get-ProcessCommandLine $_.Id
    $cmdLine -match "multi_client_v2|pyUltroid"
}

if (-not $remaining) {
    Write-Host "✓ All processes stopped successfully!" -ForegroundColor Green
} else {
    $count = ($remaining | Measure-Object).Count
    Write-Host "⚠ Warning: $count process(es) still running" -ForegroundColor Yellow
    Write-Host "Remaining processes:" -ForegroundColor Yellow
    $remaining | ForEach-Object {
        Write-Host "  PID: $($_.Id) - $((Get-ProcessCommandLine $_.Id))" -ForegroundColor Yellow
    }
    Write-Host
    Write-Host "Force killing remaining processes..." -ForegroundColor Yellow
    $remaining | Stop-Process -Force -ErrorAction SilentlyContinue
    Write-Host "✓ Force killed remaining processes" -ForegroundColor Green
}

Write-Host
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Done!" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

