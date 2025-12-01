#!/usr/bin/env python3
"""
Simple Multi-Client Ultroid Launcher
Runs all clients from the base directory with environment variable isolation
"""
import os
import subprocess
import sys
import time

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    if os.path.exists(".env"):
        load_dotenv()
        print("✓ Loaded .env file")
except ImportError:
    pass

# Required variables for each client
REQUIRED_VARS = ["API_ID", "API_HASH", "SESSION", "MONGO_URI"]

def check_client_config(client_num):
    """Check if all required variables exist for a client"""
    suffix = "" if client_num == 1 else str(client_num - 1)
    missing = []
    for var in REQUIRED_VARS:
        key = var + suffix
        if not os.environ.get(key):
            missing.append(key)
    return len(missing) == 0, missing

def get_mongo_uri_with_db(client_num, base_uri):
    """Add unique database name to MongoDB URI"""
    unique_db = f"UltroidDB{client_num}"
    # Simple URI modification
    if base_uri.endswith('/'):
        return f"{base_uri}{unique_db}"
    else:
        return f"{base_uri}/{unique_db}"

def start_client(client_num):
    """Start a single Ultroid client"""
    suffix = "" if client_num == 1 else str(client_num - 1)
    
    # Check configuration
    has_config, missing = check_client_config(client_num)
    if not has_config:
        print(f"✗ Client {client_num}: Skipped (missing: {', '.join(missing)})")
        return None
    
    print(f"✓ Client {client_num}: Starting...")
    
    # Build environment for this client
    env = os.environ.copy()
    
    # Get base values
    api_id = os.environ.get(f"API_ID{suffix}") or os.environ.get("API_ID")
    api_hash = os.environ.get(f"API_HASH{suffix}") or os.environ.get("API_HASH")
    session = os.environ.get(f"SESSION{suffix}") or os.environ.get("SESSION")
    mongo_uri = os.environ.get(f"MONGO_URI{suffix}") or os.environ.get("MONGO_URI")
    
    # Set unique database
    env["MONGO_URI"] = get_mongo_uri_with_db(client_num, mongo_uri)
    
    # Optional variables
    log_channel = os.environ.get(f"LOG_CHANNEL{suffix}") or os.environ.get("LOG_CHANNEL")
    bot_token = os.environ.get(f"BOT_TOKEN{suffix}") or os.environ.get("BOT_TOKEN")
    
    if log_channel:
        env["LOG_CHANNEL"] = log_channel
    if bot_token:
        env["BOT_TOKEN"] = bot_token
    
    # Set unique session file directory using environment variable
    # Telethon will use this for session files
    session_dir = os.path.join(os.getcwd(), f"sessions_{client_num}")
    os.makedirs(session_dir, exist_ok=True)
    env["TELEGRAM_SESSION_DIR"] = session_dir
    
    # Set PYTHONPATH to current directory
    env["PYTHONPATH"] = os.getcwd()
    
    print(f"  → Database: UltroidDB{client_num}")
    print(f"  → Session directory: sessions_{client_num}/")
    
    try:
        # Run pyUltroid with client-specific environment
        process = subprocess.Popen(
            [sys.executable, "-m", "pyUltroid", api_id, api_hash, session, "", ""],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        print(f"  → Client {client_num} started (PID: {process.pid})")
        return process
    except Exception as e:
        print(f"  ✗ Error starting Client {client_num}: {e}")
        return None

def main():
    print("=" * 60)
    print("Simple Multi-Client Ultroid Launcher")
    print("=" * 60)
    print()
    
    processes = []
    
    # Try to start up to 5 clients
    for i in range(1, 6):
        process = start_client(i)
        if process:
            processes.append((i, process))
        time.sleep(1)  # Small delay between starts
    
    if not processes:
        print("\n✗ No clients were started. Check your environment variables.")
        print("Required variables: API_ID, API_HASH, SESSION, MONGO_URI")
        print("For multiple clients, add numbers: API_ID1, API_HASH1, SESSION1, etc.")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print(f"✓ Started {len(processes)} client(s):")
    for client_num, proc in processes:
        print(f"  - Client {client_num} (PID: {proc.pid})")
    print("=" * 60)
    print("\nAll clients are running in the background.")
    print("Press Ctrl+C to stop monitoring (clients will continue running).")
    print("To stop clients, kill their PIDs or use: pkill -f pyUltroid")
    print()
    
    # Monitor processes
    try:
        while True:
            time.sleep(5)
            # Check if any process died
            for client_num, proc in processes[:]:
                if proc.poll() is not None:
                    print(f"⚠ Client {client_num} (PID: {proc.pid}) has stopped!")
                    processes.remove((client_num, proc))
            
            if not processes:
                print("\n✗ All clients have stopped.")
                break
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped. Clients are still running.")
        print("To stop all clients, run: pkill -f pyUltroid")

if __name__ == "__main__":
    main()

