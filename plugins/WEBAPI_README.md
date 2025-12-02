# Ultroid Web API & Dashboard

A beautiful black-themed web dashboard and REST API for your Ultroid bot with multi-client support.

## Features

✨ **Beautiful Black-Themed Dashboard**
- Modern, dark UI with gradient effects
- Real-time statistics and monitoring
- Multi-client instance management
- System resource monitoring
- Plugin listing and management

🚀 **REST API**
- Bot statistics endpoint
- Plugin information
- Multi-client status
- Send messages via API
- Health check endpoint

## Installation

1. **Install Required Packages:**
```bash
pip install fastapi uvicorn[standard] python-multipart
```

2. **Optional (for system stats):**
```bash
pip install psutil
```

3. **Configure (Optional):**
Add to your `.env` file:
```env
WEB_API_PORT=8000           # Port for web server (default: 8000)
WEB_API_KEY=your-secret-key  # API key for authentication (optional)
```

### Generating WEB_API_KEY

The `WEB_API_KEY` is a **secret key you generate yourself** for securing API endpoints.

#### Easy Method (Recommended):
Run this helper script:
```bash
python plugins/webapi_setup.py
```

This will generate a secure random key and show you exactly what to add to your `.env` file.

#### Alternative Methods:

**Method 1: Python one-liner**
```bash
python -c "import secrets; print('WEB_API_KEY=' + secrets.token_urlsafe(32))"
```

**Method 2: Using OpenSSL**
```bash
openssl rand -hex 32
```

**Method 3: Manual**
Create a long random string (at least 32 characters) using any random string generator.

#### After Generating:
Copy the generated key and add it to your `.env` file:
```env
WEB_API_KEY=paste-your-generated-key-here
```

**Note:** The API key is **optional** - if not set, the API works without authentication (less secure for production). For production use, always set an API key!

## Usage

### Start Web Server
```
.webapi start
```

This will start the web server on port 8000 (or your configured port).

### Access Dashboard
Open your browser and go to:
- **Dashboard:** `http://localhost:8000`
- **API Docs:** `http://localhost:8000/docs`
- **Health Check:** `http://localhost:8000/health`

### Stop Web Server
```
.webapi stop
```

### Check Status
```
.webapi status
```

## API Endpoints

### Dashboard
- `GET /` - Web dashboard interface

### Statistics
- `GET /api/stats` - Get bot statistics
  - Requires: API Key (if configured)
  - Returns: Uptime, user info, system stats

### Plugins
- `GET /api/plugins` - List all loaded plugins
  - Requires: API Key (if configured)
  - Returns: List of plugin names

### Multi-Client
- `GET /api/clients` - Get multi-client instances status
  - Requires: API Key (if configured)
  - Returns: Status of all client instances

### Messaging
- `POST /api/send` - Send message via API
  - Requires: API Key (if configured)
  - Body: `{"chat_id": -1001234567890, "message": "Hello!"}`
  - Returns: Success status

### Health
- `GET /health` - Health check (no auth required)
  - Returns: Server status

## API Usage Example

### Using curl:
```bash
# Get stats (with API key)
curl -H "X-API-Key: your-secret-key" http://localhost:8000/api/stats

# Get stats (no API key if not configured)
curl http://localhost:8000/api/stats

# Send message
curl -X POST \
  -H "X-API-Key: your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{"chat_id": -1001234567890, "message": "Hello from API!"}' \
  http://localhost:8000/api/send
```

### Using Python:
```python
import requests

API_BASE = "http://localhost:8000"
API_KEY = "your-secret-key"  # Optional

headers = {}
if API_KEY:
    headers["X-API-Key"] = API_KEY

# Get stats
response = requests.get(f"{API_BASE}/api/stats", headers=headers)
stats = response.json()
print(f"Bot uptime: {stats['uptime_formatted']}")

# Send message
data = {
    "chat_id": -1001234567890,
    "message": "Hello from Python!"
}
response = requests.post(f"{API_BASE}/api/send", json=data, headers=headers)
print(response.json())
```

## Dashboard Features

### Real-time Updates
- Auto-refreshes every 5 seconds
- Shows last update time
- Pauses when tab is hidden (saves resources)

### Bot Statistics
- Online/Offline status
- Uptime (formatted)
- User ID and username
- Bot type

### System Resources
- CPU usage with progress bar
- Memory usage with progress bar
- Real-time monitoring

### Multi-Client Management
- View all client instances
- Check running status
- Monitor CPU and memory per client
- View process IDs

### Plugin List
- Total plugin count
- Scrollable plugin list
- Refresh button

## Security Notes

1. **API Key**: Set `WEB_API_KEY` in `.env` to enable API authentication
2. **Port Binding**: By default, server binds to `0.0.0.0` (all interfaces)
3. **CORS**: Currently allows all origins (configure for production)
4. **HTTPS**: Use a reverse proxy (nginx) with SSL in production

## Production Deployment

For production use:

1. **Use Reverse Proxy (nginx):**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

2. **Set API Key:**
```env
WEB_API_KEY=your-very-secure-api-key-here
```

3. **Configure CORS:**
Edit the plugin to restrict CORS origins

## Troubleshooting

### "FastAPI not installed" error
```bash
pip install fastapi uvicorn python-multipart
```

### Dashboard shows errors
- Check if `webapi_dashboard.html` exists in `plugins/` directory
- Check browser console for JavaScript errors

### System stats not showing
- Install psutil: `pip install psutil`
- System stats are optional - dashboard works without it

### Port already in use
- Change port in `.env`: `WEB_API_PORT=8001`
- Or stop the service using port 8000

## Files

- `plugins/webapi.py` - Main plugin file
- `plugins/webapi_dashboard.html` - Dashboard HTML/CSS/JS
- `plugins/WEBAPI_README.md` - This file

## Support

For issues or questions, check the main Ultroid documentation or support channels.

