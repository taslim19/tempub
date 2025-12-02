# How to Generate and Set WEB_API_KEY

The `WEB_API_KEY` is a **secret key you create yourself** for securing your API endpoints. It's not something you get from somewhere - you generate it!

## Quick Methods to Generate API Key

### Method 1: Using Python (Recommended)
```python
import secrets
api_key = secrets.token_urlsafe(32)
print(f"WEB_API_KEY={api_key}")
```

Or run this one-liner:
```bash
python -c "import secrets; print('WEB_API_KEY=' + secrets.token_urlsafe(32))"
```

### Method 2: Using OpenSSL
```bash
openssl rand -hex 32
```

Then add to `.env`:
```env
WEB_API_KEY=your-generated-key-here
```

### Method 3: Using UUID (Less secure, but works)
```bash
python -c "import uuid; print('WEB_API_KEY=' + str(uuid.uuid4()).replace('-', ''))"
```

### Method 4: Online Generator
You can also use online tools like:
- https://randomkeygen.com/
- https://www.uuidgenerator.net/
- Generate a random string with at least 32 characters

## Setting Up API Key

1. **Generate a key** using one of the methods above

2. **Add to your `.env` file:**
```env
WEB_API_KEY=your-generated-secret-key-here-make-it-long-and-random
```

3. **Or set it in the database:**
```
.setdb WEB_API_KEY your-generated-secret-key-here
```

4. **Restart your bot** (or restart the web API):
```
.webapi stop
.webapi start
```

## Important Notes

⚠️ **Security Tips:**
- Use a **long, random** key (at least 32 characters)
- **Never share** your API key publicly
- **Don't commit** `.env` file to git
- Use different keys for different environments (dev/prod)

✅ **Optional but Recommended:**
- The API key is **optional** - if not set, the API works without authentication
- Setting an API key **adds security** and prevents unauthorized access
- For production use, **always set an API key**

## Usage

### Without API Key (Less Secure)
```bash
# API works without authentication
curl http://localhost:8000/api/stats
```

### With API Key (Recommended)
```bash
# Include API key in header
curl -H "X-API-Key: your-generated-key-here" http://localhost:8000/api/stats
```

### In Dashboard
The dashboard automatically uses the API key if configured. No manual setup needed!

## Example

**Step 1: Generate key**
```bash
$ python -c "import secrets; print('WEB_API_KEY=' + secrets.token_urlsafe(32))"
WEB_API_KEY=xK9mP2qL8vR4tN6wY7zA3bC5dE1fG9hJ0kL2mN4pQ6rS8tU0vW2xY4zA6bC8dE
```

**Step 2: Add to .env**
```env
WEB_API_KEY=xK9mP2qL8vR4tN6wY7zA3bC5dE1fG9hJ0kL2mN4pQ6rS8tU0vW2xY4zA6bC8dE
```

**Step 3: Restart web API**
```
.webapi stop
.webapi start
```

**Step 4: Use in requests**
```bash
curl -H "X-API-Key: xK9mP2qL8vR4tN6wY7zA3bC5dE1fG9hJ0kL2mN4pQ6rS8tU0vW2xY4zA6bC8dE" \
     http://localhost:8000/api/stats
```

That's it! Your API is now secured. 🔒

