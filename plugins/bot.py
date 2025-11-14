# --- Auto-update monitor (place after imports) ---
import threading
import subprocess

# Enable / disable and interval via env:
AUTO_UPDATE_ENABLED = os.getenv("AUTO_UPDATE_ENABLED", "true").lower() not in ("0", "false", "no")
AUTO_UPDATE_INTERVAL = int(os.getenv("AUTO_UPDATE_INTERVAL", "300"))

def _monitor_updates_loop():
    if not AUTO_UPDATE_ENABLED:
        LOGS.info("Auto-update monitor disabled.")
        return

    LOGS.info("Auto-update monitor started (interval %ss)", AUTO_UPDATE_INTERVAL)
    repo_path = os.getcwd()

    while True:
        try:
            if not os.path.isdir(os.path.join(repo_path, ".git")):
                LOGS.warning("Auto-update monitor: not a git repository at %s", repo_path)
                return

            try:
                subprocess.run(["git", "fetch", "--all"], cwd=repo_path, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except subprocess.CalledProcessError:
                LOGS.warning("Auto-update monitor: 'git fetch' failed; retrying later.")
                time.sleep(AUTO_UPDATE_INTERVAL)
                continue

            try:
                local = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo_path).strip()
            except subprocess.CalledProcessError:
                LOGS.exception("Auto-update monitor: failed to get local HEAD.")
                time.sleep(AUTO_UPDATE_INTERVAL)
                continue

            try:
                upstream = subprocess.check_output(["git", "rev-parse", "@{u}"], cwd=repo_path).strip()
            except subprocess.CalledProcessError:
                try:
                    upstream = subprocess.check_output(["git", "rev-parse", "origin/HEAD"], cwd=repo_path).strip()
                except subprocess.CalledProcessError:
                    LOGS.warning("Auto-update monitor: no upstream found; will retry later.")
                    time.sleep(AUTO_UPDATE_INTERVAL)
                    continue

            if local != upstream:
                LOGS.info("Auto-update monitor: update detected; pulling changes.")
                try:
                    subprocess.run(["git", "pull", "--no-edit"], cwd=repo_path, check=True)
                except subprocess.CalledProcessError:
                    LOGS.exception("Auto-update monitor: git pull failed.")
                    time.sleep(AUTO_UPDATE_INTERVAL)
                    continue

                try:
                    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], cwd=repo_path, check=False)
                except Exception:
                    LOGS.exception("Auto-update monitor: pip install failed.")

                try:
                    call_back()
                except Exception:
                    LOGS.exception("Auto-update monitor: call_back() failed.")

                LOGS.info("Auto-update monitor: restarting process now.")
                try:
                    os.execl(sys.executable, sys.executable, "-m", "pyUltroid")
                except Exception:
                    LOGS.exception("Auto-update monitor: restart failed; exiting.")
                    try:
                        sys.exit(0)
                    except SystemExit:
                        return
            else:
                LOGS.debug("Auto-update monitor: no updates found.")
        except Exception:
            LOGS.exception("Auto-update monitor encountered an unexpected error.")
        time.sleep(AUTO_UPDATE_INTERVAL)

try:
    _t = threading.Thread(target=_monitor_updates_loop, name="auto-update-monitor", daemon=True)
    _t.start()
except Exception:
    LOGS.exception("Failed to start auto-update monitor thread.")
# --- end auto-update monitor ---
