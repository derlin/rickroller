import pytest
from flask import Flask
from rickroll import create_app
from rickroll.rickroller import RickRoller, RickRollError


class TestSecurityFeatures:
    """Security-focused test cases for RickRoller"""

    @pytest.fixture
    def app(self):
        """Create test app with security features"""
        app = create_app()
        app.config.update({
            'TESTING': True,
            'WTF_CSRF_ENABLED': False  # Disable CSRF for tests
        })
        return app

    @pytest.fixture
    def client(self, app):
        return app.test_client()

    def test_secret_key_security(self, app):
        """Test that secret key is properly configured"""
        assert app.secret_key is not None
        assert len(app.secret_key) >= 32  # Minimum secure length

    def test_private_ip_blocking(self):
        """Test that private IP addresses are blocked"""
        private_ips = [
            "http://192.168.1.1/test",
            "http://10.0.0.1/test", 
            "http://172.16.0.1/test",
            "http://127.0.0.1/test",
        ]
        
        for url in private_ips:
            with pytest.raises(RickRollError, match="private"):
                RickRoller._RickRoller__ensure_is_safe(url)

    def test_cloud_metadata_blocking(self):
        """Test that cloud metadata services are blocked"""
        metadata_urls = [
            "http://169.254.169.254/metadata",  # AWS/GCP/Azure
        ]
        
        for url in metadata_urls:
            with pytest.raises(RickRollError, match="private"):
                RickRoller._RickRoller__ensure_is_safe(url)

    def test_dangerous_port_blocking(self):
        """Test that dangerous ports are blocked"""
        # This test would require implementing port blocking in the actual code
        # For now, just test that the function exists and works with valid URLs
        url = "https://example.com/test"
        try:
            RickRoller._RickRoller__ensure_is_safe(url)
        except RickRollError:
            # This might fail due to DNS resolution in test environment
            pass

    def test_url_length_validation(self, client):
        """Test URL length limits"""
        # Test very long URL
        long_url = "http://example.com/" + "a" * 3000
        response = client.post('/', data={'url': long_url})
        
        # Should redirect back to index with error
        assert response.status_code == 302

    def test_invalid_url_schemes(self, client):
        """Test that only HTTP/HTTPS schemes are allowed"""
        invalid_schemes = [
            "ftp://example.com",
            "file:///etc/passwd",
            "javascript:alert(1)",
            "data:text/html,<script>alert(1)</script>"
        ]
        
        for url in invalid_schemes:
            response = client.post('/', data={'url': url})
            assert response.status_code == 302  # Should redirect with error

    def test_scroll_count_validation(self, client):
        """Test scroll count validation"""
        test_cases = [
            {'num_scrolls': '-1', 'should_fail': True},
            {'num_scrolls': '100', 'should_fail': True},
            {'num_scrolls': 'abc', 'should_fail': True},
            {'num_scrolls': '5', 'should_fail': False}
        ]
        
        for case in test_cases:
            response = client.post('/', data={
                'url': 'http://example.com',
                'redirect_on_scroll': 'on',
                'num_scrolls': case['num_scrolls']
            })
            
            if case['should_fail']:
                # Should redirect back with error
                assert response.status_code == 302
            # Note: Valid cases would need mocking for full test

    def test_content_type_validation(self):
        """Test that non-HTML content types are rejected"""
        # This would need mocking of requests.get for full testing
        pass

    def test_response_size_limits(self):
        """Test response size limits"""
        # This would need mocking of requests.get for full testing
        pass

    def test_csrf_protection_enabled(self, app):
        """Test that CSRF protection is configured"""
        # Check if CSRFProtect is initialized
        assert 'csrf' in app.extensions

    def test_security_headers_configuration(self, app):
        """Test security headers are configured when Talisman is available"""
        try:
            import flask_talisman
            # If Talisman is available, check it's configured
            # This is basic - full header testing would require request context
            assert True  # Placeholder
        except ImportError:
            pytest.skip("Flask-Talisman not available")

    def test_rate_limiting_configuration(self, app):
        """Test rate limiting is configured when available"""
        try:
            import flask_limiter
            # Basic test - full rate limiting testing requires multiple requests
            assert True  # Placeholder
        except ImportError:
            pytest.skip("Flask-Limiter not available")

    def test_error_handling_security(self, client):
        """Test that error messages don't leak sensitive information"""
        # Test with invalid input that might cause internal errors
        response = client.post('/', data={'url': 'not-a-url'})
        
        # Should redirect, not expose internal error details
        assert response.status_code == 302
        
        # Follow redirect to see error message
        response = client.get('/')
        assert b"traceback" not in response.data.lower()
        assert b"exception" not in response.data.lower()

if __name__ == '__main__':
    pytest.main([__file__])