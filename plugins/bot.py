# --- Auto-update monitor (fully fixed, stable) ---

import os
import sys
import time
import threading
import subprocess

# Import LOGS and call_back from Ultroid
from . import LOGS, call_back


# Enable / disable and interval via env:
AUTO_UPDATE_ENABLED = os.getenv("AUTO_UPDATE_ENABLED", "true").lower() not in ("0", "false", "no")
AUTO_UPDATE_INTERVAL = int(os.getenv("AUTO_UPDATE_INTERVAL", "300"))  # seconds


def _monitor_updates_loop():
    """Background thread that auto-pulls repo + restarts when upstream changes."""
    if not AUTO_UPDATE_ENABLED:
        LOGS.info("Auto-update monitor disabled.")
        return

    LOGS.info("Auto-update monitor started (interval %ss)", AUTO_UPDATE_INTERVAL)
    repo_path = os.getcwd()

    while True:
        try:
            if not os.path.isdir(os.path.join(repo_path, ".git")):
                LOGS.warning("Auto-update: Not a git repository: %s", repo_path)
                return

            # fetch updates
            try:
                subprocess.run(
                    ["git", "fetch", "--all"],
                    cwd=repo_path,
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            except subprocess.CalledProcessError:
                LOGS.warning("Auto-update: git fetch failed; retrying...")
                time.sleep(AUTO_UPDATE_INTERVAL)
                continue

            # get local commit
            try:
                local = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo_path).strip()
            except subprocess.CalledProcessError:
                LOGS.exception("Auto-update: Could not get local HEAD.")
                time.sleep(AUTO_UPDATE_INTERVAL)
                continue

            # get upstream commit
            try:
                upstream = subprocess.check_output(["git", "rev-parse", "@{u}"], cwd=repo_path).strip()
            except subprocess.CalledProcessError:
                try:
                    upstream = subprocess.check_output(
                        ["git", "rev-parse", "origin/HEAD"], cwd=repo_path
                    ).strip()
                except subprocess.CalledProcessError:
                    LOGS.warning("Auto-update: No upstream available.")
                    time.sleep(AUTO_UPDATE_INTERVAL)
                    continue

            # compare
            if local != upstream:
                LOGS.info("Auto-update: Update detected → pulling updates.")
                try:
                    subprocess.run(["git", "pull", "--no-edit"], cwd=repo_path, check=True)
                except subprocess.CalledProcessError:
                    LOGS.exception("Auto-update: git pull failed.")
                    time.sleep(AUTO_UPDATE_INTERVAL)
                    continue

                # install any new requirements
                try:
                    subprocess.run(
                        [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                        cwd=repo_path,
                        check=False
                    )
                except Exception:
                    LOGS.exception("Auto-update: pip install error")

                # call Ultroid callback
                try:
                    call_back()
                except Exception:
                    LOGS.exception("Auto-update: call_back() failed")

                # restart bot
                LOGS.info("Auto-update: Restarting Ultroid process...")
                try:
                    os.execl(sys.executable, sys.executable, "-m", "pyUltroid")
                except Exception:
                    LOGS.exception("Auto-update: execl restart failed → exiting.")
                    sys.exit(0)
            else:
                LOGS.debug("Auto-update: No new updates.")

        except Exception:
            LOGS.exception("Auto-update: Unexpected error.")

        time.sleep(AUTO_UPDATE_INTERVAL)


# start thread
try:
    t = threading.Thread(
        target=_monitor_updates_loop,
        name="auto-update-monitor",
        daemon=True,
    )
    t.start()
except Exception:
    LOGS.exception("Auto-update monitor failed to start.")

# --- end auto-update monitor ---
