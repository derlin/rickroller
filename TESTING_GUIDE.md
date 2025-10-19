# 🚀 Running RickRoller Locally for Testing

## Quick Start (5 minutes)

### 1. **Setup Dependencies**
```bash
# Navigate to the project directory
cd /home/richard/repos/public/rickroller

# Install dependencies (already done for you)
# poetry install

# Or if using pip directly:
# pip install Flask flask-wtf flask-talisman flask-limiter requests beautifulsoup4 validators SQLAlchemy

# Verify installation
./verify-security.py
```

### 2. **Run the Application**

**Option A: Simple Development Server**
```bash
# Run with Python module (recommended)
/home/richard/repos/public/rickroller/.venv/bin/python -m rickroll --debug --port 8080

# Or using Poetry (if working)
poetry run python -m rickroll --debug --port 8080
```

**Option B: Direct Flask Run**
```bash
# Set environment and run
export FLASK_APP=rickroll
export FLASK_ENV=development
/home/richard/repos/public/rickroller/.venv/bin/python -c "from rickroll import create_app; create_app().run(debug=True, port=8080)"
```

### 3. **Access the Application**
Once running, open your browser and go to:
- **Local access**: http://localhost:8080
- **Network access**: http://0.0.0.0:8080 (if running with --host 0.0.0.0)

## 🧪 **Testing the RickRoller**

### Test URLs to Try:
1. **Simple test**: `https://example.com`
2. **News site**: `https://news.ycombinator.com` 
3. **GitHub repo**: `https://github.com/torvalds/linux`
4. **Documentation**: `https://docs.python.org`

### Expected Behavior:
1. Enter a URL in the form
2. Click submit
3. Get a rickroll URL like: `http://localhost:8080/t0/abc123def456`
4. Share that link - when someone clicks it, they see the original content
5. But any click on the page redirects to the rickroll! 😄

## 🔧 **Configuration Options**

### Environment Variables (Optional):
```bash
# Security (recommended for production)
export APP_SECRET_KEY="your-secure-secret-key-here"

# Proxy settings (if behind reverse proxy)
export BEHIND_PROXY=true

# Rate limiting storage (optional)  
export REDIS_URL=redis://localhost:6379/0

# Database for URL shortening (optional)
export DATABASE_URL=sqlite:///rickroll.db
```

### Command Line Options:
```bash
/home/richard/repos/public/rickroller/.venv/bin/python -m rickroll \
  --host 0.0.0.0 \    # Listen on all interfaces
  --port 8080 \       # Port number  
  --debug             # Enable debug mode (auto-reload)
```

## 🔍 **Troubleshooting**

### Common Issues:

**1. Import Errors**
```bash
# Make sure you're using the virtual environment
/home/richard/repos/public/rickroller/.venv/bin/python -c "import flask; print('Flask OK')"
```

**2. Port Already in Use**
```bash
# Try a different port
/home/richard/repos/public/rickroller/.venv/bin/python -m rickroll --port 8081
```

**3. Network Access Issues**
```bash
# For external access, bind to all interfaces
/home/richard/repos/public/rickroller/.venv/bin/python -m rickroll --host 0.0.0.0 --port 8080
```

**4. Security Features Not Working**
```bash
# Verify security setup
./verify-security.py

# Check what's installed
/home/richard/repos/public/rickroller/.venv/bin/python -c "
import flask_talisman; print('Talisman: OK')
import flask_limiter; print('Limiter: OK')
"
```

## 🧪 **Testing Security Features**

### Test SSRF Protection:
Try these URLs (they should be blocked):
- `http://localhost/test` 
- `http://127.0.0.1/test`
- `http://192.168.1.1/test`

### Test Input Validation:
- Very long URLs (>2048 characters)
- Invalid URLs like `not-a-url`
- Non-HTTP schemes like `ftp://example.com`

### Test Rate Limiting:
- Submit many requests quickly
- Should get rate limited after 10 POST requests per minute

## 🐳 **Docker Option** (Alternative)

If you prefer Docker:
```bash
# Build the image
docker build -t rickroller .

# Run with port mapping
docker run -p 8080:8080 rickroller

# With environment variables
docker run -p 8080:8080 \
  -e APP_SECRET_KEY="secure-key" \
  -e BEHIND_PROXY=false \
  rickroller
```

## 📝 **Development Notes**

- **Debug Mode**: Auto-reloads on code changes
- **Security Headers**: Disabled in debug mode for easier testing  
- **HTTPS**: Not required for local testing
- **Database**: Uses in-memory by default (no persistence)
- **Rate Limiting**: Uses in-memory storage (resets on restart)

## 🎯 **What to Test**

1. **Basic Functionality**: Create rickroll links
2. **Security Features**: Try malicious inputs
3. **UI/UX**: Test the web interface  
4. **Error Handling**: Invalid inputs, network errors
5. **Performance**: Multiple concurrent requests

Have fun rickrolling! 😄🎵