# How to Run Multi-Client in Background

## Method 1: Using nohup (Easiest)

```bash
# Start in background
nohup python3 multi_client.py > multi_client.log 2>&1 &

# Or use the helper script
chmod +x start_background.sh
./start_background.sh
```

**To stop:**
```bash
# Find and kill the process
pkill -f multi_client.py

# Or use the stop script
chmod +x stop_clients.sh
./stop_clients.sh
```

**To view logs:**
```bash
tail -f multi_client.log
```

---

## Method 2: Using screen (Recommended for VPS)

```bash
# Install screen (if not installed)
sudo apt-get install screen  # Debian/Ubuntu
# or
sudo yum install screen      # CentOS/RHEL

# Start a screen session
screen -S ultroid

# Run the launcher
python3 multi_client.py

# Detach: Press Ctrl+A then D
# Reattach: screen -r ultroid
# List sessions: screen -ls
# Kill session: screen -X -S ultroid quit
```

---

## Method 3: Using tmux

```bash
# Install tmux (if not installed)
sudo apt-get install tmux

# Start a tmux session
tmux new -s ultroid

# Run the launcher
python3 multi_client.py

# Detach: Press Ctrl+B then D
# Reattach: tmux attach -t ultroid
# List sessions: tmux ls
# Kill session: tmux kill-session -t ultroid
```

---

## Method 4: Using systemd (Best for production)

Create `/etc/systemd/system/ultroid-multi.service`:

```ini
[Unit]
Description=Ultroid Multi-Client Launcher
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/tempub
ExecStart=/usr/bin/python3 /path/to/tempub/multi_client.py
Restart=always
RestartSec=10
StandardOutput=append:/path/to/tempub/multi_client.log
StandardError=append:/path/to/tempub/multi_client.log

[Install]
WantedBy=multi-user.target
```

**Commands:**
```bash
# Enable and start
sudo systemctl enable ultroid-multi
sudo systemctl start ultroid-multi

# Check status
sudo systemctl status ultroid-multi

# View logs
sudo journalctl -u ultroid-multi -f

# Stop
sudo systemctl stop ultroid-multi

# Restart
sudo systemctl restart ultroid-multi
```

---

## Method 5: Using Python's daemon (Advanced)

The script can be modified to daemonize itself, but the above methods are simpler.

---

## Quick Reference

### Check if running:
```bash
ps aux | grep multi_client.py
ps aux | grep pyUltroid
```

### View all Ultroid processes:
```bash
pgrep -f pyUltroid
```

### Stop all Ultroid processes:
```bash
pkill -f pyUltroid
pkill -f multi_client.py
```

### View logs:
```bash
# Launcher logs
tail -f multi_client.log

# Individual client logs (if using client directories)
tail -f client_1/*.log
tail -f client_2/*.log
```

