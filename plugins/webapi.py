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
    async def get_stats(api_key: str = Depends(verify_api_key)):
        """Get bot statistics"""
        try:
            from pyUltroid import ultroid_bot, start_time
            import psutil
            import os

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

            stats = {
                "status": "online",
                "uptime_seconds": uptime_seconds,
                "uptime_formatted": uptime_formatted,
                "user_id": ultroid_bot.uid if hasattr(ultroid_bot, 'uid') else None,
                "username": ultroid_bot.me.username if (ultroid_bot.me and hasattr(ultroid_bot.me, 'username')) else None,
                "first_name": ultroid_bot.me.first_name if (ultroid_bot.me and hasattr(ultroid_bot.me, 'first_name')) else None,
                "is_bot": ultroid_bot.me.bot if (ultroid_bot.me and hasattr(ultroid_bot.me, 'bot')) else None,
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
            from pyUltroid.loader import PLUGINS

            plugins = {
                "total": len(PLUGINS),
                "plugins": sorted(list(PLUGINS.keys()))
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
            base_dir = os.getcwd()
            
            # Try to import psutil for process checking
            try:
                import psutil
                has_psutil = True
            except ImportError:
                has_psutil = False

            for i in range(1, 6):
                client_dir = os.path.join(base_dir, f"client_{i}")
                if os.path.exists(client_dir):
                    # Check if process is running
                    pid_file = os.path.join(base_dir, f"client_{i}.pid")
                    is_running = False
                    pid = None
                    cpu = 0
                    mem = 0

                    if os.path.exists(pid_file):
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
                                # This is a basic check - process might not actually be running
                                is_running = True
                        except Exception:
                            pass

                    clients.append({
                        "id": i,
                        "status": "running" if is_running else "stopped",
                        "pid": pid,
                        "cpu_percent": round(cpu, 2) if is_running else 0,
                        "memory_mb": round(mem, 2) if is_running else 0,
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

