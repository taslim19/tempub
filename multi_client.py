import asyncio
import os
import subprocess
import sys

# Load environment variables from .env file if it exists
env_loaded = False
try:
    from dotenv import load_dotenv
    if os.path.exists(".env"):
        load_dotenv()
        env_loaded = True
    else:
        load_dotenv()  # Try loading anyway, might be in a different location
except ImportError:
    pass

vars = ["API_ID", "API_HASH", "SESSION", "MONGO_URI"]

def _check(z):
    new = []
    for var in vars:
        ent = os.environ.get(var + z)
        if not ent:
            return False, new
        new.append(ent)
    return True, new

print("=" * 50)
print("Multi-Client Ultroid Launcher")
print("=" * 50)
if env_loaded or os.path.exists(".env"):
    print("✓ Loading environment variables from .env file")
    print()
else:
    print("ℹ Note: No .env file found. Using environment variables only.")
    print()

started_clients = []

for z in range(5):
    n = str(z + 1)
    suffix = "" if z == 0 else str(z)  # Client 1 has no suffix, others use number
    fine, out = _check(suffix)
    if fine:
        print(f"✓ Client {n}: Configuration found")
        
        # Create environment dict with variables for this client
        env = os.environ.copy()
        env["MONGO_URI"] = out[3]  # MONGO_URI is passed via environment, not command line
        
        # Optional variables: LOG_CHANNEL and BOT_TOKEN (can have numbered variants)
        # Check for numbered variant first, then fallback to non-numbered
        log_channel_key = "LOG_CHANNEL" + suffix
        bot_token_key = "BOT_TOKEN" + suffix
        log_channel = os.environ.get(log_channel_key) or os.environ.get("LOG_CHANNEL")
        bot_token = os.environ.get(bot_token_key) or os.environ.get("BOT_TOKEN")
        
        if log_channel:
            env["LOG_CHANNEL"] = log_channel
            print(f"  → LOG_CHANNEL: {log_channel[:20]}...")
        if bot_token:
            env["BOT_TOKEN"] = bot_token
            print(f"  → BOT_TOKEN: {bot_token[:20]}...")
        
        print(f"  → Starting Client {n}...")
        
        try:
            process = subprocess.Popen(
                [sys.executable, "-m", "pyUltroid", out[0], out[1], out[2], "", "", n],
                stdin=None,
                stderr=None,
                stdout=None,
                cwd=None,
                env=env,
            )
            started_clients.append((n, process.pid))
            print(f"  → Client {n} started (PID: {process.pid})")
            print()
        except Exception as e:
            print(f"  ✗ Error starting Client {n}: {e}")
            print()
    else:
        missing_vars = [var for var in vars if not os.environ.get(var + suffix)]
        if missing_vars:
            print(f"✗ Client {n}: Skipped (missing: {', '.join(missing_vars)})")

print("=" * 50)
if started_clients:
    print(f"✓ Successfully started {len(started_clients)} client(s):")
    for client_num, pid in started_clients:
        print(f"  - Client {client_num} (PID: {pid})")
    print()
    print("All clients are running in the background.")
    print("Press Ctrl+C to stop the launcher (clients will continue running).")
    print("=" * 50)
else:
    print("✗ No clients were started. Please check your environment variables.")
    print("=" * 50)
    sys.exit(1)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

try:
    loop.run_forever()
except KeyboardInterrupt:
    print("\n" + "=" * 50)
    print("Launcher stopped by user (Ctrl+C)")
    print("Note: Client processes are still running in the background.")
    print("To stop clients, you'll need to kill their processes manually.")
    print("=" * 50)
except Exception as er:
    print(f"\n✗ Error: {er}")
finally:
    loop.close()

