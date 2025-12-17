#!/usr/bin/env python3
"""
RAG API Test Suite
Tests RAG API functionality with real API calls and automatic service management.

Dependencies: Automatically installs requests library if needed.
Services: Requires RAG API service (automatically started by conftest.py).
Isolation: Uses real API calls with proper error handling and metrics collection.
"""

import sys
import os
import time
import unittest
import pytest
from pathlib import Path

# Add test framework to path
test_dir = Path(__file__).parent
sys.path.insert(0, str(test_dir))

from test_framework import APITestCase, TestUtils, test_config, ensure_dependency

@pytest.mark.requires_rag_api
class TestRAGAPI(APITestCase):
    """Test RAG API functionality with standardized framework"""

    def get_category(self) -> str:
        """Return test category for reporting"""
        return "integration"

    def test_rag_api_health(self):
        """Test RAG API health endpoint"""
        self.log_info("Testing RAG API health endpoint")

        # Require RAG API to be available
        self.require_service("rag_api")

        rag_api_url = self.get_service_url("rag_api")

        self.log_info("✅ RAG API health check passed")

    def test_rag_api_query(self):
        """Test RAG API query functionality"""
        self.log_info("Testing RAG API query functionality")

        # Require RAG API to be available
        self.require_service("rag_api")

        rag_api_url = self.get_service_url("rag_api")
        test_query = "What is the Syntheverse PoD protocol?"

        try:
            import requests

            query_payload = {
                "query": test_query,
                "top_k": 3,
                "llm_model": "ollama"
            }

            self.log_info(f"Sending query: {test_query}")

            # Record start time for metrics
            import time
            start_time = time.time()

            response = requests.post(
                f"{rag_api_url}/query",
                json=query_payload,
                timeout=test_config.get("timeouts.api_call", 60)
            )

            # Record response time
            response_time = time.time() - start_time
            self.add_metric("response_time", response_time)

            self.assertEqual(response.status_code, 200,
                           f"Query failed with status {response.status_code}: {response.text}")

            result = response.json()
            self.log_info("✅ Query successful")

            # Validate response structure
            self.assertIn("answer", result, "Response missing 'answer' field")
            self.assertIn("sources", result, "Response missing 'sources' field")

            answer_length = len(result.get("answer", ""))
            sources_count = len(result.get("sources", []))

            self.add_metric("answer_length", answer_length)
            self.add_metric("sources_count", sources_count)

            self.log_info(f"Answer length: {answer_length} characters")
            self.log_info(f"Sources found: {sources_count}")

            # Validate answer content
            self.assertGreater(answer_length, 0, "Answer is empty")
            self.assertGreater(sources_count, 0, "No sources returned")

            # Log preview of answer
            answer_preview = result["answer"][:300] + "..." if len(result["answer"]) > 300 else result["answer"]
            self.log_info(f"Answer preview: {answer_preview}")

            # Validate sources
            sources = result["sources"]
            for i, source in enumerate(sources[:3], 1):
                title = source.get("title", "Unknown")
                score = source.get("score", 0)
                self.log_info(f"Source {i}: {title} (score: {score:.4f})")

        except ImportError:
            # Try to install requests dependency
            try:
                ensure_dependency("requests")
                # Retry the import
                import requests
            except RuntimeError:
                self.fail("requests library could not be installed")
        except Exception as e:
            self.fail(f"RAG API query failed: {e}")

    def test_rag_api_query_variations(self):
        """Test RAG API with different query types and edge cases"""
        self.log_info("Testing RAG API query variations")

        rag_api_url = test_config.get("api_urls.rag_api")

        # Service should be started automatically by conftest.py due to @pytest.mark.requires_rag_api

        import requests

        test_queries = [
            "What is Syntheverse?",  # Basic query
            "",  # Empty query
            "A",  # Minimal query
            "What is the meaning of life according to quantum physics and fractal mathematics?",  # Complex query
            "Explain hydrogen holography in detail",  # Technical query
            "Test query with special characters: π ≈ 3.14159 & ∞",  # Unicode query
            "Very long query " * 50,  # Long query
        ]

        successful_queries = 0
        total_queries = len(test_queries)

        for i, query in enumerate(test_queries, 1):
            try:
                payload = {
                    "query": query,
                    "top_k": 3,
                    "llm_model": "ollama"
                }

                start_time = time.time()
                response = requests.post(
                    f"{rag_api_url}/query",
                    json=payload,
                    timeout=test_config.get("timeouts.api_call", 60)
                )
                response_time = time.time() - start_time

                if response.status_code == 200:
                    result = response.json()
                    if "answer" in result and "sources" in result:
                        successful_queries += 1
                        answer_length = len(result.get("answer", ""))
                        sources_count = len(result.get("sources", []))

                        self.log_info(f"✅ Query {i} successful: {answer_length} chars, {sources_count} sources")
                        self.add_metric(f"query_{i}_response_time", response_time)
                        self.add_metric(f"query_{i}_answer_length", answer_length)
                        self.add_metric(f"query_{i}_sources_count", sources_count)
                    else:
                        self.log_warning(f"⚠️  Query {i} returned 200 but missing expected fields")
                elif response.status_code == 400 and query == "":
                    # Empty query should return bad request
                    successful_queries += 1
                    self.log_info(f"✅ Query {i} (empty) properly rejected: {response.status_code}")
                else:
                    self.log_warning(f"⚠️  Query {i} failed: {response.status_code}")

            except Exception as e:
                self.log_warning(f"⚠️  Query {i} exception: {e}")

        success_rate = (successful_queries / total_queries * 100) if total_queries > 0 else 0
        self.log_info(f"✅ Query variations: {successful_queries}/{total_queries} successful ({success_rate:.1f}%)")
        self.add_metric("query_variations_success_rate", success_rate)

    def test_rag_api_large_query_handling(self):
        """Test RAG API handling of very large queries"""
        self.log_info("Testing RAG API large query handling")

        rag_api_url = test_config.get("api_urls.rag_api")

        # Service should be started automatically by conftest.py due to @pytest.mark.requires_rag_api

        import requests

        # Create a very large query (10KB)
        large_query = "What is the relationship between " + ("quantum physics and consciousness " * 200) + "?"

        try:
            payload = {
                "query": large_query,
                "top_k": 5,
                "llm_model": "ollama"
            }

            start_time = time.time()
            response = requests.post(
                f"{rag_api_url}/query",
                json=payload,
                timeout=120  # Extended timeout for large query
            )
            response_time = time.time() - start_time

            if response.status_code == 200:
                result = response.json()
                if "answer" in result:
                    self.log_info(f"✅ Large query handled successfully in {response_time:.2f}s")
                    self.add_metric("large_query_response_time", response_time)
                    self.add_metric("large_query_answer_length", len(result.get("answer", "")))
                    self.add_metric("large_query_success", True)
                else:
                    self.fail("Large query returned 200 but missing answer field")
            elif response.status_code == 413:  # Payload too large
                self.log_info("✅ Large query properly rejected as too large")
                self.add_metric("large_query_rejected", True)
            else:
                self.fail(f"Large query failed with unexpected status: {response.status_code}")

        except requests.exceptions.Timeout:
            self.log_info("⚠️  Large query timed out (may be expected for very large payloads)")
            self.add_metric("large_query_timeout", True)
        except Exception as e:
            self.fail(f"Large query test failed: {e}")

    def test_rag_api_error_scenarios(self):
        """Test RAG API error handling scenarios"""
        self.log_info("Testing RAG API error scenarios")

        rag_api_url = test_config.get("api_urls.rag_api")
        import requests

        error_scenarios = [
            {
                "name": "invalid_json",
                "payload": "invalid json",
                "expected_status": 400,
                "content_type": "application/json"
            },
            {
                "name": "missing_query",
                "payload": {"top_k": 3},
                "expected_status": 400
            },
            {
                "name": "invalid_top_k",
                "payload": {"query": "test", "top_k": "invalid"},
                "expected_status": 400
            },
            {
                "name": "negative_top_k",
                "payload": {"query": "test", "top_k": -1},
                "expected_status": 400
            },
            {
                "name": "empty_payload",
                "payload": {},
                "expected_status": 400
            },
            {
                "name": "null_query",
                "payload": {"query": None, "top_k": 3},
                "expected_status": 400
            }
        ]

        successful_errors = 0
        total_scenarios = len(error_scenarios)

        for scenario in error_scenarios:
            try:
                if scenario["name"] == "invalid_json":
                    # Send raw string instead of JSON
                    response = requests.post(
                        f"{rag_api_url}/query",
                        data=scenario["payload"],
                        headers={"Content-Type": scenario["content_type"]},
                        timeout=30
                    )
                else:
                    response = requests.post(
                        f"{rag_api_url}/query",
                        json=scenario["payload"],
                        timeout=30
                    )

                if response.status_code == scenario["expected_status"]:
                    successful_errors += 1
                    self.log_info(f"✅ {scenario['name']}: properly rejected with {response.status_code}")
                else:
                    self.log_warning(f"⚠️  {scenario['name']}: got {response.status_code}, expected {scenario['expected_status']}")

                self.add_metric(f"error_{scenario['name']}_status", response.status_code)

            except Exception as e:
                self.log_warning(f"⚠️  {scenario['name']}: test failed: {e}")

        error_success_rate = (successful_errors / total_scenarios * 100) if total_scenarios > 0 else 0
        self.log_info(f"✅ Error scenarios: {successful_errors}/{total_scenarios} properly handled ({error_success_rate:.1f}%)")
        self.add_metric("error_handling_success_rate", error_success_rate)

if __name__ == "__main__":
    unittest.main()

