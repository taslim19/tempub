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
        
        # Set unique database name for each client to avoid database locking issues
        # Each client gets its own database: UltroidDB1, UltroidDB2, etc.
        mongo_uri = out[3]
        unique_db_name = f"UltroidDB{n}"
        
        # Parse and modify MongoDB URI to include unique database name
        # Handle different URI formats: mongodb://, mongodb+srv://
        from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
        
        try:
            parsed = urlparse(mongo_uri)
            # Reconstruct with unique database name
            # Path will be like '/dbname' or '/' 
            if parsed.path and parsed.path != '/':
                # Database already in path, replace it
                new_path = f'/{unique_db_name}'
            else:
                # No database in path, add it
                new_path = f'/{unique_db_name}'
            
            # Reconstruct URI
            new_uri = urlunparse((
                parsed.scheme,
                parsed.netloc,
                new_path,
                parsed.params,
                parsed.query,
                parsed.fragment
            ))
            env["MONGO_URI"] = new_uri
        except Exception:
            # Fallback: simple string manipulation if parsing fails
            mongo_uri_temp = mongo_uri.rstrip('/')
            if '?' in mongo_uri_temp:
                base, query = mongo_uri_temp.split('?', 1)
                env["MONGO_URI"] = f"{base}/{unique_db_name}?{query}"
            else:
                env["MONGO_URI"] = f"{mongo_uri_temp}/{unique_db_name}"
        
        print(f"  → Database: {unique_db_name} (unique per client)")
        print(f"  → Working directory: client_{n}/ (isolated session files)")
        
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
        
        # Create unique working directory for each client to avoid SQLite session file conflicts
        # Each client will have its own session files (asst.session, etc.) in its own directory
        base_dir = os.getcwd()
        client_dir = os.path.join(base_dir, f"client_{n}")
        
        # Detect Git branch from parent directory for addons cloning
        git_branch = "main"  # default
        try:
            import subprocess as sp
            result = sp.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], 
                          cwd=base_dir, capture_output=True, text=True)
            if result.returncode == 0:
                git_branch = result.stdout.strip()
        except Exception:
            pass
        
        if not os.path.exists(client_dir):
            os.makedirs(client_dir)
            
            # Copy essential files/directories (or create symlinks on Unix)
            import shutil
            import platform
            
            # Copy .env file
            if os.path.exists(".env"):
                shutil.copy(".env", os.path.join(client_dir, ".env"))
            
            # Create .git symlink or file pointing to parent repository
            # This allows Git operations to work from client subdirectories
            git_link = os.path.join(client_dir, ".git")
            parent_git = os.path.join(base_dir, ".git")
            if os.path.exists(parent_git) and not os.path.exists(git_link):
                if platform.system() != "Windows":
                    try:
                        # Create symlink to parent .git directory
                        os.symlink(os.path.abspath(parent_git), git_link)
                    except (OSError, FileExistsError):
                        # If symlink creation fails, create a gitdir file
                        try:
                            with open(git_link, "w") as f:
                                f.write(f"gitdir: {os.path.abspath(parent_git)}\n")
                        except Exception:
                            pass
                else:
                    # On Windows, create a gitdir file
                    try:
                        with open(git_link, "w") as f:
                            f.write(f"gitdir: {os.path.abspath(parent_git)}\n")
                    except Exception:
                        pass
            
            # For plugins, resources, addons - create symlinks (they should point to parent)
            for dir_name in ["plugins", "resources", "addons"]:
                src = os.path.join(base_dir, dir_name)
                dst = os.path.join(client_dir, dir_name)
                if os.path.exists(src) and not os.path.exists(dst):
                    if platform.system() != "Windows":
                        try:
                            os.symlink(os.path.abspath(src), dst)
                        except OSError:
                            shutil.copytree(src, dst, dirs_exist_ok=True)
                    else:
                        # Copy on Windows
                        if os.path.isdir(src):
                            shutil.copytree(src, dst, dirs_exist_ok=True)
        
        # Set Git environment variables to point to parent repository
        # This ensures Git operations work even from client subdirectories
        git_dir = os.path.join(base_dir, ".git")
        if os.path.exists(git_dir):
            env["GIT_DIR"] = os.path.abspath(git_dir)
            env["GIT_WORK_TREE"] = os.path.abspath(base_dir)
        
        # Set Git branch as environment variable (fallback)
        env["ULTR_REPO_BRANCH"] = git_branch
        
        # Set PYTHONPATH to include the base directory so pyUltroid can be found
        pythonpath = env.get("PYTHONPATH", "")
        if pythonpath:
            env["PYTHONPATH"] = f"{base_dir}{os.pathsep}{pythonpath}"
        else:
            env["PYTHONPATH"] = base_dir
        
        # Create a wrapper script that patches Git Repo detection to use parent directory
        wrapper_script = os.path.join(client_dir, f"_client_{n}_wrapper.py")
        if not os.path.exists(wrapper_script):
            # Escape the base_dir path for use in Python string
            base_dir_escaped = base_dir.replace("\\", "\\\\").replace('"', '\\"')
            wrapper_content = '''#!/usr/bin/env python3
"""Wrapper script to patch Git repository detection for client {n}"""
import os
import sys

# Add parent directory to path first
base_dir = r"{base_dir_escaped}"
sys.path.insert(0, base_dir)

# Patch git.Repo BEFORE any other imports that might use it
try:
    # Import git module early and patch Repo class
    import git
    from git.exc import InvalidGitRepositoryError
    
    OriginalRepo = git.Repo
    
    class PatchedRepo(OriginalRepo):
        """Patched Repo that falls back to parent directory"""
        def __init__(self, path=None, *args, **kwargs):
            if path is None:
                # Try current directory first
                try:
                    super().__init__(path=".", *args, **kwargs)
                    return
                except InvalidGitRepositoryError:
                    # Fall back to parent directory
                    super().__init__(path=base_dir, *args, **kwargs)
            else:
                super().__init__(path=path, *args, **kwargs)
    
    # Replace Repo class in git module
    git.Repo = PatchedRepo
    
except Exception as e:
    # If patching fails, continue anyway
    import warnings
    warnings.warn(f"Could not patch Git Repo: {{e}}")

# Now run pyUltroid (it will use the patched Repo)
if __name__ == "__main__":
    sys.argv = ["pyUltroid", "{out[0]}", "{out[1]}", "{out[2]}", "", "", "{n}"]
    from pyUltroid.__main__ import main
    main()
'''.format(
                n=n,
                base_dir_escaped=base_dir_escaped,
                out0=out[0],
                out1=out[1],
                out2=out[2]
            )
            with open(wrapper_script, "w", encoding="utf-8") as f:
                f.write(wrapper_content)
            # Make executable on Unix
            import platform
            if platform.system() != "Windows":
                os.chmod(wrapper_script, 0o755)
        
        try:
            process = subprocess.Popen(
                [sys.executable, wrapper_script],
                stdin=None,
                stderr=None,
                stdout=None,
                cwd=os.path.abspath(client_dir),  # Run each client in its own directory
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

