# Ultroid - UserBot
# Copyright (C) 2021-2025 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}webapi start`
    Start FastAPI web server for bot control.

• `{i}webapi stop`
    Stop the web server.

• `{i}webapi status`
    Check web server status.

• `{i}webapi autostart on/off`
    Enable/disable auto-start on bot startup (enabled by default).

Setup:
1. Install FastAPI: pip install fastapi uvicorn python-multipart
2. Set WEB_API_PORT in .env (default: 8000)
3. Set WEB_API_KEY in .env for authentication (optional)
4. Web API starts automatically on bot startup (use .webapi autostart off to disable)
"""

from . import LOGS, eor, get_string, udB, ultroid_cmd
import os
import asyncio
import time
from threading import Thread
from typing import Optional, List, Dict
import json

# Global server reference
_web_server = None
_server_thread = None
_server_port = None


def start_web_api(port=8000, api_key=None):
    """Start FastAPI web server"""
    global _web_server, _server_port
    
    try:
        from fastapi import FastAPI, HTTPException, Depends, Header, Request
        from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
        from fastapi.middleware.cors import CORSMiddleware
        from fastapi.staticfiles import StaticFiles
        import uvicorn
    except ImportError:
        return False, "FastAPI not installed. Run: pip install fastapi uvicorn python-multipart"

    if _web_server:
        return False, "Web API server is already running!"

    app = FastAPI(
        title="Ultroid Bot API",
        description="REST API & Dashboard for Ultroid Bot",
        version="2.0.0"
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Authentication function (optional - only required if API key is configured)
    def verify_api_key(x_api_key: Optional[str] = Header(None)):
        # Only require API key if it's configured
        if api_key:
            if not x_api_key or x_api_key != api_key:
                raise HTTPException(status_code=401, detail="Invalid or missing API Key")
        # If no API key is configured, allow access without authentication
        return x_api_key

    @app.get("/")
    async def root():
        """Serve dashboard"""
        return HTMLResponse(content=get_dashboard_html())

    @app.get("/api/stats")
    async def get_stats(api_key: str = Depends(verify_api_key), client_id: int = None):
        """Get bot statistics - shows stats for specified or current client instance"""
        try:
            from pyUltroid import ultroid_bot, start_time
            import psutil
            import os

            # If client_id is specified, we need to get stats from that client
            # For now, we can only get stats from the current client instance
            # In the future, we could implement inter-process communication
            
            # Detect which client instance this webapi is running in
            current_client_id = client_id
            cwd = os.getcwd()
            if current_client_id is None:
                if 'client_' in cwd:
                    try:
                        current_client_id = int(cwd.split('client_')[-1].split(os.sep)[0])
                    except:
                        pass
            
            # If not in client directory, try to detect from PID
            if current_client_id is None:
                base_dir = os.path.dirname(cwd) if 'client_' in cwd else cwd
                current_pid = os.getpid()
                try:
                    import psutil
                    current_proc = psutil.Process(current_pid)
                    parent_pid = current_proc.ppid()
                except:
                    parent_pid = None
                
                for i in range(1, 6):
                    pid_file = os.path.join(base_dir, f"client_{i}.pid")
                    if os.path.exists(pid_file):
                        try:
                            with open(pid_file, 'r') as f:
                                pid = int(f.read().strip())
                            # Check if current process or parent matches
                            if current_pid == pid or (parent_pid and parent_pid == pid):
                                current_client_id = i
                                break
                            # Also check if we're a child of this process
                            if parent_pid:
                                try:
                                    parent_proc = psutil.Process(parent_pid)
                                    if parent_proc.pid == pid:
                                        current_client_id = i
                                        break
                                except:
                                    pass
                        except:
                            pass

            uptime_seconds = int(time.time() - start_time)
            uptime_formatted = format_uptime(uptime_seconds)

            # Get system stats (optional - psutil may not be installed)
            system_stats = None
            try:
                import psutil
                process = psutil.Process(os.getpid())
                memory_info = process.memory_info()
                cpu_percent = process.cpu_percent(interval=0.1)
                system_stats = {
                    "cpu_percent": round(cpu_percent, 2),
                    "memory_mb": round(memory_info.rss / 1024 / 1024, 2),
                    "memory_percent": round(process.memory_percent(), 2),
                }
            except ImportError:
                pass  # psutil not installed, skip system stats

            # Get bot info
            bot_info = {}
            try:
                if ultroid_bot and ultroid_bot.me:
                    bot_info = {
                        "user_id": ultroid_bot.uid if hasattr(ultroid_bot, 'uid') else None,
                        "username": ultroid_bot.me.username if hasattr(ultroid_bot.me, 'username') else None,
                        "first_name": ultroid_bot.me.first_name if hasattr(ultroid_bot.me, 'first_name') else None,
                        "is_bot": ultroid_bot.me.bot if hasattr(ultroid_bot.me, 'bot') else None,
                    }
            except:
                pass

            stats = {
                "status": "online",
                "client_id": current_client_id,
                "uptime_seconds": uptime_seconds,
                "uptime_formatted": uptime_formatted,
                "user_id": bot_info.get("user_id"),
                "username": bot_info.get("username"),
                "first_name": bot_info.get("first_name"),
                "is_bot": bot_info.get("is_bot"),
                "system": system_stats
            }
            return stats
        except Exception as e:
            LOGS.exception(e)
            return {"status": "error", "error": str(e)}

    @app.get("/api/plugins")
    async def get_plugins(api_key: str = Depends(verify_api_key)):
        """List all loaded plugins"""
        try:
            from pyUltroid.dB._core import LOADED, HELP
            
            # Get plugin names from LOADED dict (keys are plugin names)
            # Also include plugins from HELP dict which contains all loaded plugins
            loaded_plugins = set(LOADED.keys()) if LOADED else set()
            
            # Also get from HELP dict which has plugin names organized by category
            for category_plugins in HELP.values():
                if isinstance(category_plugins, dict):
                    loaded_plugins.update(category_plugins.keys())
            
            # Fallback: list plugin files from plugins directory
            if not loaded_plugins:
                import os
                plugins_dir = os.path.join(os.getcwd(), "plugins")
                if os.path.exists(plugins_dir):
                    plugin_files = [
                        f.replace(".py", "") 
                        for f in os.listdir(plugins_dir) 
                        if f.endswith(".py") and not f.startswith("__")
                    ]
                    loaded_plugins = set(plugin_files)
            
            plugins = {
                "total": len(loaded_plugins),
                "plugins": sorted(list(loaded_plugins))
            }
            return plugins
        except Exception as e:
            LOGS.exception(e)
            return {"total": 0, "plugins": [], "error": str(e)}

    @app.get("/api/clients")
    async def get_clients(api_key: str = Depends(verify_api_key)):
        """Get multi-client instances status"""
        try:
            import psutil
            import os

            clients = []
            # Get base directory (parent of client_N directories)
            cwd = os.getcwd()
            if 'client_' in cwd:
                # We're in a client directory, go up to parent
                base_dir = os.path.dirname(cwd)
            else:
                base_dir = cwd
            
            # Try to import psutil for process checking
            try:
                import psutil
                has_psutil = True
            except ImportError:
                has_psutil = False

            # First, find all running pyUltroid processes and map them to clients
            running_processes = {}
            if has_psutil:
                for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cwd', 'cpu_percent', 'memory_info']):
                    try:
                        cmdline = proc.info.get('cmdline', [])
                        if cmdline and any('pyUltroid' in str(arg) for arg in cmdline):
                            proc_cwd = proc.info.get('cwd', '')
                            pid = proc.info['pid']
                            
                            # Try to determine which client this is
                            client_id = None
                            
                            # Method 1: Check if cwd is in a client_N directory
                            if 'client_' in proc_cwd:
                                try:
                                    # Extract client number from path like /path/to/client_1 or /path/to/client_2/
                                    parts = proc_cwd.split('client_')
                                    if len(parts) > 1:
                                        client_num_str = parts[-1].split(os.sep)[0].split('/')[0]
                                        client_id = int(client_num_str)
                                except:
                                    pass
                            
                            # Method 2: Check PID files (PID files are in base directory, not client directories)
                            if client_id is None:
                                # PID files are stored in the base directory (parent of client_N)
                                # Get base directory from current process or from proc_cwd
                                proc_base_dir = base_dir  # Use the base_dir we calculated above
                                for i in range(1, 6):
                                    pid_file = os.path.join(proc_base_dir, f"client_{i}.pid")
                                    if os.path.exists(pid_file):
                                        try:
                                            with open(pid_file, 'r') as f:
                                                if int(f.read().strip()) == pid:
                                                    client_id = i
                                                    break
                                        except:
                                            pass
                            
                            # Method 3: If we can't determine, assign to first available
                            if client_id is None:
                                for i in range(1, 6):
                                    if i not in running_processes:
                                        client_id = i
                                        break
                            
                            if client_id:
                                try:
                                    proc_obj = psutil.Process(pid)
                                    running_processes[client_id] = {
                                        'pid': pid,
                                        'cpu': proc_obj.cpu_percent(interval=0.1),
                                        'mem': proc_obj.memory_info().rss / 1024 / 1024
                                    }
                                except:
                                    pass
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue

            # Check which clients have environment variables configured
            # Only show clients that have API_ID, API_HASH, SESSION, MONGO_URI
            configured_clients = set()
            try:
                from dotenv import load_dotenv
                # Try to load .env from base directory
                env_file = os.path.join(base_dir, ".env")
                if os.path.exists(env_file):
                    # Load .env file to check for all client configurations
                    # We need to load it to check for API_ID, API_ID1, API_ID2, etc.
                    load_dotenv(env_file)
                
                required_vars = ["API_ID", "API_HASH", "SESSION", "MONGO_URI"]
                for i in range(1, 6):
                    suffix = "" if i == 1 else str(i - 1)
                    has_all = True
                    for var in required_vars:
                        var_name = var + suffix
                        # Check numbered variable first, then fallback to base variable
                        value = os.environ.get(var_name)
                        if not value and suffix:
                            # For clients 2-5, also check base variable as fallback
                            value = os.environ.get(var)
                        if not value:
                            has_all = False
                            break
                    if has_all:
                        configured_clients.add(i)
            except Exception as e:
                # If we can't check, show all running clients
                LOGS.debug(f"Could not check client configuration: {e}")

            # Show clients that are running OR have configuration
            for i in range(1, 6):
                client_dir = os.path.join(base_dir, f"client_{i}")
                pid_file = os.path.join(base_dir, f"client_{i}.pid")
                has_directory = os.path.exists(client_dir)
                
                # Check if we found this client in running processes
                is_running = False
                pid = None
                cpu = 0
                mem = 0
                
                if i in running_processes:
                    # Found via process scanning
                    is_running = True
                    pid = running_processes[i]['pid']
                    cpu = running_processes[i]['cpu']
                    mem = running_processes[i]['mem']
                elif os.path.exists(pid_file):
                    # Fallback: check PID file
                    try:
                        with open(pid_file, 'r') as f:
                            pid = int(f.read().strip())
                        if has_psutil:
                            if psutil.pid_exists(pid):
                                proc = psutil.Process(pid)
                                is_running = True
                                cpu = proc.cpu_percent(interval=0.1)
                                mem = proc.memory_info().rss / 1024 / 1024
                        else:
                            # Without psutil, just check if file exists
                            is_running = True
                    except Exception:
                        pass

                # Show clients that are running OR have configuration
                # Don't show clients that are stopped AND don't have configuration
                if not is_running:
                    # If not running, only show if it has configuration
                    if configured_clients and i not in configured_clients:
                        continue  # Skip stopped clients without configuration
                # If running, always show (even if config check failed)
                
                clients.append({
                    "id": i,
                    "status": "running" if is_running else "stopped",
                    "pid": pid,
                    "cpu_percent": round(cpu, 2) if is_running else 0,
                    "memory_mb": round(mem, 2) if is_running else 0,
                    "has_directory": has_directory,
                })

            return {"clients": clients, "total": len(clients)}
        except Exception as e:
            LOGS.exception(e)
            return {"clients": [], "total": 0, "error": str(e)}

    @app.get("/api/logs")
    async def get_logs(api_key: str = Depends(verify_api_key), lines: int = 50):
        """Get recent logs"""
        try:
            logs = []
            # Try to get logs from LOGS handler if available
            return {"logs": logs, "total": len(logs)}
        except Exception as e:
            LOGS.exception(e)
            return {"logs": [], "total": 0, "error": str(e)}

    @app.post("/api/send")
    async def send_message(
        request: Request,
        api_key: str = Depends(verify_api_key)
    ):
        """Send message via API"""
        try:
            data = await request.json()
            chat_id = data.get("chat_id")
            message = data.get("message")
            client = data.get("client", 1)

            if not chat_id or not message:
                raise HTTPException(status_code=400, detail="chat_id and message required")

            from pyUltroid import ultroid_bot
            await ultroid_bot.send_message(chat_id, message)
            return {"status": "success", "message": "Message sent"}
        except Exception as e:
            LOGS.exception(e)
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {"status": "healthy", "timestamp": time.time()}

    # Start server in background thread
    def run_server():
        config = uvicorn.Config(
            app,
            host="0.0.0.0",
            port=port,
            log_level="info",
            access_log=False
        )
        server = uvicorn.Server(config)
        asyncio.run(server.serve())

    global _server_thread
    _server_thread = Thread(target=run_server, daemon=True)
    _server_thread.start()

    _web_server = app
    _server_port = port
    return True, f"Web API server started on http://0.0.0.0:{port}"


def format_uptime(seconds):
    """Format uptime in human readable format"""
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if days > 0:
        return f"{days}d {hours}h {minutes}m {secs}s"
    elif hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"


def get_dashboard_html():
    """Get dashboard HTML content"""
    # Read dashboard HTML from separate file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    dashboard_file = os.path.join(current_dir, "webapi_dashboard.html")
    
    if os.path.exists(dashboard_file):
        try:
            with open(dashboard_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            LOGS.exception(f"Error reading dashboard file: {e}")
    
    # Fallback HTML
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Ultroid Dashboard</title>
        <style>
            body { background: #0a0a0a; color: #fff; font-family: sans-serif; padding: 20px; }
            h1 { color: #00d9ff; }
            .error { color: #ff4444; }
        </style>
    </head>
    <body>
        <h1>Ultroid Dashboard</h1>
        <p class="error">Dashboard HTML file not found. Please check webapi_dashboard.html exists in plugins directory.</p>
    </body>
    </html>
    """


@ultroid_cmd(pattern="webapi start$", fullsudo=True)
async def webapi_start(event):
    """Start FastAPI web server"""
    port = int(udB.get_key("WEB_API_PORT") or os.getenv("WEB_API_PORT", "8000"))
    api_key = udB.get_key("WEB_API_KEY") or os.getenv("WEB_API_KEY")

    success, message = start_web_api(port=port, api_key=api_key)
    if success:
        await eor(
            event,
            f"✓ {message}\n"
            f"📖 **Dashboard:** http://localhost:{port}\n"
            f"📚 **API Docs:** http://localhost:{port}/docs\n"
            f"🔐 **API Key:** {'✓ Set' if api_key else '✗ Not set (optional)'}"
        )
        udB.set_key("WEB_API_RUNNING", True)
        udB.set_key("WEB_API_PORT", port)
    else:
        await eor(event, f"✗ {message}")


@ultroid_cmd(pattern="webapi stop$", fullsudo=True)
async def webapi_stop(event):
    """Stop FastAPI web server"""
    global _web_server, _server_thread, _server_port

    if not _web_server:
        return await eor(event, "Web API server is not running!")

    # Note: This is a simple implementation
    _web_server = None
    _server_thread = None
    _server_port = None
    udB.set_key("WEB_API_RUNNING", False)
    await eor(event, "✓ Web API server stopped (restart bot to fully stop)")


@ultroid_cmd(pattern="webapi status$")
async def webapi_status(event):
    """Check web API server status"""
    port = int(udB.get_key("WEB_API_PORT") or os.getenv("WEB_API_PORT", "8000"))
    api_key = udB.get_key("WEB_API_KEY") or os.getenv("WEB_API_KEY")

    status = "running" if _web_server else "stopped"
    
    auto_start_setting = udB.get_key("WEB_API_AUTO_START")
    if auto_start_setting is False:
        auto_start_status = "✗ Disabled"
    else:
        auto_start_status = "✓ Enabled (default)"
    
    msg = (
        f"**Web API Status:** {status}\n"
        f"**Port:** {port}\n"
        f"**API Key:** {'✓ Set' if api_key else '✗ Not set'}\n"
        f"**Auto-Start:** {auto_start_status}\n"
    )
    
    if _web_server:
        msg += f"📖 **Dashboard:** http://localhost:{port}\n"
        msg += f"📚 **API Docs:** http://localhost:{port}/docs\n"
        msg += f"🔗 **Health:** http://localhost:{port}/health"

    await eor(event, msg)


@ultroid_cmd(pattern="webapi autostart (on|off)$", fullsudo=True)
async def webapi_autostart(event):
    """Enable/disable auto-start of web API"""
    mode = event.pattern_match.group(1)
    
    if mode == "on":
        udB.set_key("WEB_API_AUTO_START", True)
        await eor(event, "✓ Web API auto-start enabled. It will start automatically on bot startup.")
    else:
        udB.set_key("WEB_API_AUTO_START", False)
        await eor(event, "✗ Web API auto-start disabled. Use `.webapi start` to start manually.")


# Auto-start web API by default (unless explicitly disabled)
def _auto_start_webapi():
    """Auto-start web API on plugin load by default"""
    try:
        # Check if auto-start is explicitly disabled
        auto_start_setting = udB.get_key("WEB_API_AUTO_START")
        if auto_start_setting is False:
            LOGS.info("Web API auto-start is disabled")
            return
        
        # Don't start if already running
        if _web_server:
            return
        
        # Get configuration
        port = int(udB.get_key("WEB_API_PORT") or os.getenv("WEB_API_PORT", "8000"))
        api_key = udB.get_key("WEB_API_KEY") or os.getenv("WEB_API_KEY")
        
        # Start the server (starts by default)
        success, message = start_web_api(port=port, api_key=api_key)
        if success:
            LOGS.info(f"Web API auto-started: {message}")
        else:
            LOGS.warning(f"Web API auto-start failed: {message}")
    except Exception as e:
        LOGS.exception(f"Error in webapi auto-start: {e}")


# Start web API automatically when plugin loads (if enabled)
# Use a small delay to ensure bot is fully initialized
def _delayed_auto_start():
    """Start web API after a short delay"""
    time.sleep(5)  # Wait 5 seconds for bot to fully initialize
    _auto_start_webapi()

# Start auto-start thread
try:
    auto_start_thread = Thread(target=_delayed_auto_start, daemon=True, name="webapi-autostart")
    auto_start_thread.start()
except Exception as e:
    LOGS.exception(f"Failed to start webapi auto-start thread: {e}")

