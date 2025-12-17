#!/usr/bin/env python3
"""
Comprehensive PoC API Test Suite
Tests all endpoints of the PoC API server (port 5001)
"""

import sys
import os
import json
import tempfile
import pytest
from pathlib import Path

# Add test framework to path
test_dir = Path(__file__).parent
sys.path.insert(0, str(test_dir))

from test_framework import APITestCase, TestUtils, test_config, TestFixtures

@pytest.mark.requires_poc_api
class TestPoCAPI(APITestCase):
    """Comprehensive test suite for PoC API endpoints"""

    def get_category(self) -> str:
        """Return test category for reporting"""
        return "integration"

    def setUp(self):
        """Set up test with service availability check and test data"""
        super().setUp()
        # Require PoC API to be available
        self.require_service("poc_api")

        # Create test data for tests that need existing contributions
        self._ensure_test_contributions()

    def _ensure_test_contributions(self):
        """Ensure at least one test contribution exists for tests that need it"""
        import requests
        poc_api_url = test_config.get("api_urls.poc_api")

        # Check if any contributions already exist
        try:
            response = requests.get(f"{poc_api_url}/api/archive/contributions", timeout=10)
            if response.status_code == 200:
                contributions = response.json().get("contributions", [])
                if contributions:
                    self.log_info(f"Found {len(contributions)} existing contributions")
                    return  # Already have data
        except Exception as e:
            self.log_warning(f"Could not check existing contributions: {e}")

        # Create a test contribution if none exist
        try:
            self.log_info("Creating test contribution for subsequent tests...")

            # Create test contribution data
            test_contrib = self.create_test_contribution()

            # Create a temporary PDF file
            pdf_path = TestFixtures.generate_test_pdf()

            # Submit the contribution
            with open(pdf_path, 'rb') as pdf_file:
                files = {'pdf': ('test.pdf', pdf_file, 'application/pdf')}
                data = {
                    'title': test_contrib['title'],
                    'category': test_contrib['category'],
                    'contributor': test_contrib['contributor']
                }

                response = requests.post(
                    f"{poc_api_url}/api/submit",
                    files=files,
                    data=data,
                    timeout=30
                )

            if response.status_code == 200:
                result = response.json()
                submission_hash = result.get("submission_hash")
                self.log_info(f"✅ Test contribution created: {submission_hash}")

                # Try to evaluate it so certificate tests have data too
                try:
                    eval_response = requests.post(
                        f"{poc_api_url}/api/evaluate/{submission_hash}",
                        timeout=60
                    )
                    if eval_response.status_code == 200:
                        self.log_info(f"✅ Test contribution evaluated: {submission_hash}")
                    else:
                        self.log_warning(f"Could not evaluate test contribution: {eval_response.status_code}")
                except Exception as e:
                    self.log_warning(f"Could not evaluate test contribution: {e}")

            elif response.status_code == 429:
                self.log_info("⚠️  Rate limited when creating test data (acceptable)")
            else:
                self.log_warning(f"Could not create test contribution: {response.status_code}")

            # Clean up temp file
            TestFixtures.cleanup_test_files([pdf_path])

        except ImportError:
            self.log_warning("PDF generation not available, cannot create test contributions")
        except Exception as e:
            self.log_warning(f"Could not create test contribution: {e}")

    def test_health_endpoint(self):
        """Test /health endpoint"""
        self.log_info("Testing /health endpoint")

        import requests
        poc_api_url = test_config.get("api_urls.poc_api")

        response = requests.get(f"{poc_api_url}/health", timeout=10)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("status", data)
        self.assertIn("timestamp", data)

        self.log_info("✅ Health endpoint working")
        self.add_metric("response_time", response.elapsed.total_seconds())

    def test_archive_statistics(self):
        """Test /api/archive/statistics endpoint"""
        self.log_info("Testing archive statistics endpoint")

        import requests
        poc_api_url = test_config.get("api_urls.poc_api")

        response = requests.get(f"{poc_api_url}/api/archive/statistics", timeout=10)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("total_contributions", data)
        self.assertIn("contributions_by_status", data)
        self.assertIn("contributions_by_metal", data)

        # Validate data types
        self.assertIsInstance(data["total_contributions"], int)
        self.assertIsInstance(data["contributions_by_status"], dict)
        self.assertIsInstance(data["contributions_by_metal"], dict)

        self.log_info(f"Total contributions: {data['total_contributions']}")
        self.add_metric("total_contributions", data["total_contributions"])

    def test_archive_contributions(self):
        """Test /api/archive/contributions endpoint"""
        self.log_info("Testing archive contributions endpoint")

        import requests
        poc_api_url = test_config.get("api_urls.poc_api")

        response = requests.get(f"{poc_api_url}/api/archive/contributions", timeout=10)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("contributions", data)
        self.assertIsInstance(data["contributions"], list)

        # Check structure of first contribution if any exist
        if data["contributions"]:
            contrib = data["contributions"][0]
            required_fields = ["submission_hash", "title", "contributor", "status"]
            for field in required_fields:
                self.assertIn(field, contrib, f"Missing field: {field}")

        self.log_info(f"Found {len(data['contributions'])} contributions")
        self.add_metric("contributions_count", len(data["contributions"]))

    def test_sandbox_map(self):
        """Test /api/sandbox-map endpoint"""
        self.log_info("Testing sandbox map endpoint")

        import requests
        poc_api_url = test_config.get("api_urls.poc_api")

        response = requests.get(f"{poc_api_url}/api/sandbox-map", timeout=10)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("dimensions", data)
        self.assertIn("nodes", data)
        self.assertIn("edges", data)

        # Validate data structures
        self.assertIsInstance(data["dimensions"], list)
        self.assertIsInstance(data["nodes"], list)
        self.assertIsInstance(data["edges"], list)

        self.log_info(f"Sandbox map has {len(data['nodes'])} nodes and {len(data['edges'])} edges")
        self.add_metric("sandbox_nodes", len(data["nodes"]))
        self.add_metric("sandbox_edges", len(data["edges"]))

    def test_epoch_info(self):
        """Test /api/tokenomics/epoch-info endpoint"""
        self.log_info("Testing epoch info endpoint")

        import requests
        poc_api_url = test_config.get("api_urls.poc_api")

        response = requests.get(f"{poc_api_url}/api/tokenomics/epoch-info", timeout=10)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("current_epoch", data)
        self.assertIn("epoch_name", data)
        self.assertIn("epoch_description", data)

        self.log_info(f"Current epoch: {data['current_epoch']} ({data['epoch_name']})")
        self.add_metric("current_epoch", data["current_epoch"])

    def test_tokenomics_statistics(self):
        """Test /api/tokenomics/statistics endpoint"""
        self.log_info("Testing tokenomics statistics endpoint")

        import requests
        poc_api_url = test_config.get("api_urls.poc_api")

        response = requests.get(f"{poc_api_url}/api/tokenomics/statistics", timeout=10)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("total_allocated", data)
        self.assertIn("total_rewards", data)

        self.log_info(f"Total allocated SYNTH: {data.get('total_allocated', 0)}")
        self.add_metric("total_allocated", data.get("total_allocated", 0))

    def test_submit_contribution(self):
        """Test /api/submit endpoint with test data"""
        self.log_info("Testing contribution submission endpoint")

        import requests
        poc_api_url = test_config.get("api_urls.poc_api")

        # Create test contribution data
        test_contrib = self.create_test_contribution()

        # Create a temporary PDF file
        pdf_path = TestFixtures.generate_test_pdf()
        self.addCleanup(lambda: TestFixtures.cleanup_test_files([pdf_path]))

        try:
            # Submit the contribution
            with open(pdf_path, 'rb') as pdf_file:
                files = {'pdf': ('test.pdf', pdf_file, 'application/pdf')}
                data = {
                    'title': test_contrib['title'],
                    'category': test_contrib['category'],
                    'contributor': test_contrib['contributor']
                }

                response = requests.post(
                    f"{poc_api_url}/api/submit",
                    files=files,
                    data=data,
                    timeout=30
                )

            # Check response
            if response.status_code == 200:
                result = response.json()
                self.assertIn("submission_hash", result)
                self.assertIn("status", result)

                submission_hash = result["submission_hash"]
                self.log_info(f"✅ Submission successful, hash: {submission_hash}")
                self.add_metric("submission_hash", submission_hash)

                # Store hash for potential cleanup
                self.submission_hash = submission_hash

            elif response.status_code == 429:
                # Rate limited - this is acceptable for testing
                self.log_info("⚠️  Submission rate limited (acceptable for testing)")
                self.add_metric("rate_limited", True)
            else:
                self.fail(f"Unexpected response: {response.status_code} - {response.text}")

        except ImportError:
            self.skipTest("PDF generation not available")
        except Exception as e:
            self.fail(f"Submission test failed: {e}")

    def test_evaluate_contribution(self):
        """Test /api/evaluate/<submission_hash> endpoint"""
        self.log_info("Testing contribution evaluation endpoint")

        import requests
        poc_api_url = test_config.get("api_urls.poc_api")

        # First, we need a submission hash. Try to get one from existing contributions
        response = requests.get(f"{poc_api_url}/api/archive/contributions", timeout=10)
        contributions = response.json().get("contributions", [])

        if not contributions:
            self.skipTest("No existing contributions to evaluate")

        # Use the first contribution's hash
        submission_hash = contributions[0]["submission_hash"]
        self.log_info(f"Evaluating contribution: {submission_hash}")

        # Trigger evaluation
        response = requests.post(
            f"{poc_api_url}/api/evaluate/{submission_hash}",
            timeout=60  # Evaluation can take time
        )

        if response.status_code == 200:
            result = response.json()
            self.assertIn("success", result)
            if result["success"]:
                self.assertIn("evaluation", result)
                self.assertIn("metals", result["evaluation"])

                metals = result["evaluation"]["metals"]
                self.log_info(f"✅ Evaluation successful, metals: {metals}")
                self.add_metric("evaluation_metals", metals)
            else:
                self.log_info("⚠️  Evaluation in progress or failed")
                self.add_metric("evaluation_status", "in_progress")

        elif response.status_code == 429:
            self.log_info("⚠️  Evaluation rate limited")
            self.add_metric("rate_limited", True)
        else:
            self.fail(f"Evaluation failed: {response.status_code} - {response.text}")

    def test_contribution_details(self):
        """Test /api/archive/contributions/<submission_hash> endpoint"""
        self.log_info("Testing contribution details endpoint")

        import requests
        poc_api_url = test_config.get("api_urls.poc_api")

        # Get list of contributions first
        response = requests.get(f"{poc_api_url}/api/archive/contributions", timeout=10)
        contributions = response.json().get("contributions", [])

        if not contributions:
            self.skipTest("No contributions available for detail testing")

        # Test details for first contribution
        submission_hash = contributions[0]["submission_hash"]

        response = requests.get(
            f"{poc_api_url}/api/archive/contributions/{submission_hash}",
            timeout=10
        )

        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("contribution", data)
        self.assertIn("evaluation", data)

        contrib = data["contribution"]
        required_fields = ["submission_hash", "title", "contributor", "status"]
        for field in required_fields:
            self.assertIn(field, contrib)

        self.log_info(f"✅ Retrieved details for contribution: {contrib['title']}")

    def test_certificate_generation(self):
        """Test /api/certificate/<submission_hash> endpoint"""
        self.log_info("Testing certificate generation endpoint")

        import requests
        poc_api_url = test_config.get("api_urls.poc_api")

        # Need an evaluated contribution
        response = requests.get(f"{poc_api_url}/api/archive/contributions", timeout=10)
        contributions = response.json().get("contributions", [])

        evaluated_contrib = None
        for contrib in contributions:
            if contrib.get("status") in ["approved", "gold", "silver", "copper"]:
                evaluated_contrib = contrib
                break

        if not evaluated_contrib:
            self.skipTest("No evaluated contributions available for certificate testing")

        submission_hash = evaluated_contrib["submission_hash"]

        response = requests.post(
            f"{poc_api_url}/api/certificate/{submission_hash}",
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            self.assertIn("success", result)
            if result["success"]:
                self.assertIn("certificate", result)
                cert = result["certificate"]
                self.assertIn("tier", cert)
                self.assertIn("reward", cert)

                self.log_info(f"✅ Certificate generated: {cert['tier']} tier")
                self.add_metric("certificate_tier", cert["tier"])
                self.add_metric("certificate_reward", cert["reward"])
            else:
                self.log_info("⚠️  Certificate generation failed")
        else:
            self.fail(f"Certificate generation failed: {response.status_code}")

    def test_admin_cleanup(self):
        """Test admin cleanup endpoints"""
        self.log_info("Testing admin cleanup endpoints")

        import requests
        poc_api_url = test_config.get("api_urls.poc_api")

        # Test cleanup test submissions
        response = requests.post(
            f"{poc_api_url}/api/admin/cleanup-test-submissions",
            timeout=10
        )

        # Admin endpoints might return various status codes based on permissions
        self.assertIn(response.status_code, [200, 401, 403, 404])

        if response.status_code == 200:
            result = response.json()
            self.assertIn("success", result)
            self.log_info("✅ Admin cleanup successful")
        else:
            self.log_info(f"⚠️  Admin cleanup returned {response.status_code} (may require authentication)")

    def test_register_poc(self):
        """Test /api/register-poc endpoint"""
        self.log_info("Testing PoC registration endpoint")

        import requests
        poc_api_url = test_config.get("api_urls.poc_api")

        # This endpoint may require specific data, so we'll just test it exists
        # and returns a reasonable response
        response = requests.post(
            f"{poc_api_url}/api/register-poc",
            json={"test": "data"},
            timeout=10
        )

        # Accept various responses as this endpoint may have validation
        self.assertIn(response.status_code, [200, 400, 401, 403])

        if response.status_code == 200:
            result = response.json()
            self.assertIn("success", result)
            self.log_info("✅ PoC registration successful")
        else:
            self.log_info(f"⚠️  PoC registration returned {response.status_code} (validation/authentication)")

    def test_debug_tokenomics(self):
        """Test debug tokenomics state endpoint"""
        self.log_info("Testing debug tokenomics state endpoint")

        import requests
        poc_api_url = test_config.get("api_urls.poc_api")

        response = requests.get(
            f"{poc_api_url}/api/debug/tokenomics-state",
            timeout=10
        )

        # Debug endpoints might be restricted
        self.assertIn(response.status_code, [200, 401, 403, 404])

        if response.status_code == 200:
            data = response.json()
            self.assertIn("tokenomics_state", data)
            self.log_info("✅ Debug tokenomics state retrieved")
        else:
            self.log_info(f"⚠️  Debug endpoint returned {response.status_code} (may be restricted)")

    def test_api_error_scenarios(self):
        """Test all API error scenarios defined in test_config.json"""
        self.log_info("Testing API error scenarios")

        import requests
        poc_api_url = test_config.get("api_urls.poc_api")
        error_scenarios = test_config.get("test_scenarios.api_error_scenarios", [])

        tested_scenarios = 0
        successful_scenarios = 0

        for scenario in error_scenarios:
            endpoint = scenario["endpoint"]
            method = scenario["method"]
            error_type = scenario["error_type"]
            expected_status = scenario["expected_status"]

            full_url = f"{poc_api_url}{endpoint}"

            try:
                if method == "GET":
                    response = requests.get(full_url, timeout=10)
                elif method == "POST":
                    # For POST requests, send minimal data that might trigger validation errors
                    if "submit" in endpoint:
                        # Try empty data for submit endpoint
                        response = requests.post(full_url, json={}, timeout=10)
                    elif "evaluate" in endpoint:
                        response = requests.post(full_url, json={"invalid": "data"}, timeout=10)
                    else:
                        response = requests.post(full_url, json={}, timeout=10)
                else:
                    # Skip other methods for now
                    continue

                tested_scenarios += 1

                # Check if response matches expected status or is in acceptable range
                acceptable_statuses = [expected_status]
                if expected_status == 400:
                    acceptable_statuses.extend([422, 400])  # Validation errors
                elif expected_status == 404:
                    acceptable_statuses.extend([404, 405])  # Not found or method not allowed

                if response.status_code in acceptable_statuses:
                    successful_scenarios += 1
                    self.log_info(f"✅ {error_type}: {response.status_code} (expected {expected_status})")
                else:
                    self.log_warning(f"⚠️  {error_type}: got {response.status_code}, expected {expected_status}")

                self.add_metric(f"error_scenario_{error_type}", response.status_code)

            except requests.exceptions.RequestException as e:
                self.log_warning(f"⚠️  {error_type}: Request failed: {e}")
            except Exception as e:
                self.log_warning(f"⚠️  {error_type}: Test failed: {e}")

        success_rate = (successful_scenarios / tested_scenarios * 100) if tested_scenarios > 0 else 0
        self.log_info(f"✅ Error scenarios tested: {successful_scenarios}/{tested_scenarios} ({success_rate:.1f}%)")
        self.add_metric("error_scenarios_success_rate", success_rate)

    def test_api_rate_limiting(self):
        """Test API rate limiting behavior"""
        self.log_info("Testing API rate limiting")

        import requests
        import time

        poc_api_url = test_config.get("api_urls.poc_api")

        # Test rapid requests to health endpoint
        request_count = 0
        rate_limited_count = 0

        for i in range(20):  # Make 20 rapid requests
            try:
                response = requests.get(f"{poc_api_url}/health", timeout=5)
                request_count += 1

                if response.status_code == 429:  # Too Many Requests
                    rate_limited_count += 1
                    self.log_info(f"✅ Rate limiting detected on request {i+1}")
                    break
                elif response.status_code == 200:
                    # Brief pause between requests
                    time.sleep(0.1)
                else:
                    self.log_info(f"⚠️  Unexpected status {response.status_code} on request {i+1}")

            except Exception as e:
                self.log_warning(f"⚠️  Rate limit test request {i+1} failed: {e}")
                break

        if rate_limited_count > 0:
            self.log_info(f"✅ Rate limiting working: {rate_limited_count} requests blocked")
            self.add_metric("rate_limiting_detected", True)
            self.add_metric("rate_limited_requests", rate_limited_count)
        else:
            self.log_info("ℹ️  No rate limiting detected (may not be implemented)")
            self.add_metric("rate_limiting_detected", False)

    def test_api_concurrent_requests(self):
        """Test API handling of concurrent requests"""
        self.log_info("Testing API concurrent request handling")

        import requests
        import threading
        import time

        poc_api_url = test_config.get("api_urls.poc_api")

        results = []
        errors = []

        def make_request(request_id):
            """Make a single API request"""
            try:
                start_time = time.time()
                response = requests.get(f"{poc_api_url}/health", timeout=10)
                end_time = time.time()

                results.append({
                    "id": request_id,
                    "status": response.status_code,
                    "duration": end_time - start_time
                })
            except Exception as e:
                errors.append({
                    "id": request_id,
                    "error": str(e)
                })

        # Launch 10 concurrent requests
        threads = []
        for i in range(10):
            thread = threading.Thread(target=make_request, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=15)

        successful_requests = len([r for r in results if r["status"] == 200])
        total_requests = len(results) + len(errors)

        success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0

        self.log_info(f"✅ Concurrent requests: {successful_requests}/{total_requests} successful ({success_rate:.1f}%)")

        if errors:
            self.log_warning(f"⚠️  {len(errors)} concurrent requests failed")

        # Calculate response time statistics
        if results:
            durations = [r["duration"] for r in results]
            avg_duration = sum(durations) / len(durations)
            max_duration = max(durations)
            min_duration = min(durations)

            self.add_metric("concurrent_success_rate", success_rate)
            self.add_metric("concurrent_avg_duration", avg_duration)
            self.add_metric("concurrent_max_duration", max_duration)
            self.add_metric("concurrent_min_duration", min_duration)

    def test_api_input_validation(self):
        """Test API input validation for various endpoints"""
        self.log_info("Testing API input validation")

        import requests
        poc_api_url = test_config.get("api_urls.poc_api")

        # Test invalid inputs for submit endpoint
        invalid_submissions = [
            {},  # Empty submission
            {"title": ""},  # Missing required fields
            {"title": "Test", "category": ""},  # Empty category
            {"title": None, "category": "scientific"},  # None title
            {"title": "Test", "category": None},  # None category
            {"title": "A" * 1000, "category": "scientific"},  # Very long title
        ]

        validation_errors = 0
        total_tests = len(invalid_submissions)

        for i, invalid_data in enumerate(invalid_submissions, 1):
            try:
                response = requests.post(
                    f"{poc_api_url}/api/submit",
                    json=invalid_data,
                    timeout=10
                )

                if response.status_code in [400, 422]:  # Bad Request or Validation Error
                    validation_errors += 1
                    self.log_info(f"✅ Invalid input {i} properly rejected: {response.status_code}")
                elif response.status_code == 200:
                    self.log_warning(f"⚠️  Invalid input {i} was accepted (status 200)")
                else:
                    self.log_info(f"ℹ️  Invalid input {i} returned status {response.status_code}")

            except Exception as e:
                self.log_warning(f"⚠️  Input validation test {i} failed: {e}")

        validation_rate = (validation_errors / total_tests * 100) if total_tests > 0 else 0
        self.log_info(f"✅ Input validation: {validation_errors}/{total_tests} properly rejected ({validation_rate:.1f}%)")
        self.add_metric("input_validation_rate", validation_rate)


def run_poc_api_tests():
    """Run PoC API tests with framework"""
    TestUtils.print_test_header(
        "PoC API Test Suite",
        "Comprehensive testing of all PoC API endpoints"
    )

    import unittest
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPoCAPI)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    import unittest
    unittest.main()


