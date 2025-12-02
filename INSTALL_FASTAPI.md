# How to Install FastAPI for Web API Plugin

## Quick Installation

### Required Packages:
```bash
pip install fastapi uvicorn[standard] python-multipart
```

### Optional (for system stats in dashboard):
```bash
pip install psutil
```

## Complete Installation (All at once)

```bash
# Install all required packages
pip install fastapi uvicorn[standard] python-multipart psutil
```

## Using Virtual Environment (Recommended)

If you're using a virtual environment (venv):

```bash
# Activate your virtual environment first
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows

# Then install
pip install fastapi uvicorn[standard] python-multipart psutil
```

## Verify Installation

After installing, verify it works:

```bash
python -c "import fastapi; import uvicorn; print('✓ FastAPI installed successfully!')"
```

## After Installation

1. Start the web API:
   ```
   .webapi start
   ```

2. Access dashboard:
   - Dashboard: http://localhost:8000 (or your configured port)
   - API Docs: http://localhost:8000/docs

That's it! 🚀

