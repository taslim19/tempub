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
    
    # Use indirect variable expansion for numbered variables
    local api_id_var="API_ID$suffix"
    local api_hash_var="API_HASH$suffix"
    local session_var="SESSION$suffix"
    local mongo_uri_var="MONGO_URI$suffix"
    
    local api_id_val="${!api_id_var:-$API_ID}"
    local api_hash_val="${!api_hash_var:-$API_HASH}"
    local session_val="${!session_var:-$SESSION}"
    local mongo_uri_val="${!mongo_uri_var:-$MONGO_URI}"
    
    # Check if required vars exist
    if [ -z "$api_id_val" ]; then
        echo "✗ Client $num: Skipped (missing API_ID)"
        return 1
    fi
    
    if [ -z "$api_hash_val" ]; then
        echo "✗ Client $num: Skipped (missing API_HASH)"
        return 1
    fi
    
    if [ -z "$session_val" ]; then
        echo "✗ Client $num: Skipped (missing SESSION)"
        return 1
    fi
    
    if [ -z "$mongo_uri_val" ]; then
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
    
    # Set PYTHONPATH to parent directory so pyUltroid can be found
    export PYTHONPATH="$(cd .. && pwd):${PYTHONPATH:-}"
    
    # Set environment variables
    export API_ID="$api_id_val"
    export API_HASH="$api_hash_val"
    export SESSION="$session_val"
    
    # Unique database
    DB_NAME="UltroidDB$num"
    if [[ "$mongo_uri_val" == */ ]]; then
        export MONGO_URI="${mongo_uri_val}$DB_NAME"
    else
        export MONGO_URI="${mongo_uri_val}/$DB_NAME"
    fi
    
    # Optional vars (use indirect expansion)
    local log_channel_var="LOG_CHANNEL$suffix"
    local bot_token_var="BOT_TOKEN$suffix"
    local log_channel_val="${!log_channel_var:-$LOG_CHANNEL}"
    local bot_token_val="${!bot_token_var:-$BOT_TOKEN}"
    
    [ -n "$log_channel_val" ] && export LOG_CHANNEL="$log_channel_val"
    [ -n "$bot_token_val" ] && export BOT_TOKEN="$bot_token_val"
    
    # Start in background with arguments
    nohup python3 -m pyUltroid "$api_id_val" "$api_hash_val" "$session_val" "" "" > "../client_${num}.log" 2>&1 &
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

