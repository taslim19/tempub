# How to Kill/Stop multi_client_v2.py

## Quick Methods

### Method 1: Find and Kill Process (Linux/Mac)

**Kill multi_client_v2.py launcher:**
```bash
pkill -f multi_client_v2.py
```

**Kill all Ultroid clients it started:**
```bash
pkill -f pyUltroid
```

**Kill everything at once:**
```bash
pkill -f multi_client_v2.py && pkill -f pyUltroid
```

### Method 2: Using ps and kill (Linux/Mac)

**Find the process:**
```bash
ps aux | grep multi_client_v2.py
```

**Kill by PID:**
```bash
kill <PID>
# Or force kill:
kill -9 <PID>
```

**Kill all related processes:**
```bash
ps aux | grep multi_client_v2.py | grep -v grep | awk '{print $2}' | xargs kill
ps aux | grep pyUltroid | grep -v grep | awk '{print $2}' | xargs kill
```

### Method 3: Windows PowerShell

**Find processes:**
```powershell
Get-Process | Where-Object {$_.ProcessName -like "*python*"} | Select-Object Id, ProcessName, CommandLine
```

**Kill by process name:**
```powershell
Get-Process python | Where-Object {$_.MainWindowTitle -like "*multi_client_v2*"} | Stop-Process -Force
```

**Kill all Python processes (CAREFUL - kills all Python):**
```powershell
Get-Process python | Stop-Process -Force
```

**Kill specific process by PID:**
```powershell
Stop-Process -Id <PID> -Force
```

### Method 4: Using Task Manager (Windows GUI)

1. Open Task Manager (Ctrl+Shift+Esc)
2. Go to "Details" tab
3. Find `python.exe` processes
4. Right-click → End Task

## Complete Stop Script

### Linux/Mac (stop_all.sh)

```bash
#!/bin/bash
echo "Stopping multi_client_v2.py and all Ultroid clients..."

# Kill multi_client_v2.py
pkill -f multi_client_v2.py 2>/dev/null && echo "✓ Stopped multi_client_v2.py"

# Kill all pyUltroid processes
pkill -f "pyUltroid" 2>/dev/null && echo "✓ Stopped all Ultroid clients"

# Kill wrapper scripts
pkill -f "_client_.*_wrapper.py" 2>/dev/null && echo "✓ Stopped wrapper processes"

echo "Done!"
```

### Windows PowerShell (stop_all.ps1)

```powershell
Write-Host "Stopping multi_client_v2.py and all Ultroid clients..."

# Kill processes containing multi_client_v2
Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*multi_client_v2*"
} | Stop-Process -Force -ErrorAction SilentlyContinue

# Kill pyUltroid processes
Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*pyUltroid*"
} | Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host "Done!"
```

## One-Line Commands

### Linux/Mac:
```bash
pkill -f "multi_client_v2|pyUltroid"
```

### Windows (PowerShell):
```powershell
Get-Process python | Where-Object {$_.CommandLine -match "multi_client_v2|pyUltroid"} | Stop-Process -Force
```

## Check What's Running

### Linux/Mac:
```bash
ps aux | grep -E "multi_client_v2|pyUltroid" | grep -v grep
```

### Windows:
```powershell
Get-Process python | Format-Table Id, ProcessName, @{Label="CommandLine";Expression={$_.CommandLine}}
```

## Important Notes

⚠️ **Warning:**
- Killing processes forcefully can cause data loss
- It's better to use Ctrl+C if the script is running in foreground
- Stop clients gracefully if possible

✅ **Best Practice:**
- Use Ctrl+C if running in terminal (foreground)
- Use the kill commands above if running in background
- Check processes are actually stopped after killing

## Verify Everything Stopped

```bash
# Linux/Mac
ps aux | grep -E "multi_client_v2|pyUltroid" | grep -v grep

# Windows
Get-Process python | Where-Object {$_.CommandLine -match "multi_client_v2|pyUltroid"}
```

If nothing shows up, all processes are stopped! ✅

