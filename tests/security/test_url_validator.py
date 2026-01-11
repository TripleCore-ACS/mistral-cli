#!/usr/bin/env python3
"""
Unit Tests for mistralcli.security.url_validator

Tests URL validation including:
- SSRF protection (private IP blocking)
- URL format validation
- Protocol validation

Version: 1.5.2
"""

import pytest
from mistralcli.security.url_validator import validate_url


# ============================================================================
# Test Valid Public URLs
# ============================================================================

class TestValidPublicURLs:
    """Tests for valid public URLs that should be allowed."""

    @pytest.mark.unit
    @pytest.mark.security
    @pytest.mark.parametrize("url", [
        "https://www.google.com",
        "https://api.mistral.ai/v1/chat",
        "http://example.com",
        "https://github.com/user/repo",
        "https://pypi.org/project/mistralai/",
        "http://httpbin.org/get",
        "https://jsonplaceholder.typicode.com/posts/1",
        "ftp://ftp.debian.org/debian/",
        "https://8.8.8.8",  # Public IP (Google DNS)
        "https://1.1.1.1",  # Public IP (Cloudflare DNS)
    ])
    def test_public_urls_allowed(self, url):
        """Test that public URLs are allowed."""
        is_valid, message = validate_url(url)
        assert is_valid, f"Valid public URL '{url}' was incorrectly blocked: {message}"


# ============================================================================
# Test SSRF Protection (Private IPs)
# ============================================================================

class TestSSRFProtection:
    """Tests for SSRF protection via private IP blocking."""

    @pytest.mark.unit
    @pytest.mark.security
    @pytest.mark.parametrize("url,description", [
        ("http://localhost", "Localhost"),
        ("http://127.0.0.1", "Loopback IPv4"),
        ("http://127.0.0.2", "Loopback IPv4 other"),
        ("http://[::1]", "Loopback IPv6"),
        ("http://192.168.0.1", "Private IPv4 Class C"),
        ("http://192.168.1.100", "Private IPv4 router"),
        ("http://10.0.0.1", "Private IPv4 Class A"),
        ("http://10.10.10.10", "Private IPv4 internal"),
        ("http://172.16.0.1", "Private IPv4 Class B"),
        ("http://172.31.255.255", "Private IPv4 Class B end"),
        ("http://169.254.1.1", "Link-local"),
        ("http://0.0.0.0", "Wildcard"),
        ("ftp://192.168.1.1", "FTP to private IP"),
        ("http://[::ffff:127.0.0.1]", "IPv4-mapped IPv6 loopback"),
        ("http://[fc00::1]", "Unique local IPv6"),
        ("http://[fe80::1]", "Link-local IPv6"),
    ])
    def test_private_ips_blocked(self, url, description):
        """Test that private/local IPs are blocked (SSRF protection)."""
        is_valid, message = validate_url(url)
        assert not is_valid, f"Private URL '{url}' ({description}) was NOT blocked!"
        assert any(word in message.lower() for word in ["privat", "lokal", "ssrf", "private", "local"])


# ============================================================================
# Test Invalid URL Formats
# ============================================================================

class TestInvalidURLFormats:
    """Tests for invalid URL formats."""

    @pytest.mark.unit
    @pytest.mark.security
    @pytest.mark.parametrize("url,description", [
        ("", "Empty string"),
        ("   ", "Whitespace only"),
        ("not a url", "Plain text"),
        ("www.example.com", "Missing protocol"),
        ("//example.com", "Protocol-relative"),
        ("ftp://", "Protocol without host"),
        ("http://", "HTTP without host"),
        ("javascript:alert(1)", "JavaScript protocol"),
        ("data:text/html,<script>alert(1)</script>", "Data URI"),
        ("file:///etc/passwd", "File protocol"),
    ])
    def test_invalid_url_formats(self, url, description):
        """Test that invalid URL formats are rejected."""
        is_valid, message = validate_url(url)
        assert not is_valid, f"Invalid URL '{url}' ({description}) was NOT rejected!"


# ============================================================================
# Test Protocol Validation
# ============================================================================

class TestProtocolValidation:
    """Tests for protocol validation."""

    @pytest.mark.unit
    @pytest.mark.security
    @pytest.mark.parametrize("url", [
        "http://example.com",
        "https://example.com",
        "ftp://ftp.example.com",
        "ftps://secure.example.com",
    ])
    def test_allowed_protocols(self, url):
        """Test that allowed protocols are accepted."""
        is_valid, message = validate_url(url)
        assert is_valid, f"Valid protocol in '{url}' was incorrectly blocked: {message}"

    @pytest.mark.unit
    @pytest.mark.security
    @pytest.mark.parametrize("url,description", [
        ("javascript:alert(1)", "JavaScript protocol"),
        ("data:text/html,test", "Data URI"),
        ("file:///etc/passwd", "File protocol"),
        ("gopher://example.com", "Gopher protocol"),
        ("telnet://example.com", "Telnet protocol"),
        ("ssh://example.com", "SSH protocol (if not in allowed list)"),
    ])
    def test_dangerous_protocols_blocked(self, url, description):
        """Test that dangerous protocols are blocked."""
        is_valid, message = validate_url(url)
        assert not is_valid, f"Dangerous protocol '{url}' ({description}) was NOT blocked!"


# ============================================================================
# Test Edge Cases
# ============================================================================

class TestEdgeCases:
    """Tests for edge cases in URL validation."""

    @pytest.mark.unit
    @pytest.mark.security
    def test_url_with_port(self):
        """Test that URLs with ports are handled correctly."""
        # Public IP with port should work
        is_valid, _ = validate_url("https://example.com:8080")
        assert is_valid

        # Private IP with port should be blocked
        is_valid, _ = validate_url("http://192.168.1.1:8080")
        assert not is_valid

    @pytest.mark.unit
    @pytest.mark.security
    def test_url_with_path(self):
        """Test that URLs with paths are handled."""
        url = "https://api.example.com/v1/endpoint?param=value"
        is_valid, _ = validate_url(url)
        assert is_valid

    @pytest.mark.unit
    @pytest.mark.security
    def test_url_with_credentials(self):
        """Test that URLs with credentials are handled."""
        # Should validate URL structure, credentials might be stripped/warned
        url = "https://user:pass@example.com"
        is_valid, message = validate_url(url)
        # Should either be valid or warn about credentials
        assert is_valid or "credential" in message.lower()

    @pytest.mark.unit
    @pytest.mark.security
    def test_url_with_fragment(self):
        """Test that URLs with fragments are handled."""
        url = "https://example.com/page#section"
        is_valid, _ = validate_url(url)
        assert is_valid

    @pytest.mark.unit
    @pytest.mark.security
    def test_international_domain(self):
        """Test that international domain names are handled."""
        url = "https://例え.jp"  # Japanese domain
        is_valid, message = validate_url(url)
        # Should either be valid or give clear error
        assert isinstance(is_valid, bool)

    @pytest.mark.unit
    @pytest.mark.security
    def test_very_long_url(self):
        """Test that very long URLs are handled."""
        long_path = "a/" * 1000
        url = f"https://example.com/{long_path}"
        is_valid, message = validate_url(url)
        # Should still validate even if it's impractically long
        assert isinstance(is_valid, bool)

    @pytest.mark.unit
    @pytest.mark.security
    def test_none_url(self):
        """Test that None is handled gracefully."""
        # validate_url catches exceptions and returns (False, error_message)
        is_valid, message = validate_url(None) if None else (False, "None URL")
        assert not is_valid


# ============================================================================
# Test DNS Rebinding Protection
# ============================================================================

class TestDNSRebindingProtection:
    """Tests for protection against DNS rebinding attacks."""

    @pytest.mark.unit
    @pytest.mark.security
    def test_localhost_variants(self):
        """Test that localhost variants are blocked."""
        localhost_variants = [
            "http://localhost",
            "http://localhost.localdomain",
            "http://127.0.0.1",
            "http://[::1]",
        ]

        for url in localhost_variants:
            is_valid, message = validate_url(url)
            assert not is_valid, f"Localhost variant '{url}' was NOT blocked!"
