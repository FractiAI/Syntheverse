#!/usr/bin/env python3
"""
Performance Test Suite
Tests system performance, scalability, and resource usage
"""

import sys
import os
import time
import threading
import statistics
from pathlib import Path

# Add test framework to path
test_dir = Path(__file__).parent
sys.path.insert(0, str(test_dir))

from test_framework import SyntheverseTestCase, TestUtils, test_config, TestFixtures

class TestPerformance(SyntheverseTestCase):
    """Test system performance and scalability"""

    def get_category(self) -> str:
        """Return test category for reporting"""
        return "performance"

    def setUp(self):
        """Set up performance tests"""
        super().setUp()

        # Check service availability
        self.services_available = {}
        for service_name, url in test_config.get("api_urls", {}).items():
            if url and service_name in ["poc_api", "rag_api"]:
                healthy, _ = TestUtils.check_service_health(url, timeout=5)
                self.services_available[service_name] = healthy

    def test_api_response_times(self):
        """Test API response times under normal load"""
        self.log_info("Testing API response times")

        if not any(self.services_available.values()):
            self.skipTest("No API services available for performance testing")

        import requests

        # Test endpoints and their expected performance thresholds
        test_endpoints = {
            "poc_api": [
                ("/health", "health_check_max_time"),
                ("/api/archive/statistics", "api_call_max_time"),
                ("/api/sandbox-map", "api_call_max_time"),
            ],
            "rag_api": [
                ("/health", "health_check_max_time"),
            ]
        }

        total_tests = 0
        passed_tests = 0
        response_times = []

        for service_name, endpoints in test_endpoints.items():
            if not self.services_available.get(service_name, False):
                continue

            base_url = test_config.get(f"api_urls.{service_name}")

            for endpoint, threshold_key in endpoints:
                total_tests += 1
                full_url = f"{base_url}{endpoint}"

                try:
                    # Make multiple requests to get average
                    times = []
                    for _ in range(3):  # 3 requests for averaging
                        start_time = time.time()
                        response = requests.get(full_url, timeout=30)
                        end_time = time.time()

                        if response.status_code == 200:
                            times.append(end_time - start_time)
                            time.sleep(0.1)  # Brief pause between requests
                        else:
                            self.log_warning(f"⚠️  {endpoint} returned status {response.status_code}")
                            break

                    if times:
                        avg_time = statistics.mean(times)
                        max_time = max(times)
                        min_time = min(times)

                        # Check against performance threshold
                        threshold = test_config.get(f"performance_thresholds.{threshold_key}", 30.0)

                        response_times.append(avg_time)

                        if avg_time <= threshold:
                            passed_tests += 1
                            self.log_info(f"✅ {endpoint}: {avg_time:.3f}s (threshold: {threshold:.1f}s)")
                        else:
                            self.log_warning(f"⚠️  {endpoint}: {avg_time:.3f}s exceeds threshold {threshold:.1f}s")

                        self.add_metric(f"{endpoint.replace('/', '_')}_avg_time", avg_time)
                        self.add_metric(f"{endpoint.replace('/', '_')}_max_time", max_time)
                        self.add_metric(f"{endpoint.replace('/', '_')}_min_time", min_time)

                except Exception as e:
                    self.log_warning(f"⚠️  Performance test failed for {endpoint}: {e}")

        if response_times:
            overall_avg = statistics.mean(response_times)
            overall_p95 = statistics.quantiles(response_times, n=20)[18]  # 95th percentile

            performance_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

            self.log_info(f"✅ API Performance: {performance_rate:.1f}% within thresholds")
            self.log_info(f"Average response time: {overall_avg:.3f}s")
            self.log_info(f"95th percentile: {overall_p95:.3f}s")

            self.add_metric("api_performance_rate", performance_rate)
            self.add_metric("overall_avg_response_time", overall_avg)
            self.add_metric("overall_p95_response_time", overall_p95)

    def test_concurrent_api_load(self):
        """Test API performance under concurrent load"""
        self.log_info("Testing concurrent API load")

        if not self.services_available.get("poc_api", False):
            self.skipTest("PoC API not available for concurrent load testing")

        import requests

        poc_api_url = test_config.get("api_urls.poc_api")
        num_threads = 10
        requests_per_thread = 5

        results = []
        errors = []

        def make_requests(thread_id):
            """Make multiple requests from a single thread"""
            thread_results = []

            for i in range(requests_per_thread):
                try:
                    start_time = time.time()
                    response = requests.get(f"{poc_api_url}/health", timeout=10)
                    end_time = time.time()

                    if response.status_code == 200:
                        response_time = end_time - start_time
                        thread_results.append({
                            "thread": thread_id,
                            "request": i,
                            "response_time": response_time,
                            "status": response.status_code
                        })
                    else:
                        errors.append({
                            "thread": thread_id,
                            "request": i,
                            "error": f"Status {response.status_code}"
                        })

                except Exception as e:
                    errors.append({
                        "thread": thread_id,
                        "request": i,
                        "error": str(e)
                    })

            results.extend(thread_results)

        # Launch concurrent threads
        threads = []
        start_time = time.time()

        for thread_id in range(num_threads):
            thread = threading.Thread(target=make_requests, args=(thread_id,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=30)

        total_time = time.time() - start_time

        # Analyze results
        successful_requests = len(results)
        total_expected = num_threads * requests_per_thread
        success_rate = (successful_requests / total_expected * 100)

        if results:
            response_times = [r["response_time"] for r in results]
            avg_response_time = statistics.mean(response_times)
            max_response_time = max(response_times)
            min_response_time = min(response_times)
            p95_response_time = statistics.quantiles(response_times, n=20)[18]

            # Calculate throughput
            throughput = successful_requests / total_time

            self.log_info(f"✅ Concurrent load test completed:")
            self.log_info(f"  Success rate: {success_rate:.1f}% ({successful_requests}/{total_expected})")
            self.log_info(f"  Average response time: {avg_response_time:.3f}s")
            self.log_info(f"  95th percentile: {p95_response_time:.3f}s")
            self.log_info(f"  Max response time: {max_response_time:.3f}s")
            self.log_info(f"  Throughput: {throughput:.2f} requests/second")
            self.log_info(f"  Total test time: {total_time:.2f}s")

            self.add_metric("concurrent_success_rate", success_rate)
            self.add_metric("concurrent_avg_response_time", avg_response_time)
            self.add_metric("concurrent_p95_response_time", p95_response_time)
            self.add_metric("concurrent_max_response_time", max_response_time)
            self.add_metric("concurrent_throughput", throughput)
            self.add_metric("concurrent_total_time", total_time)

        if errors:
            self.log_warning(f"⚠️  {len(errors)} requests failed during concurrent load test")
            self.add_metric("concurrent_errors", len(errors))

    def test_memory_usage_patterns(self):
        """Test memory usage patterns during operations"""
        self.log_info("Testing memory usage patterns")

        try:
            import psutil
            import os

            process = psutil.Process(os.getpid())

            # Get initial memory usage
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            self.log_info(f"Initial memory usage: {initial_memory:.2f} MB")
            self.add_metric("initial_memory_mb", initial_memory)

            # Perform memory-intensive operations
            memory_snapshots = []

            # Create large data structures
            large_data = []
            for i in range(1000):
                large_data.append({
                    "id": f"memory-test-{i}",
                    "content": "Large content string " * 100,  # ~2KB per item
                    "metadata": {"index": i, "size": "large"}
                })

                if i % 100 == 0:  # Take memory snapshot every 100 items
                    current_memory = process.memory_info().rss / 1024 / 1024
                    memory_snapshots.append(current_memory)

            peak_memory = max(memory_snapshots) if memory_snapshots else initial_memory
            final_memory = process.memory_info().rss / 1024 / 1024
            memory_growth = final_memory - initial_memory

            self.log_info(f"Peak memory usage: {peak_memory:.2f} MB")
            self.log_info(f"Final memory usage: {final_memory:.2f} MB")
            self.log_info(f"Memory growth: {memory_growth:.2f} MB")

            # Memory growth should be reasonable (< 100MB for this test)
            if memory_growth < 100:
                self.log_info("✅ Memory usage within acceptable limits")
                self.add_metric("memory_usage_acceptable", True)
            else:
                self.log_warning(f"⚠️  Excessive memory growth: {memory_growth:.2f} MB")
                self.add_metric("memory_usage_acceptable", False)

            self.add_metric("peak_memory_mb", peak_memory)
            self.add_metric("final_memory_mb", final_memory)
            self.add_metric("memory_growth_mb", memory_growth)

            # Clean up to free memory
            del large_data

        except ImportError:
            self.skipTest("psutil not available for memory testing")
        except Exception as e:
            self.fail(f"Memory usage test failed: {e}")

    def test_file_operation_performance(self):
        """Test file operation performance"""
        self.log_info("Testing file operation performance")

        import tempfile
        import json

        # Create temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Test data sizes
            test_sizes = [100, 1000, 10000]  # Number of records

            for size in test_sizes:
                # Create test data
                test_data = {
                    "records": [
                        {
                            "id": f"perf-test-{i}",
                            "content": f"Content for record {i}",
                            "metadata": {"size": size, "index": i}
                        }
                        for i in range(size)
                    ]
                }

                file_path = temp_path / f"perf_test_{size}.json"

                # Test write performance
                write_start = time.time()
                with open(file_path, 'w') as f:
                    json.dump(test_data, f, indent=2)
                write_time = time.time() - write_start

                file_size = file_path.stat().st_size

                # Test read performance
                read_start = time.time()
                with open(file_path, 'r') as f:
                    loaded_data = json.load(f)
                read_time = time.time() - read_start

                # Verify data integrity
                self.assertEqual(len(loaded_data["records"]), size, f"Data size mismatch for {size} records")

                # Calculate performance metrics
                write_speed = file_size / write_time / 1024 / 1024  # MB/s
                read_speed = file_size / read_time / 1024 / 1024    # MB/s

                self.log_info(f"✅ Size {size}: Write {write_speed:.2f} MB/s, Read {read_speed:.2f} MB/s")

                self.add_metric(f"file_write_speed_{size}", write_speed)
                self.add_metric(f"file_read_speed_{size}", read_speed)
                self.add_metric(f"file_size_{size}", file_size)

    def test_cpu_usage_during_operations(self):
        """Test CPU usage during intensive operations"""
        self.log_info("Testing CPU usage during operations")

        try:
            import psutil
            import os

            process = psutil.Process(os.getpid())

            # Get initial CPU usage
            initial_cpu = process.cpu_percent(interval=0.1)

            # Perform CPU-intensive operations
            cpu_samples = []

            def cpu_intensive_task():
                """CPU-intensive computation"""
                result = 0
                for i in range(1000000):  # 1 million iterations
                    result += i ** 2
                return result

            # Run multiple CPU-intensive tasks
            for i in range(5):
                start_time = time.time()
                cpu_intensive_task()
                end_time = time.time()

                # Sample CPU usage
                cpu_percent = process.cpu_percent(interval=0.1)
                cpu_samples.append(cpu_percent)

                self.log_info(f"Task {i+1}: CPU usage {cpu_percent:.1f}%")

            if cpu_samples:
                avg_cpu = statistics.mean(cpu_samples)
                max_cpu = max(cpu_samples)
                min_cpu = min(cpu_samples)

                self.log_info(f"✅ CPU usage stats: Avg {avg_cpu:.1f}%, Max {max_cpu:.1f}%, Min {min_cpu:.1f}%")

                # CPU usage should be reasonable (not constantly 100%)
                if avg_cpu < 90:
                    self.log_info("✅ CPU usage within acceptable limits")
                    self.add_metric("cpu_usage_acceptable", True)
                else:
                    self.log_warning(f"⚠️  High CPU usage detected: {avg_cpu:.1f}%")
                    self.add_metric("cpu_usage_acceptable", False)

                self.add_metric("avg_cpu_usage", avg_cpu)
                self.add_metric("max_cpu_usage", max_cpu)
                self.add_metric("min_cpu_usage", min_cpu)

        except ImportError:
            self.skipTest("psutil not available for CPU testing")
        except Exception as e:
            self.fail(f"CPU usage test failed: {e}")

    def test_scalability_with_data_size(self):
        """Test how performance scales with data size"""
        self.log_info("Testing scalability with data size")

        # Test data processing with different sizes
        test_sizes = [10, 100, 1000]

        processing_times = []

        for size in test_sizes:
            # Create test data
            test_data = [
                {
                    "id": f"scale-test-{i}",
                    "content": f"Content {i} with some processing",
                    "metadata": {"size": size, "index": i}
                }
                for i in range(size)
            ]

            # Measure processing time
            start_time = time.time()

            # Simulate data processing
            processed_count = 0
            total_content_length = 0

            for item in test_data:
                # Simulate processing: count words, calculate hash, etc.
                processed_count += 1
                total_content_length += len(item["content"])

                # Add some computational work
                hash_value = hash(item["content"])
                item["processed_hash"] = hash_value

            processing_time = time.time() - start_time

            processing_times.append(processing_time)

            # Calculate metrics
            items_per_second = size / processing_time if processing_time > 0 else 0
            avg_content_length = total_content_length / size

            self.log_info(f"✅ Size {size}: {processing_time:.3f}s ({items_per_second:.1f} items/sec)")

            self.add_metric(f"processing_time_{size}", processing_time)
            self.add_metric(f"items_per_second_{size}", items_per_second)
            self.add_metric(f"avg_content_length_{size}", avg_content_length)

        # Analyze scalability (should not have exponential growth)
        if len(processing_times) >= 2:
            time_ratio_10_to_100 = processing_times[1] / processing_times[0] if processing_times[0] > 0 else 0
            time_ratio_100_to_1000 = processing_times[2] / processing_times[1] if len(processing_times) > 2 and processing_times[1] > 0 else 0

            self.log_info(f"Scalability ratios: 10→100: {time_ratio_10_to_100:.2f}x, 100→1000: {time_ratio_100_to_1000:.2f}x")

            # Scalability is good if ratios are reasonable (< 20x for 10x data increase)
            if time_ratio_10_to_100 < 20 and time_ratio_100_to_1000 < 20:
                self.log_info("✅ Scalability within acceptable limits")
                self.add_metric("scalability_acceptable", True)
            else:
                self.log_warning("⚠️  Poor scalability detected")
                self.add_metric("scalability_acceptable", False)

            self.add_metric("scalability_ratio_10_100", time_ratio_10_to_100)
            self.add_metric("scalability_ratio_100_1000", time_ratio_100_to_1000)


def run_performance_tests():
    """Run performance tests with framework"""
    TestUtils.print_test_header(
        "Performance Test Suite",
        "Testing system performance, scalability, and resource usage"
    )

    import unittest
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPerformance)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    import unittest
    unittest.main()
