import asyncio
import os
import subprocess
import sys

vars = ["API_ID", "API_HASH", "SESSION", "MONGO_URI"]

def _check(z):
    new = []
    for var in vars:
        ent = os.environ.get(var + z)
        if not ent:
            return False, new
        new.append(ent)
    return True, new

for z in range(5):
    n = str(z + 1)
    suffix = "" if z == 0 else str(z)  # Client 1 has no suffix, others use number
    fine, out = _check(suffix)
    if fine:
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
        if bot_token:
            env["BOT_TOKEN"] = bot_token
        
        subprocess.Popen(
            [sys.executable, "-m", "pyUltroid", out[0], out[1], out[2], "", "", n],
            stdin=None,
            stderr=None,
            stdout=None,
            cwd=None,
            env=env,
        )

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

try:
    loop.run_forever()
except Exception as er:
    print(er)
finally:
    loop.close()

