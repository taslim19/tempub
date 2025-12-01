#!/bin/bash
# Simple bash script to start multiple Ultroid clients
# Usage: ./start_clients.sh

# Load .env if it exists
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Function to start a client
start_client() {
    local num=$1
    local suffix=""
    [ $num -gt 1 ] && suffix=$((num-1))
    
    # Check if required vars exist
    if [ -z "${API_ID${suffix}}" ] && [ -z "$API_ID" ]; then
        echo "✗ Client $num: Skipped (missing API_ID)"
        return 1
    fi
    
    if [ -z "${API_HASH${suffix}}" ] && [ -z "$API_HASH" ]; then
        echo "✗ Client $num: Skipped (missing API_HASH)"
        return 1
    fi
    
    if [ -z "${SESSION${suffix}}" ] && [ -z "$SESSION" ]; then
        echo "✗ Client $num: Skipped (missing SESSION)"
        return 1
    fi
    
    if [ -z "${MONGO_URI${suffix}}" ] && [ -z "$MONGO_URI" ]; then
        echo "✗ Client $num: Skipped (missing MONGO_URI)"
        return 1
    fi
    
    echo "✓ Starting Client $num..."
    
    # Create client directory
    mkdir -p "client_$num"
    cd "client_$num"
    
    # Create symlinks
    [ ! -e plugins ] && ln -s ../plugins plugins 2>/dev/null
    [ ! -e resources ] && ln -s ../resources resources 2>/dev/null
    [ ! -e assistant ] && ln -s ../assistant assistant 2>/dev/null
    [ ! -e strings ] && ln -s ../strings strings 2>/dev/null
    [ ! -e addons ] && ln -s ../addons addons 2>/dev/null
    [ ! -e .git ] && ln -s ../.git .git 2>/dev/null
    
    # Copy .env if exists
    [ -f ../.env ] && cp ../.env .env
    
    # Set environment variables
    export API_ID="${API_ID${suffix}:-$API_ID}"
    export API_HASH="${API_HASH${suffix}:-$API_HASH}"
    export SESSION="${SESSION${suffix}:-$SESSION}"
    
    # Unique database
    DB_NAME="UltroidDB$num"
    if [[ "${MONGO_URI${suffix}:-$MONGO_URI}" == */ ]]; then
        export MONGO_URI="${MONGO_URI${suffix}:-$MONGO_URI}$DB_NAME"
    else
        export MONGO_URI="${MONGO_URI${suffix}:-$MONGO_URI}/$DB_NAME"
    fi
    
    # Optional vars
    [ -n "${LOG_CHANNEL${suffix}}" ] && export LOG_CHANNEL="${LOG_CHANNEL${suffix}}"
    [ -n "${BOT_TOKEN${suffix}}" ] && export BOT_TOKEN="${BOT_TOKEN${suffix}}"
    
    # Start in background
    nohup python3 -m pyUltroid > "../client_${num}.log" 2>&1 &
    CLIENT_PID=$!
    
    echo "  → Client $num started (PID: $CLIENT_PID)"
    echo $CLIENT_PID > "../client_${num}.pid"
    
    cd ..
    return 0
}

echo "=========================================="
echo "Multi-Client Ultroid Launcher (Bash)"
echo "=========================================="
echo

# Start clients 1-5
for i in {1..5}; do
    start_client $i
    sleep 1
done

echo
echo "=========================================="
echo "All clients started!"
echo "Logs: client_1.log, client_2.log, etc."
echo "PIDs: client_1.pid, client_2.pid, etc."
echo "=========================================="
echo
echo "To stop all clients:"
echo "  for pid in client_*.pid; do kill \$(cat \$pid) 2>/dev/null; done"
echo "  rm client_*.pid"

