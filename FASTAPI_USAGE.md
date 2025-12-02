# FastAPI Integration for Ultroid Bot

## What is FastAPI?
FastAPI is a modern, fast web framework for building APIs with Python. It's perfect for creating REST APIs, webhooks, and web dashboards.

## Potential Use Cases in Ultroid Bot

### 1. **Web Dashboard / Control Panel** 🌐
- **Real-time Bot Statistics**: Monitor uptime, message counts, active users
- **Plugin Management**: Enable/disable plugins via web interface
- **Multi-Client Management**: Control all your bot instances from one dashboard
- **Settings Configuration**: Edit database variables, environment configs
- **Logs Viewer**: View real-time logs in a web interface

**Example Dashboard Features:**
```python
# Dashboard endpoints
GET  /api/stats          # Get bot statistics
GET  /api/plugins        # List all plugins
POST /api/plugins/{name}/toggle  # Enable/disable plugin
GET  /api/clients        # List all multi-client instances
GET  /api/logs           # View recent logs
GET  /api/config         # View current configuration
```

### 2. **REST API for External Integrations** 🔌
- **Third-party Integrations**: Allow external services to interact with your bot
- **Automation**: Trigger bot actions via HTTP requests
- **CI/CD Integration**: Automate deployments and updates
- **Mobile App Backend**: Create a companion mobile app

**Example API Endpoints:**
```python
# Send message via API
POST /api/send
{
    "chat_id": -1001234567890,
    "message": "Hello from API!",
    "client": 1  # Which multi-client to use
}

# Get chat information
GET /api/chat/{chat_id}

# Upload file
POST /api/upload
```

### 3. **Webhook System** 🎣
- **GitHub Webhooks**: Auto-update bot on git push
- **Payment Webhooks**: Handle payment notifications
- **External Service Notifications**: Receive events from other services
- **Custom Triggers**: Create custom webhook endpoints for specific actions

**Example Webhook:**
```python
# GitHub webhook for auto-update
POST /webhooks/github
{
    "ref": "refs/heads/main",
    "commits": [...]
}

# Custom webhook
POST /webhooks/custom/{token}
{
    "action": "restart",
    "client": 1
}
```

### 4. **Real-time Monitoring & Analytics** 📊
- **System Metrics**: CPU, memory, disk usage
- **Bot Performance**: Response times, command execution stats
- **User Analytics**: Active users, message frequency
- **Error Tracking**: Track and display errors in real-time

**Example Metrics:**
```python
GET /api/metrics/system   # System resources
GET /api/metrics/bot      # Bot performance
GET /api/metrics/users    # User statistics
GET /api/metrics/errors   # Error logs
```

### 5. **File Upload/Download API** 📁
- **Direct File Access**: Upload/download files via HTTP
- **Share Files**: Generate shareable links for files
- **Media Management**: Manage bot's media library
- **Cloud Integration**: Interface with cloud storage

### 6. **Authentication & API Keys** 🔐
- **Secure Access**: Protect API endpoints with authentication
- **Multi-user Access**: Different API keys for different users
- **Rate Limiting**: Prevent abuse with rate limits
- **Access Logs**: Track API usage

### 7. **WebSocket Support** 🔄
- **Real-time Updates**: Push updates to connected clients
- **Live Logs**: Stream logs in real-time
- **Command Execution**: Execute commands via WebSocket
- **Status Updates**: Real-time bot status updates

## Implementation Example

### Basic FastAPI Server Setup

```python
# plugins/webapi.py
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from typing import Optional
import asyncio

app = FastAPI(title="Ultroid API", version="1.0.0")

# CORS middleware for web dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Key authentication
API_KEY = "your-secret-api-key"  # Store in database

def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return x_api_key

@app.get("/")
async def root():
    return {"message": "Ultroid API", "status": "running"}

@app.get("/api/stats")
async def get_stats(api_key: str = Depends(verify_api_key)):
    """Get bot statistics"""
    from pyUltroid import ultroid_bot
    from pyUltroid import start_time
    import time
    
    stats = {
        "uptime": time.time() - start_time,
        "user_id": ultroid_bot.uid,
        "username": ultroid_bot.me.username,
        "name": ultroid_bot.me.first_name,
        "is_bot": ultroid_bot.me.bot,
    }
    return stats

@app.get("/api/plugins")
async def get_plugins(api_key: str = Depends(verify_api_key)):
    """List all loaded plugins"""
    from pyUltroid.loader import PLUGINS
    
    plugins = {
        "total": len(PLUGINS),
        "plugins": list(PLUGINS.keys())
    }
    return plugins

@app.post("/api/send")
async def send_message(
    chat_id: int,
    message: str,
    client: int = 1,
    api_key: str = Depends(verify_api_key)
):
    """Send message via API"""
    from pyUltroid import ultroid_bot
    
    try:
        await ultroid_bot.send_message(chat_id, message)
        return {"status": "success", "message": "Message sent"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Start server function
def start_web_server(host="0.0.0.0", port=8000):
    """Start FastAPI server in background"""
    config = uvicorn.Config(
        app,
        host=host,
        port=port,
        log_level="info"
    )
    server = uvicorn.Server(config)
    asyncio.create_task(server.serve())
```

### Integration with Ultroid

```python
# In pyUltroid/startup/funcs.py or a plugin
def start_web_api():
    """Start FastAPI server"""
    from plugins.webapi import start_web_server
    start_web_server(host="0.0.0.0", port=8000)
    LOGS.info("Web API server started on http://0.0.0.0:8000")
```

## Advantages for Multi-Client Setup

1. **Centralized Management**: Control all clients from one dashboard
2. **Monitoring**: Monitor all instances simultaneously
3. **Load Balancing**: Distribute requests across clients
4. **Analytics**: Aggregate statistics from all clients

## Security Considerations

1. **API Authentication**: Always use API keys or tokens
2. **HTTPS**: Use HTTPS in production
3. **Rate Limiting**: Prevent abuse
4. **Input Validation**: Validate all inputs
5. **CORS**: Configure CORS properly
6. **Access Control**: Implement proper authorization

## Requirements

Add to `requirements.txt`:
```
fastapi
uvicorn[standard]
pydantic
python-multipart
```

## Example Dashboard HTML

```html
<!-- Simple dashboard example -->
<!DOCTYPE html>
<html>
<head>
    <title>Ultroid Dashboard</title>
</head>
<body>
    <h1>Ultroid Bot Dashboard</h1>
    <div id="stats"></div>
    <button onclick="loadStats()">Refresh Stats</button>
    
    <script>
        async function loadStats() {
            const response = await fetch('/api/stats', {
                headers: {'X-API-Key': 'your-api-key'}
            });
            const stats = await response.json();
            document.getElementById('stats').innerHTML = 
                `Uptime: ${stats.uptime}s<br>User: ${stats.username}`;
        }
        loadStats();
        setInterval(loadStats, 5000); // Refresh every 5 seconds
    </script>
</body>
</html>
```

## Recommended Ports

- **Development**: `8000` (default FastAPI)
- **Production**: Use reverse proxy (nginx) on port `80/443`
- **Multi-instance**: Use different ports for each client

## Next Steps

1. Install FastAPI: `pip install fastapi uvicorn`
2. Create web API plugin
3. Add authentication
4. Create dashboard interface
5. Deploy with reverse proxy (nginx)

## Use Cases Summary

| Feature | Use Case | Benefit |
|---------|----------|---------|
| Dashboard | Monitor & Control | Better visibility |
| REST API | External Integration | Automation |
| Webhooks | Event Handling | Real-time updates |
| Analytics | Performance Tracking | Optimization |
| File API | Media Management | Easy access |
| WebSocket | Real-time Updates | Live monitoring |

---

**Note**: FastAPI is optional and not required for basic bot functionality. It's useful if you need web interfaces, external integrations, or advanced monitoring.

