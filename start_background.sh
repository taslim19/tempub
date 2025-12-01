#!/bin/bash
# Script to start multi_client_v2.py in the background

echo "Starting multi_client_v2.py in background..."
nohup python3 multi_client_v2.py > multi_client.log 2>&1 &
echo $! > multi_client.pid

echo "✓ Multi-client launcher started in background!"
echo "  PID: $(cat multi_client.pid)"
echo "  Logs: multi_client.log"
echo ""
echo "To stop: kill $(cat multi_client.pid)"
echo "To view logs: tail -f multi_client.log"

