#!/usr/bin/env python3
"""
Service Health Check Module for Syntheverse
Unified health checking for all Syntheverse services
"""

import time
import requests
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

class ServiceStatus(Enum):
    """Service health status"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"
    STARTING = "starting"

@dataclass
class ServiceInfo:
    """Information about a service"""
    name: str
    port: int
    endpoint: str
    expected_status: int = 200
    timeout: int = 5
    description: str = ""

@dataclass
class HealthCheckResult:
    """Result of a health check"""
    service: ServiceInfo
    status: ServiceStatus
    response_time: float
    status_code: Optional[int] = None
    error_message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class ServiceHealthChecker:
    """Unified health checker for Syntheverse services"""

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)

        # Define all Syntheverse services
        self.services = {
            'poc_api': ServiceInfo(
                name='PoC API',
                port=5001,
                endpoint='/health',
                description='Flask REST API for PoC operations'
            ),
            'rag_api': ServiceInfo(
                name='RAG API',
                port=8000,
                endpoint='/health',
                description='FastAPI server for RAG queries'
            ),
            'nextjs_frontend': ServiceInfo(
                name='Next.js Frontend',
                port=3001,
                endpoint='/',
                description='Modern React UI dashboard'
            ),
            'legacy_web_ui': ServiceInfo(
                name='Legacy Web UI',
                port=5000,
                endpoint='/',
                description='Flask-based legacy web interface'
            ),
            'anvil': ServiceInfo(
                name='Anvil',
                port=8545,
                endpoint=None,  # Special handling for RPC
                description='Foundry Ethereum development node'
            )
        }

    def check_service_health(self, service_name: str) -> HealthCheckResult:
        """Check health of a specific service"""
        if service_name not in self.services:
            return HealthCheckResult(
                service=ServiceInfo(name=f"Unknown: {service_name}", port=0, endpoint=""),
                status=ServiceStatus.UNKNOWN,
                response_time=0.0,
                error_message=f"Service '{service_name}' not defined"
            )

        service_info = self.services[service_name]
        return self._check_single_service(service_info)

    def check_all_services(self) -> Dict[str, HealthCheckResult]:
        """Check health of all services"""
        results = {}
        for service_name in self.services.keys():
            results[service_name] = self.check_service_health(service_name)
        return results

    def get_service_status(self, service_name: str) -> Dict[str, Any]:
        """Get detailed status information for a service"""
        result = self.check_service_health(service_name)

        status_info = {
            'name': result.service.name,
            'port': result.service.port,
            'status': result.status.value,
            'response_time': result.response_time,
            'description': result.service.description
        }

        if result.status_code is not None:
            status_info['status_code'] = result.status_code

        if result.error_message:
            status_info['error_message'] = result.error_message

        if result.details:
            status_info['details'] = result.details

        return status_info

    def wait_for_service(self, service_name: str, timeout: int = 30,
                        interval: int = 2) -> bool:
        """Wait for a service to become healthy"""
        self.logger.info(f"Waiting for {service_name} to be ready (timeout: {timeout}s)")

        start_time = time.time()

        while time.time() - start_time < timeout:
            result = self.check_service_health(service_name)

            if result.status == ServiceStatus.HEALTHY:
                elapsed = time.time() - start_time
                self.logger.info(f"✅ {service_name} is ready after {elapsed:.1f}s")
                return True

            if result.status != ServiceStatus.STARTING:
                self.logger.debug(f"{service_name} status: {result.status.value}")

            time.sleep(interval)

        elapsed = time.time() - start_time
        self.logger.error(f"❌ {service_name} failed to become ready within {timeout}s timeout")
        return False

    def wait_for_all_services(self, timeout: int = 60, interval: int = 3) -> Dict[str, bool]:
        """Wait for all services to become healthy"""
        self.logger.info("Waiting for all services to be ready...")

        results = {}
        for service_name in self.services.keys():
            results[service_name] = self.wait_for_service(service_name, timeout, interval)

        ready_count = sum(results.values())
        total_count = len(results)

        if ready_count == total_count:
            self.logger.info(f"🎉 All {total_count} services are ready!")
        else:
            self.logger.warning(f"⚠️ Only {ready_count}/{total_count} services are ready")

        return results

    def _check_single_service(self, service: ServiceInfo) -> HealthCheckResult:
        """Check health of a single service"""
        start_time = time.time()

        try:
            if service.name == 'Anvil':
                # Special handling for Anvil RPC
                return self._check_anvil_health(service, start_time)
            else:
                # Standard HTTP health check
                return self._check_http_health(service, start_time)

        except Exception as e:
            response_time = time.time() - start_time
            return HealthCheckResult(
                service=service,
                status=ServiceStatus.UNHEALTHY,
                response_time=response_time,
                error_message=str(e)
            )

    def _check_http_health(self, service: ServiceInfo, start_time: float) -> HealthCheckResult:
        """Check health via HTTP request"""
        url = f"http://127.0.0.1:{service.port}{service.endpoint}"

        try:
            response = requests.get(url, timeout=service.timeout)
            response_time = time.time() - start_time

            if response.status_code == service.expected_status:
                status = ServiceStatus.HEALTHY
                error_message = None
            else:
                status = ServiceStatus.UNHEALTHY
                error_message = f"Unexpected status code: {response.status_code}"

            return HealthCheckResult(
                service=service,
                status=status,
                response_time=response_time,
                status_code=response.status_code,
                error_message=error_message,
                details={'url': url, 'content_length': len(response.content)}
            )

        except requests.exceptions.Timeout:
            response_time = time.time() - start_time
            return HealthCheckResult(
                service=service,
                status=ServiceStatus.STARTING,
                response_time=response_time,
                error_message="Request timeout"
            )

        except requests.exceptions.ConnectionError:
            response_time = time.time() - start_time
            return HealthCheckResult(
                service=service,
                status=ServiceStatus.UNHEALTHY,
                response_time=response_time,
                error_message="Connection refused"
            )

        except Exception as e:
            response_time = time.time() - start_time
            return HealthCheckResult(
                service=service,
                status=ServiceStatus.UNHEALTHY,
                response_time=response_time,
                error_message=f"Unexpected error: {str(e)}"
            )

    def _check_anvil_health(self, service: ServiceInfo, start_time: float) -> HealthCheckResult:
        """Check Anvil health via RPC"""
        try:
            # Try to get the current block number
            response = requests.post(
                f"http://127.0.0.1:{service.port}",
                json={
                    "jsonrpc": "2.0",
                    "method": "eth_blockNumber",
                    "params": [],
                    "id": 1
                },
                timeout=service.timeout
            )

            response_time = time.time() - start_time

            if response.status_code == 200:
                result = response.json()
                if 'result' in result:
                    # Try to get additional info
                    details = {'block_number': int(result['result'], 16)}

                    # Get accounts count
                    accounts_response = requests.post(
                        f"http://127.0.0.1:{service.port}",
                        json={
                            "jsonrpc": "2.0",
                            "method": "eth_accounts",
                            "params": [],
                            "id": 2
                        },
                        timeout=2
                    )

                    if accounts_response.status_code == 200:
                        accounts_result = accounts_response.json()
                        if 'result' in accounts_result:
                            details['accounts'] = len(accounts_result['result'])

                    return HealthCheckResult(
                        service=service,
                        status=ServiceStatus.HEALTHY,
                        response_time=response_time,
                        status_code=response.status_code,
                        details=details
                    )

            return HealthCheckResult(
                service=service,
                status=ServiceStatus.UNHEALTHY,
                response_time=response_time,
                status_code=response.status_code,
                error_message="Invalid RPC response"
            )

        except requests.exceptions.Timeout:
            response_time = time.time() - start_time
            return HealthCheckResult(
                service=service,
                status=ServiceStatus.STARTING,
                response_time=response_time,
                error_message="RPC timeout"
            )

        except requests.exceptions.ConnectionError:
            response_time = time.time() - start_time
            return HealthCheckResult(
                service=service,
                status=ServiceStatus.UNHEALTHY,
                response_time=response_time,
                error_message="Connection refused"
            )

        except Exception as e:
            response_time = time.time() - start_time
            return HealthCheckResult(
                service=service,
                status=ServiceStatus.UNHEALTHY,
                response_time=response_time,
                error_message=f"RPC error: {str(e)}"
            )

    def print_health_report(self, results: Optional[Dict[str, HealthCheckResult]] = None) -> None:
        """Print a formatted health report"""
        if results is None:
            results = self.check_all_services()

        print("\n" + "="*60)
        print("🩺 SYNTHVERSE SERVICE HEALTH REPORT")
        print("="*60)

        healthy_count = 0
        total_count = len(results)

        for service_name, result in results.items():
            status_icon = {
                ServiceStatus.HEALTHY: "✅",
                ServiceStatus.UNHEALTHY: "❌",
                ServiceStatus.STARTING: "⏳",
                ServiceStatus.UNKNOWN: "❓"
            }.get(result.status, "❓")

            print(f"{status_icon} {result.service.name:<15} "
                  f"(Port {result.service.port:<5}) - "
                  f"{result.status.value.upper():<8} "
                  f"({result.response_time:.2f}s)")

            if result.error_message:
                print(f"    Error: {result.error_message}")

            if result.details:
                for key, value in result.details.items():
                    print(f"    {key}: {value}")

            if result.status == ServiceStatus.HEALTHY:
                healthy_count += 1

        print("="*60)
        print(f"Summary: {healthy_count}/{total_count} services healthy")
        print("="*60)

# Global instance for convenience
health_checker = ServiceHealthChecker()

# Convenience functions
def check_service_health(service_name: str) -> HealthCheckResult:
    """Check health of a specific service"""
    return health_checker.check_service_health(service_name)

def check_all_services() -> Dict[str, HealthCheckResult]:
    """Check health of all services"""
    return health_checker.check_all_services()

def get_service_status(service_name: str) -> Dict[str, Any]:
    """Get detailed status information for a service"""
    return health_checker.get_service_status(service_name)

def wait_for_service(service_name: str, timeout: int = 30) -> bool:
    """Wait for a service to become healthy"""
    return health_checker.wait_for_service(service_name, timeout)

def wait_for_all_services(timeout: int = 60) -> Dict[str, bool]:
    """Wait for all services to become healthy"""
    return health_checker.wait_for_all_services(timeout)

def print_health_report(results: Optional[Dict[str, HealthCheckResult]] = None) -> None:
    """Print a formatted health report"""
    health_checker.print_health_report(results)


