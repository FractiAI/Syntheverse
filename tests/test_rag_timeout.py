#!/usr/bin/env python3
"""
RAG API Timeout and Performance Test
Tests RAG API response times, timeout handling, and performance metrics.
"""

import sys
import time
import pytest
from pathlib import Path

# Add test framework to path
test_dir = Path(__file__).parent
sys.path.insert(0, str(test_dir))

from test_framework import SyntheverseTestCase, TestUtils, test_config

@pytest.mark.requires_rag_api
class TestRAGTimeout(SyntheverseTestCase):
    """Test RAG API timeout and performance characteristics"""

    def get_category(self) -> str:
        """Return test category for reporting"""
        return "integration"

    def setUp(self):
        """Set up timeout tests"""
        super().setUp()
        # Check if RAG API is running
        rag_api_url = test_config.get("api_urls.rag_api")
        healthy, status = TestUtils.check_service_health(rag_api_url, timeout=5)
        if not healthy:
            self.skipTest(f"RAG API not available: {status}")

    def test_health_check_performance(self):
        """Test health check response time"""
        self.log_info("Testing RAG API health check performance")

        import requests
        rag_api_url = test_config.get("api_urls.rag_api")

        start_time = time.time()
        response = requests.get(f"{rag_api_url}/health", timeout=5)
        response_time = time.time() - start_time

        self.assertEqual(response.status_code, 200)
        self.assertLess(response_time, 2.0, f"Health check too slow: {response_time:.2f}s")

        self.log_info(f"✅ Health check responded in {response_time:.2f}s")
        self.add_metric("health_check_time", response_time)

    def test_simple_query_performance(self):
        """Test simple query performance within timeout limits"""
        self.log_info("Testing simple query performance")

        import requests
        rag_api_url = test_config.get("api_urls.rag_api")

        query_payload = {
            "query": "What is Syntheverse?",
            "top_k": 3,
            "llm_model": "ollama"
        }

        start_time = time.time()

        try:
            response = requests.post(
                f"{rag_api_url}/query",
                json=query_payload,
                timeout=30  # 30 second timeout
            )

            response_time = time.time() - start_time

            self.assertEqual(response.status_code, 200)
            self.assertLess(response_time, 25.0, f"Query too slow: {response_time:.2f}s")

            result = response.json()
            answer_length = len(result.get("answer", ""))

            self.assertGreater(answer_length, 0, "Query returned empty answer")

            self.log_info(f"✅ Query completed in {response_time:.2f}s, answer length: {answer_length}")
            self.add_metric("simple_query_time", response_time)
            self.add_metric("simple_query_answer_length", answer_length)

        except requests.exceptions.Timeout:
            response_time = time.time() - start_time
            self.fail(f"Query timed out after {response_time:.2f}s")

    def test_timeout_handling(self):
        """Test timeout handling with slow/complex queries"""
        self.log_info("Testing timeout handling")

        import requests
        rag_api_url = test_config.get("api_urls.rag_api")

        # Test with a more complex query that might take longer
        complex_query = """
        Explain the relationship between hydrogen holography, fractal intelligence,
        and the Syntheverse PoC protocol in detail, including how these concepts
        interact within the blockchain ecosystem and what implications this has
        for decentralized scientific validation.
        """

        query_payload = {
            "query": complex_query,
            "top_k": 5,
            "llm_model": "ollama"
        }

        start_time = time.time()

        try:
            response = requests.post(
                f"{rag_api_url}/query",
                json=query_payload,
                timeout=60  # Allow up to 60 seconds for complex queries
            )

            response_time = time.time() - start_time

            # Accept both success and timeout scenarios
            if response.status_code == 200:
                result = response.json()
                answer_length = len(result.get("answer", ""))

                self.log_info(f"✅ Complex query completed in {response_time:.2f}s")
                self.add_metric("complex_query_time", response_time)
                self.add_metric("complex_query_answer_length", answer_length)
                self.add_metric("complex_query_success", True)

            else:
                self.log_info(f"⚠️  Complex query returned status {response.status_code} after {response_time:.2f}s")
                self.add_metric("complex_query_timeout", True)
                self.add_metric("complex_query_response_time", response_time)

        except requests.exceptions.Timeout:
            response_time = time.time() - start_time
            self.log_info(f"⚠️  Complex query timed out after {response_time:.2f}s (expected for slow queries)")
            self.add_metric("complex_query_timeout", True)
            self.add_metric("complex_query_timeout_time", response_time)

        except Exception as e:
            response_time = time.time() - start_time
            self.log_error(f"Complex query failed after {response_time:.2f}s: {e}")
            self.add_metric("complex_query_error", True)

    def test_concurrent_request_handling(self):
        """Test how the API handles concurrent requests"""
        self.log_info("Testing concurrent request handling")

        import requests
        import threading
        import queue

        rag_api_url = test_config.get("api_urls.rag_api")
        results_queue = queue.Queue()

        def make_request(request_id):
            """Make a single request and record results"""
            try:
                start_time = time.time()
                response = requests.post(
                    f"{rag_api_url}/query",
                    json={
                        "query": f"What is request {request_id} about?",
                        "top_k": 2,
                        "llm_model": "ollama"
                    },
                    timeout=45
                )
                response_time = time.time() - start_time

                results_queue.put({
                    "request_id": request_id,
                    "success": response.status_code == 200,
                    "response_time": response_time,
                    "status_code": response.status_code
                })

            except Exception as e:
                results_queue.put({
                    "request_id": request_id,
                    "success": False,
                    "error": str(e),
                    "response_time": time.time() - start_time
                })

        # Make 3 concurrent requests
        threads = []
        for i in range(3):
            thread = threading.Thread(target=make_request, args=(i+1,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=60)

        # Collect results
        results = []
        while not results_queue.empty():
            results.append(results_queue.get())

        # Analyze results
        successful_requests = sum(1 for r in results if r["success"])
        avg_response_time = sum(r["response_time"] for r in results) / len(results)

        self.log_info(f"✅ Concurrent requests: {successful_requests}/{len(results)} successful")
        self.log_info(f"Average response time: {avg_response_time:.2f}s")

        # At least some requests should succeed
        self.assertGreater(successful_requests, 0, "No concurrent requests succeeded")

        self.add_metric("concurrent_requests_successful", successful_requests)
        self.add_metric("concurrent_requests_total", len(results))
        self.add_metric("concurrent_avg_response_time", avg_response_time)

    def test_rate_limiting_detection(self):
        """Test detection of rate limiting"""
        self.log_info("Testing rate limiting detection")

        import requests
        import time

        rag_api_url = test_config.get("api_urls.rag_api")

        # Make multiple rapid requests
        responses = []

        for i in range(5):
            try:
                response = requests.post(
                    f"{rag_api_url}/query",
                    json={
                        "query": f"Rate limit test query {i+1}",
                        "top_k": 1,
                        "llm_model": "ollama"
                    },
                    timeout=10
                )
                responses.append(response.status_code)

                # Small delay between requests
                time.sleep(0.5)

            except requests.exceptions.Timeout:
                responses.append("timeout")
            except Exception as e:
                responses.append("error")

        # Check for rate limiting indicators
        rate_limited_responses = sum(1 for r in responses if r in [429, "timeout"])

        if rate_limited_responses > 0:
            self.log_info(f"⚠️  Detected {rate_limited_responses} rate limited requests")
            self.add_metric("rate_limiting_detected", True)
            self.add_metric("rate_limited_count", rate_limited_responses)
        else:
            self.log_info("✅ No rate limiting detected in test sequence")
            self.add_metric("rate_limiting_detected", False)

    def test_error_recovery(self):
        """Test error recovery and resilience"""
        self.log_info("Testing error recovery")

        import requests

        rag_api_url = test_config.get("api_urls.rag_api")

        # Test with invalid request first
        try:
            invalid_response = requests.post(
                f"{rag_api_url}/query",
                json={"invalid": "payload"},
                timeout=5
            )
            # Invalid request should be handled gracefully
            self.assertIn(invalid_response.status_code, [400, 422, 500])
            self.log_info("✅ Invalid request handled gracefully")

        except Exception as e:
            self.log_warning(f"Invalid request error handling: {e}")

        # Test that subsequent valid requests still work
        try:
            valid_response = requests.post(
                f"{rag_api_url}/query",
                json={
                    "query": "Test recovery query",
                    "top_k": 1,
                    "llm_model": "ollama"
                },
                timeout=15
            )

            if valid_response.status_code == 200:
                self.log_info("✅ API recovered from invalid request")
                self.add_metric("error_recovery_success", True)
            else:
                self.log_warning(f"⚠️  API did not recover properly: {valid_response.status_code}")

        except Exception as e:
            self.fail(f"Recovery test failed: {e}")


def run_timeout_tests():
    """Run timeout tests with framework"""
    TestUtils.print_test_header(
        "RAG API Timeout & Performance Test Suite",
        "Testing response times, timeout handling, and performance metrics"
    )

    import unittest
    suite = unittest.TestLoader().loadTestsFromTestCase(TestRAGTimeout)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    unittest.main()

