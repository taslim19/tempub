# How to Get/Set WEB_API_KEY

## Quick Answer

The `WEB_API_KEY` is **not something you get** - you **generate it yourself** as a secret password for your API.

## 🚀 Easy Way to Generate

### Option 1: Run the Helper Script
```bash
python plugins/webapi_setup.py
```

This will generate a secure key and show you what to add to your `.env` file.

### Option 2: One-Line Command
```bash
python -c "import secrets; print('WEB_API_KEY=' + secrets.token_urlsafe(32))"
```

Copy the output and add it to your `.env` file.

### Option 3: Manual Method
1. Go to https://randomkeygen.com/ or any random string generator
2. Generate a random string (at least 32 characters)
3. Add it to your `.env` file

## 📝 Setting It Up

After generating the key, add it to your `.env` file:

```env
WEB_API_KEY=your-generated-key-here-paste-it-here
```

## 🔐 Is It Required?

**No, it's optional!**

- ✅ **Without API Key**: API works, but **less secure** (anyone can access)
- ✅ **With API Key**: API is **protected** - only requests with the correct key can access

**For production use, always set an API key!**

## 📍 Where to Set It

1. **In `.env` file** (recommended):
   ```env
   WEB_API_KEY=your-key-here
   ```

2. **In database**:
   ```
   .setdb WEB_API_KEY your-key-here
   ```

3. **As environment variable**:
   ```bash
   export WEB_API_KEY=your-key-here
   ```

## 🎯 Complete Example

```bash
# Step 1: Generate key
$ python -c "import secrets; print('WEB_API_KEY=' + secrets.token_urlsafe(32))"
WEB_API_KEY=xK9mP2qL8vR4tN6wY7zA3bC5dE1fG9hJ0kL2mN4pQ6rS8tU0vW2xY4zA6bC8dE

# Step 2: Add to .env file
nano .env
# Add this line:
WEB_API_KEY=xK9mP2qL8vR4tN6wY7zA3bC5dE1fG9hJ0kL2mN4pQ6rS8tU0vW2xY4zA6bC8dE

# Step 3: Start web API
.webapi start
```

That's it! Your API is now secured. 🔒

## 💡 Tips

- Use a **long, random** key (at least 32 characters)
- **Never share** your API key publicly
- **Don't commit** `.env` file to git
- The dashboard will automatically use the key if configured

