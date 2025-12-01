#!/bin/bash
# Script to stop multi_client_v2.py and all Ultroid clients

echo "Stopping multi-client launcher and clients..."

# Stop the launcher if PID file exists
if [ -f multi_client.pid ]; then
    LAUNCHER_PID=$(cat multi_client.pid)
    if ps -p $LAUNCHER_PID > /dev/null 2>&1; then
        kill $LAUNCHER_PID 2>/dev/null
        echo "✓ Stopped launcher (PID: $LAUNCHER_PID)"
    else
        echo "✗ Launcher not running"
    fi
    rm -f multi_client.pid
else
    echo "✗ No PID file found"
fi

# Stop all pyUltroid processes
PYULTROID_PIDS=$(pgrep -f "pyUltroid")
if [ -n "$PYULTROID_PIDS" ]; then
    echo "$PYULTROID_PIDS" | xargs kill 2>/dev/null
    echo "✓ Stopped all Ultroid clients"
else
    echo "✗ No Ultroid clients running"
fi

# Stop client wrapper processes
WRAPPER_PIDS=$(pgrep -f "_client_.*_wrapper.py")
if [ -n "$WRAPPER_PIDS" ]; then
    echo "$WRAPPER_PIDS" | xargs kill 2>/dev/null
    echo "✓ Stopped wrapper processes"
fi

echo ""
echo "Done!"

