#!/bin/bash
# Script to stop multi_client_v2.py and all Ultroid clients

echo "=========================================="
echo "Stopping Multi-Client Ultroid Processes"
echo "=========================================="
echo

# Stop multi_client_v2.py launcher
echo "Looking for multi_client_v2.py..."
if pkill -f multi_client_v2.py 2>/dev/null; then
    echo "✓ Stopped multi_client_v2.py launcher"
else
    echo "✗ multi_client_v2.py not running"
fi

sleep 1

# Stop all pyUltroid processes
echo "Looking for pyUltroid processes..."
PYULTROID_COUNT=$(pgrep -f "pyUltroid" | wc -l)
if [ "$PYULTROID_COUNT" -gt 0 ]; then
    pkill -f "pyUltroid" 2>/dev/null
    echo "✓ Stopped $PYULTROID_COUNT Ultroid client(s)"
else
    echo "✗ No Ultroid clients running"
fi

sleep 1

# Stop wrapper scripts
echo "Looking for wrapper scripts..."
WRAPPER_COUNT=$(pgrep -f "_client_.*_wrapper.py" | wc -l)
if [ "$WRAPPER_COUNT" -gt 0 ]; then
    pkill -f "_client_.*_wrapper.py" 2>/dev/null
    echo "✓ Stopped $WRAPPER_COUNT wrapper process(es)"
else
    echo "✗ No wrapper processes running"
fi

sleep 1

# Verify everything is stopped
echo
echo "Verifying all processes stopped..."
REMAINING=$(pgrep -f "multi_client_v2|pyUltroid" | wc -l)
if [ "$REMAINING" -eq 0 ]; then
    echo "✓ All processes stopped successfully!"
else
    echo "⚠ Warning: $REMAINING process(es) still running"
    echo "Remaining processes:"
    ps aux | grep -E "multi_client_v2|pyUltroid" | grep -v grep
    echo
    echo "Force killing remaining processes..."
    pkill -9 -f "multi_client_v2|pyUltroid" 2>/dev/null
    echo "✓ Force killed remaining processes"
fi

echo
echo "=========================================="
echo "Done!"
echo "=========================================="

