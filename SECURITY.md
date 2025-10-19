# Security Configuration for RickRoller
# This file contains security-related configuration options

## Environment Variables for Security

# Flask Secret Key - MUST be set in production
# Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
# APP_SECRET_KEY=your_secure_random_key_here

# Rate Limiting Storage (optional - uses in-memory if not set)
# REDIS_URL=redis://localhost:6379/0
# RATE_LIMIT_STORAGE_URL=redis://localhost:6379/0

# Proxy Configuration (set to true if behind reverse proxy)
# BEHIND_PROXY=false

# Content Security Policy Override (optional)
# CSP_DIRECTIVES="default-src 'self'; script-src 'self' 'unsafe-inline'"

## Recommended Security Headers (handled by Flask-Talisman)
# - Strict-Transport-Security (HSTS)
# - X-Frame-Options
# - X-Content-Type-Options
# - Content-Security-Policy
# - Referrer-Policy

## Rate Limits (default values)
# Global: 100 requests per hour, 20 per minute
# POST /: 10 requests per minute

## Request Size Limits
# Maximum request size: 16MB
# Maximum URL length: 2048 characters
# Maximum response size: 50MB
# Request timeout: 10 seconds

## IP Address Restrictions
# Private IP ranges are blocked
# Localhost access is blocked
# Cloud metadata services (169.254.169.254) are blocked
# Common service ports (22, 25, 3306, etc.) are blocked

## Content Validation
# Only HTML and XHTML content types are allowed
# Response size is limited to prevent memory attacks
# All redirect URLs are validated for security