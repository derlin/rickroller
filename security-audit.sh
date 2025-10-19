#!/bin/bash
# Security audit script for RickRoller

echo "🔍 RickRoller Security Audit"
echo "============================"

# Check if security dependencies are installed
echo "📦 Checking security dependencies..."
python -c "import flask_talisman; print('✅ flask-talisman: OK')" 2>/dev/null || echo "❌ flask-talisman: MISSING"
python -c "import flask_limiter; print('✅ flask-limiter: OK')" 2>/dev/null || echo "❌ flask-limiter: MISSING"

# Check for hardcoded secrets
echo
echo "🔑 Checking for hardcoded secrets..."
if grep -r "secret.*=" --include="*.py" . | grep -v "getenv\|secrets\|SECURITY.md"; then
    echo "❌ Found potential hardcoded secrets"
else
    echo "✅ No hardcoded secrets found"
fi

# Check environment variables
echo
echo "🌍 Checking security environment variables..."
if [ -z "$APP_SECRET_KEY" ]; then
    echo "⚠️  APP_SECRET_KEY not set - using random key (not suitable for production)"
else
    echo "✅ APP_SECRET_KEY is configured"
fi

# Check for HTTPS enforcement
echo
echo "🔒 Security configurations..."
if [ "$BEHIND_PROXY" = "true" ]; then
    echo "✅ Proxy mode enabled"
else
    echo "ℹ️  Direct mode (no proxy)"
fi

# Check dependencies for known vulnerabilities
echo
echo "🛡️  Checking dependencies for vulnerabilities..."
if command -v safety >/dev/null 2>&1; then
    safety check --json 2>/dev/null || echo "⚠️  Run 'pip install safety && safety check' to scan dependencies"
else
    echo "⚠️  Install 'safety' to scan dependencies: pip install safety"
fi

# Check permissions
echo
echo "📁 File permissions check..."
find . -name "*.py" -perm /o+w 2>/dev/null && echo "❌ World-writable Python files found" || echo "✅ File permissions OK"

echo
echo "✅ Security audit complete!"
echo "💡 For production deployment:"
echo "   - Set APP_SECRET_KEY environment variable"
echo "   - Enable HTTPS (use BEHIND_PROXY=true if behind reverse proxy)"
echo "   - Set up Redis for rate limiting (REDIS_URL)"
echo "   - Monitor logs for security events"
echo "   - Keep dependencies updated"