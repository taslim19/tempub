# How to Set WebAPI Port to 8090

## Method 1: Using .env File (Recommended)

1. **Open or create `.env` file** in your project root:
```bash
nano .env
```

2. **Add this line:**
```env
WEB_API_PORT=8090
```

3. **Or if the file already exists, find the line** and change it:
```env
WEB_API_PORT=8090  # Change from 8000 to 8090
```

4. **Save the file** and restart the web API:
```
.webapi stop
.webapi start
```

## Method 2: Using Database Command

You can also set it directly in the bot using a command:

```
.setdb WEB_API_PORT 8090
```

Then restart the web API:
```
.webapi stop
.webapi start
```

## Verify Port is Set

Check the status:
```
.webapi status
```

It should show:
```
Port: 8090
Dashboard: http://localhost:8090
```

## Complete Example

```bash
# Edit .env file
echo "WEB_API_PORT=8090" >> .env

# Or edit existing line
# Change WEB_API_PORT=8000 to WEB_API_PORT=8090

# Start web API (it will use port 8090)
.webapi start
```

The dashboard will now be available at:
- **Dashboard:** http://localhost:8090
- **API Docs:** http://localhost:8090/docs

