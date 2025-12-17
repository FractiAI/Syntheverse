#!/usr/bin/env python3
"""
Syntheverse Test Runner
Advanced Python test orchestrator with discovery, execution, and reporting
"""

import sys
import os
import subprocess
import time
import argparse
import hashlib
import pickle
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Set
import json
import html

class TestRunner:
    def __init__(self, test_dir: Path, results_dir: Path = None):
        self.test_dir = test_dir
        self.project_root = test_dir.parent
        self.results_dir = results_dir or test_dir / "results"
        self.results_dir.mkdir(exist_ok=True)

        # Test results tracking
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.test_results = []

        # Filtering and caching
        self.include_filters: Set[str] = set()
        self.exclude_filters: Set[str] = set()
        self.include_markers: Set[str] = set()
        self.exclude_markers: Set[str] = set()
        self.cache_enabled = True
        self.cache_dir = self.results_dir / "cache"
        self.cache_dir.mkdir(exist_ok=True)

        # HTML reporting
        self.html_reports_enabled = True

    def print_header(self, title: str):
        print(f"\n{'='*50}")
        print(f"{title}")
        print(f"{'='*50}")

    def print_status(self, message: str, status: str = "INFO"):
        colors = {
            "✅": "\033[0;32m",  # Green
            "❌": "\033[0;31m",  # Red
            "⚠️": "\033[1;33m",   # Yellow
            "ℹ️": "\033[0;34m",   # Blue
            "🚀": "\033[0;35m",  # Purple
        }
        color = colors.get(status, "\033[0;34m")
        reset = "\033[0m"
        print(f"{color}{status} {message}{reset}")

    def discover_tests(self, pattern: str = "test_*.py") -> List[Path]:
        """Discover test files matching the pattern with filtering"""
        all_files = list(self.test_dir.glob(pattern))

        # Apply file filters
        filtered_files = []
        for test_file in all_files:
            file_name = test_file.stem

            # Check include filters
            if self.include_filters and not any(f in file_name for f in self.include_filters):
                continue

            # Check exclude filters
            if self.exclude_filters and any(f in file_name for f in self.exclude_filters):
                continue

            filtered_files.append(test_file)

        return filtered_files

    def set_filters(self, include: Optional[List[str]] = None, exclude: Optional[List[str]] = None,
                   include_markers: Optional[List[str]] = None, exclude_markers: Optional[List[str]] = None):
        """Set test filtering options"""
        if include:
            self.include_filters.update(include)
        if exclude:
            self.exclude_filters.update(exclude)
        if include_markers:
            self.include_markers.update(include_markers)
        if exclude_markers:
            self.exclude_markers.update(exclude_markers)

    def _get_cache_key(self, test_file: Path) -> str:
        """Generate cache key for test file based on file hash"""
        if not test_file.exists():
            return ""

        # Get file modification time and content hash
        stat = test_file.stat()
        content = test_file.read_text()
        cache_data = f"{test_file}:{stat.st_mtime}:{hashlib.md5(content.encode()).hexdigest()}"
        return hashlib.md5(cache_data.encode()).hexdigest()

    def _get_cached_result(self, cache_key: str) -> Optional[Dict]:
        """Get cached test result if available and valid"""
        if not self.cache_enabled:
            return None

        cache_file = self.cache_dir / f"{cache_key}.pkl"
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    cached_data = pickle.load(f)
                    # Check if cache is still valid (within last hour)
                    if time.time() - cached_data.get('timestamp', 0) < 3600:
                        return cached_data['result']
            except Exception:
                # Cache corrupted, ignore
                pass
        return None

    def _cache_result(self, cache_key: str, result: Dict):
        """Cache test result"""
        if not self.cache_enabled:
            return

        cache_file = self.cache_dir / f"{cache_key}.pkl"
        cache_data = {
            'timestamp': time.time(),
            'result': result
        }

        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
        except Exception:
            # Ignore caching errors
            pass

    def run_test_file(self, test_file: Path, timeout: int = 300, use_cache: bool = True) -> Tuple[bool, float, str]:
        """Run a single test file and return (success, duration, output) with caching support"""
        test_name = test_file.stem

        # Check cache first
        if use_cache and self.cache_enabled:
            cache_key = self._get_cache_key(test_file)
            cached_result = self._get_cached_result(cache_key)
            if cached_result:
                self.print_status(f"{test_name} (cached)", "ℹ️")
                return cached_result['success'], cached_result['duration'], cached_result['output']

        self.print_status(f"Running {test_name}...", "🚀")

        start_time = time.time()

        try:
            # Change to project root for proper imports
            os.chdir(self.project_root)

            # Run the test with timeout and enhanced error handling
            result = subprocess.run(
                [sys.executable, str(test_file)],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.project_root,
                env={**os.environ, 'PYTHONPATH': str(self.project_root)}
            )

            duration = time.time() - start_time

            # Save detailed output to file
            timestamp = int(time.time())
            output_file = self.results_dir / f"{test_name}_{timestamp}.log"
            with open(output_file, 'w') as f:
                f.write(f"Test: {test_name}\n")
                f.write(f"Timestamp: {timestamp}\n")
                f.write(f"Duration: {duration:.2f}s\n")
                f.write(f"Exit Code: {result.returncode}\n")
                f.write(f"Timeout: {timeout}s\n")
                f.write(f"{'='*50}\n")
                f.write("STDOUT:\n")
                f.write(result.stdout)
                f.write(f"{'='*50}\n")
                f.write("STDERR:\n")
                f.write(result.stderr)

            success = result.returncode == 0
            output = result.stdout + result.stderr

            # Cache the result
            if use_cache and self.cache_enabled and cache_key:
                result_data = {
                    'success': success,
                    'duration': duration,
                    'output': output,
                    'timestamp': timestamp
                }
                self._cache_result(cache_key, result_data)

            if success:
                self.print_status(f"{test_name} PASSED ({duration:.1f}s)", "✅")
            else:
                self.print_status(f"{test_name} FAILED ({duration:.1f}s)", "❌")
                self.print_status(f"See details: {output_file}")

            return success, duration, output

        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            error_msg = f"Test timed out after {timeout}s"
            self.print_status(f"{test_name} TIMEOUT ({duration:.1f}s)", "❌")

            # Save timeout information
            timestamp = int(time.time())
            output_file = self.results_dir / f"{test_name}_{timestamp}_timeout.log"
            with open(output_file, 'w') as f:
                f.write(f"Test: {test_name}\n")
                f.write(f"Error: {error_msg}\n")
                f.write(f"Duration: {duration:.2f}s\n")
                f.write(f"Timeout: {timeout}s\n")

            return False, duration, error_msg

        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Test execution error: {e}"
            self.print_status(f"{test_name} ERROR ({duration:.1f}s): {e}", "❌")

            # Save error information
            timestamp = int(time.time())
            output_file = self.results_dir / f"{test_name}_{timestamp}_error.log"
            with open(output_file, 'w') as f:
                f.write(f"Test: {test_name}\n")
                f.write(f"Error: {error_msg}\n")
                f.write(f"Duration: {duration:.2f}s\n")

            return False, duration, error_msg

    def run_test_category(self, category: str, test_files: List[str]):
        """Run a category of tests"""
        self.print_header(f"🧪 RUNNING {category.upper()} TESTS")

        for test_name in test_files:
            test_file = self.test_dir / f"{test_name}.py"
            if test_file.exists():
                success, duration, output = self.run_test_file(test_file)

                self.test_results.append({
                    "name": test_name,
                    "category": category,
                    "success": success,
                    "duration": duration,
                    "output": output[:500]  # Truncate for summary
                })

                if success:
                    self.passed += 1
                else:
                    self.failed += 1
            else:
                self.print_status(f"Test file not found: {test_name}", "⚠️")
                self.skipped += 1

    def run_unit_tests(self):
        """Run unit tests - individual component tests"""
        # Load test categories from config if available
        try:
            from test_framework import test_config
            unit_tests = test_config.get("test_categories.unit", [
                "test_submission",
                "test_rag_timeout"
            ])
        except ImportError:
            unit_tests = [
                "test_submission",
                "test_rag_timeout"
            ]
        self.run_test_category("UNIT", unit_tests)

    def run_integration_tests(self):
        """Run integration tests - API and service integration"""
        try:
            from test_framework import test_config
            integration_tests = test_config.get("test_categories.integration", [
                "test_rag_api",
                "test_rag_pod_query"
            ])
        except ImportError:
            integration_tests = [
                "test_rag_api",
                "test_rag_pod_query"
            ]
        self.run_test_category("INTEGRATION", integration_tests)

    def run_end_to_end_tests(self):
        """Run end-to-end tests - complete workflow tests"""
        try:
            from test_framework import test_config
            e2e_tests = test_config.get("test_categories.end_to_end", [
                "test_submission_flow",
                "test_full_submission_flow"
            ])
        except ImportError:
            e2e_tests = [
                "test_submission_flow",
                "test_full_submission_flow"
            ]
        self.run_test_category("END-TO-END", e2e_tests)

    def run_all_tests(self):
        """Run all test categories"""
        self.print_header("🚀 RUNNING ALL TESTS")

        self.run_unit_tests()
        self.run_integration_tests()
        self.run_end_to_end_tests()

    def generate_report(self):
        """Generate a summary report with optional HTML output"""
        self.print_header("📊 TEST REPORT")

        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Skipped: {self.skipped}")
        total = self.passed + self.failed + self.skipped
        print(f"Total: {total}")

        if total > 0:
            success_rate = (self.passed / total) * 100
            print(f"Success Rate: {success_rate:.1f}%")

            # Calculate additional metrics
            avg_duration = sum(r.get('duration', 0) for r in self.test_results) / len(self.test_results)
            total_duration = sum(r.get('duration', 0) for r in self.test_results)

            print(f"Average Duration: {avg_duration:.2f}s")
            print(f"Total Duration: {total_duration:.2f}s")

            timestamp = int(time.time())

            # Save detailed JSON report
            report_file = self.results_dir / f"test_report_{timestamp}.json"
            report_data = {
                "summary": {
                    "passed": self.passed,
                    "failed": self.failed,
                    "skipped": self.skipped,
                    "total": total,
                    "success_rate": success_rate,
                    "avg_duration": avg_duration,
                    "total_duration": total_duration,
                    "timestamp": timestamp
                },
                "results": self.test_results,
                "filters": {
                    "include": list(self.include_filters),
                    "exclude": list(self.exclude_filters),
                    "include_markers": list(self.include_markers),
                    "exclude_markers": list(self.exclude_markers)
                }
            }

            with open(report_file, 'w') as f:
                json.dump(report_data, f, indent=2)

            self.print_status(f"JSON report saved: {report_file}", "ℹ️")

            # Generate HTML report if enabled
            if self.html_reports_enabled:
                html_file = self.generate_html_report(report_data, timestamp)
                self.print_status(f"HTML report saved: {html_file}", "ℹ️")

        return self.failed == 0

    def generate_html_report(self, report_data: Dict, timestamp: int) -> Path:
        """Generate HTML report from test data"""
        html_file = self.results_dir / f"test_report_{timestamp}.html"

        summary = report_data['summary']
        results = report_data['results']

        # Calculate metrics
        failed_tests = [r for r in results if not r.get('success', False)]
        passed_tests = [r for r in results if r.get('success', False)]

        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Syntheverse Test Report - {timestamp}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .header {{ background-color: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
        .summary {{ display: flex; gap: 20px; margin: 20px 0; }}
        .metric {{ background-color: white; padding: 15px; border-radius: 5px; flex: 1; text-align: center; }}
        .passed {{ border-left: 5px solid #27ae60; }}
        .failed {{ border-left: 5px solid #e74c3c; }}
        .skipped {{ border-left: 5px solid #f39c12; }}
        .tests {{ margin-top: 20px; }}
        .test-item {{ background-color: white; margin: 10px 0; padding: 15px; border-radius: 5px; }}
        .test-passed {{ border-left: 5px solid #27ae60; }}
        .test-failed {{ border-left: 5px solid #e74c3c; }}
        .test-details {{ margin-top: 10px; font-size: 0.9em; color: #666; }}
        .filters {{ background-color: #ecf0f1; padding: 15px; border-radius: 5px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Syntheverse Test Report</h1>
        <p>Generated: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))}</p>
    </div>

    <div class="summary">
        <div class="metric passed">
            <h2>{summary['passed']}</h2>
            <p>Passed</p>
        </div>
        <div class="metric failed">
            <h2>{summary['failed']}</h2>
            <p>Failed</p>
        </div>
        <div class="metric skipped">
            <h2>{summary['skipped']}</h2>
            <p>Skipped</p>
        </div>
        <div class="metric">
            <h2>{summary['success_rate']:.1f}%</h2>
            <p>Success Rate</p>
        </div>
    </div>

    <div class="filters">
        <h3>Active Filters</h3>
        <p><strong>Include:</strong> {', '.join(report_data['filters']['include']) or 'None'}</p>
        <p><strong>Exclude:</strong> {', '.join(report_data['filters']['exclude']) or 'None'}</p>
        <p><strong>Include Markers:</strong> {', '.join(report_data['filters']['include_markers']) or 'None'}</p>
        <p><strong>Exclude Markers:</strong> {', '.join(report_data['filters']['exclude_markers']) or 'None'}</p>
    </div>

    <div class="tests">
        <h2>Test Results ({len(results)} total)</h2>

        {"".join(f'''
        <div class="test-item test-{'passed' if r.get('success', False) else 'failed'}">
            <h3>{r['name']} - {'✅ PASSED' if r.get('success', False) else '❌ FAILED'}</h3>
            <div class="test-details">
                <p><strong>Category:</strong> {r.get('category', 'Unknown')}</p>
                <p><strong>Duration:</strong> {r.get('duration', 0):.2f}s</p>
                {"<p><strong>Error:</strong> " + html.escape(str(r.get('error_message', ''))) + "</p>" if not r.get('success', False) and r.get('error_message') else ""}
            </div>
        </div>
        ''' for r in results)}
    </div>
</body>
</html>
"""

        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return html_file

    def clean_results(self):
        """Clean old test results"""
        self.print_status("Cleaning test results...", "🔧")

        for file in self.results_dir.glob("*"):
            if file.is_file():
                file.unlink()

        self.print_status("Test results cleaned", "✅")

def main():
    parser = argparse.ArgumentParser(description="Syntheverse Test Runner")
    parser.add_argument("--category", choices=["unit", "integration", "e2e", "all"],
                       default="all", help="Test category to run")
    parser.add_argument("--clean", action="store_true", help="Clean results before running")
    parser.add_argument("--timeout", type=int, default=300, help="Test timeout in seconds")
    parser.add_argument("--report-only", action="store_true", help="Generate report from existing results")

    # New filtering options
    parser.add_argument("--include", nargs="*", help="Include only tests containing these strings")
    parser.add_argument("--exclude", nargs="*", help="Exclude tests containing these strings")
    parser.add_argument("--include-markers", nargs="*", help="Include tests with these markers")
    parser.add_argument("--exclude-markers", nargs="*", help="Exclude tests with these markers")

    # Caching options
    parser.add_argument("--no-cache", action="store_true", help="Disable result caching")
    parser.add_argument("--clear-cache", action="store_true", help="Clear test result cache")

    # Reporting options
    parser.add_argument("--html-report", action="store_true", default=True, help="Generate HTML report")
    parser.add_argument("--no-html-report", action="store_true", help="Disable HTML report generation")

    args = parser.parse_args()

    # Setup paths
    script_dir = Path(__file__).parent
    test_dir = script_dir
    results_dir = script_dir / "results"

    # Initialize test runner
    runner = TestRunner(test_dir, results_dir)

    # Configure caching
    runner.cache_enabled = not args.no_cache

    # Configure HTML reports
    runner.html_reports_enabled = args.html_report and not args.no_html_report

    # Set filters
    runner.set_filters(
        include=args.include,
        exclude=args.exclude,
        include_markers=args.include_markers,
        exclude_markers=args.exclude_markers
    )

    # Clear cache if requested
    if args.clear_cache:
        runner.print_status("Clearing test cache...", "🔧")
        for cache_file in runner.cache_dir.glob("*.pkl"):
            cache_file.unlink()
        runner.print_status("Cache cleared", "✅")

    # Clean if requested
    if args.clean:
        runner.clean_results()

    if args.report_only:
        # Just generate report from existing results
        runner.generate_report()
        return

    # Run tests based on category
    if args.category == "unit":
        runner.run_unit_tests()
    elif args.category == "integration":
        runner.run_integration_tests()
    elif args.category == "e2e":
        runner.run_end_to_end_tests()
    else:
        runner.run_all_tests()

    # Generate final report
    success = runner.generate_report()

    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
