#!/bin/bash
# Script to clean up all log and PID files from multi-client setup

echo "=========================================="
echo "Cleaning Up Multi-Client Log & PID Files"
echo "=========================================="
echo

CLEANED=0

# Remove client log files (client_1.log, client_2.log, etc.)
echo "Removing client log files..."
for i in {1..5}; do
    if [ -f "client_${i}.log" ]; then
        rm -f "client_${i}.log"
        echo "  ✓ Removed client_${i}.log"
        CLEANED=$((CLEANED + 1))
    fi
done

# Remove client PID files (client_1.pid, client_2.pid, etc.)
echo "Removing client PID files..."
for i in {1..5}; do
    if [ -f "client_${i}.pid" ]; then
        rm -f "client_${i}.pid"
        echo "  ✓ Removed client_${i}.pid"
        CLEANED=$((CLEANED + 1))
    fi
done

# Remove ultroid log files (ultroid1.log, ultroid2.log, etc.)
echo "Removing ultroid log files..."
for i in {1..10}; do
    if [ -f "ultroid${i}.log" ]; then
        rm -f "ultroid${i}.log"
        echo "  ✓ Removed ultroid${i}.log"
        CLEANED=$((CLEANED + 1))
    fi
done

# Remove multi_client.pid if exists
if [ -f "multi_client.pid" ]; then
    rm -f "multi_client.pid"
    echo "  ✓ Removed multi_client.pid"
    CLEANED=$((CLEANED + 1))
fi

# Remove nohup.out if exists
if [ -f "nohup.out" ]; then
    rm -f "nohup.out"
    echo "  ✓ Removed nohup.out"
    CLEANED=$((CLEANED + 1))
fi

echo
if [ "$CLEANED" -gt 0 ]; then
    echo "=========================================="
    echo "✓ Cleaned up $CLEANED file(s) successfully!"
    echo "=========================================="
else
    echo "=========================================="
    echo "✗ No log/PID files found to clean up"
    echo "=========================================="
fi

