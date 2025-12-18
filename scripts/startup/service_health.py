#!/usr/bin/env python3
"""
Service Health Check Module for Syntheverse
Unified health checking for all Syntheverse services
"""

import time
import requests
import logging
import threading
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass
from enum import Enum
import websockets
import asyncio

class ServiceStatus(Enum):
    """Service health status"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"
    STARTING = "starting"
    CIRCUIT_OPEN = "circuit_open"

class HealthCheckType(Enum):
    """Types of health checks supported"""
    HTTP = "http"
    HTTPS = "https"
    WEBSOCKET = "websocket"
    RPC = "rpc"

class ErrorCategory(Enum):
    """Error categorization for health checks"""
    NETWORK = "network"
    TIMEOUT = "timeout"
    AUTHENTICATION = "authentication"
    SERVICE_ERROR = "service_error"
    CONFIGURATION = "configuration"
    UNKNOWN = "unknown"

@dataclass
class ServiceDependency:
    """Service dependency relationship"""
    service: str
    depends_on: str
    required: bool = True

@dataclass
class CircuitBreakerState:
    """Circuit breaker state"""
    failures: int = 0
    last_failure_time: Optional[float] = None
    state: str = "closed"  # closed, open, half_open
    next_attempt_time: Optional[float] = None

@dataclass
class ServiceInfo:
    """Information about a service"""
    name: str
    port: int
    endpoint: str
    expected_status: int = 200
    timeout: int = 5
    description: str = ""
    check_type: HealthCheckType = HealthCheckType.HTTP
    dependencies: List[str] = None
    adaptive_timeout: bool = True

@dataclass
class HealthCheckResult:
    """Result of a health check"""
    service: ServiceInfo
    status: ServiceStatus
    response_time: float
    status_code: Optional[int] = None
    error_message: Optional[str] = None
    error_category: Optional[ErrorCategory] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: Optional[float] = None

@dataclass
class ServiceMetrics:
    """Service performance metrics"""
    service_name: str
    total_checks: int = 0
    healthy_checks: int = 0
    average_response_time: float = 0.0
    last_check_time: Optional[float] = None
    uptime_percentage: float = 0.0
    consecutive_failures: int = 0
    total_failures: int = 0

class ServiceHealthChecker:
    """Unified health checker for Syntheverse services with advanced features"""

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)

        # Service definitions with enhanced metadata
        self.services = {
            'poc_api': ServiceInfo(
                name='PoC API',
                port=5001,
                endpoint='/health',
                description='Flask REST API for PoC operations',
                dependencies=[]  # PoC API is independent
            ),
            'rag_api': ServiceInfo(
                name='RAG API',
                port=8000,
                endpoint='/health',
                description='FastAPI server for RAG queries',
                dependencies=[]
            ),
            'nextjs_frontend': ServiceInfo(
                name='Next.js Frontend',
                port=3001,
                endpoint='/',
                expected_status=200,  # Next.js returns 200 for homepage
                description='Modern React UI dashboard',
                dependencies=['poc_api']  # Frontend needs API to function
            ),
            'frontend': ServiceInfo(  # Alias for consistency
                name='Next.js Frontend',
                port=3001,
                endpoint='/',
                expected_status=200,
                description='Modern React UI dashboard',
                dependencies=['poc_api']
            ),
            'legacy_web_ui': ServiceInfo(
                name='Legacy Web UI',
                port=5000,
                endpoint='/',
                description='Flask-based legacy web interface',
                dependencies=['poc_api']  # Legacy UI also needs API
            ),
            'anvil': ServiceInfo(
                name='Anvil',
                port=8545,
                endpoint=None,
                check_type=HealthCheckType.RPC,
                description='Foundry Ethereum development node',
                dependencies=[]
            )
        }

        # Service dependency graph
        self._dependency_graph = self._build_dependency_graph()

        # Circuit breakers for each service
        self._circuit_breakers: Dict[str, CircuitBreakerState] = {}
        self._circuit_lock = threading.Lock()

        # Health check caching
        self._health_cache: Dict[str, HealthCheckResult] = {}
        self._cache_ttl = 30  # seconds
        self._cache_lock = threading.Lock()

        # Service performance metrics
        self._metrics: Dict[str, ServiceMetrics] = {}
        self._metrics_lock = threading.Lock()

        # Adaptive health check intervals
        self._adaptive_intervals: Dict[str, float] = {}
        self._base_interval = 30  # seconds
        self._max_interval = 300  # 5 minutes

    def _build_dependency_graph(self) -> Dict[str, Set[str]]:
        """Build dependency graph from service definitions"""
        graph = {}
        for service_name, service_info in self.services.items():
            graph[service_name] = set(service_info.dependencies or [])
        return graph

    def add_dependency(self, service: str, depends_on: str, required: bool = True):
        """Add a service dependency"""
        if service not in self.services:
            self.logger.warning(f"Service {service} not found, cannot add dependency")
            return

        if depends_on not in self.services:
            self.logger.warning(f"Dependency service {depends_on} not found")
            return

        if self.services[service].dependencies is None:
            self.services[service].dependencies = []

        if depends_on not in self.services[service].dependencies:
            self.services[service].dependencies.append(depends_on)
            self._dependency_graph[service].add(depends_on)
            self.logger.info(f"Added dependency: {service} -> {depends_on}")

    def get_startup_order(self) -> List[str]:
        """Get optimal service startup order based on dependencies"""
        # Simple topological sort
        visited = set()
        temp_visited = set()
        order = []

        def visit(service):
            if service in temp_visited:
                self.logger.warning(f"Circular dependency detected involving {service}")
                return
            if service in visited:
                return

            temp_visited.add(service)

            for dependency in self._dependency_graph.get(service, set()):
                visit(dependency)

            temp_visited.remove(service)
            visited.add(service)
            order.append(service)

        for service in self.services.keys():
            if service not in visited:
                visit(service)

        return order[::-1]  # Reverse to get startup order

    def _get_circuit_breaker(self, service_name: str) -> CircuitBreakerState:
        """Get or create circuit breaker for service"""
        with self._circuit_lock:
            if service_name not in self._circuit_breakers:
                self._circuit_breakers[service_name] = CircuitBreakerState()
            return self._circuit_breakers[service_name]

    def _update_circuit_breaker(self, service_name: str, success: bool):
        """Update circuit breaker state based on health check result"""
        cb = self._get_circuit_breaker(service_name)
        current_time = time.time()

        with self._circuit_lock:
            if success:
                cb.failures = 0
                cb.state = "closed"
                cb.last_failure_time = None
                cb.next_attempt_time = None
            else:
                cb.failures += 1
                cb.last_failure_time = current_time

                # Open circuit after 3 consecutive failures
                if cb.failures >= 3 and cb.state != "open":
                    cb.state = "open"
                    cb.next_attempt_time = current_time + 60  # Try again in 1 minute
                    self.logger.warning(f"Circuit breaker opened for {service_name}")

    def _is_circuit_open(self, service_name: str) -> bool:
        """Check if circuit breaker is open"""
        cb = self._get_circuit_breaker(service_name)
        current_time = time.time()

        if cb.state == "open":
            if cb.next_attempt_time and current_time >= cb.next_attempt_time:
                # Half-open: allow one request through
                cb.state = "half_open"
                return False
            return True

        return False

    def _get_adaptive_interval(self, service_name: str) -> float:
        """Get adaptive health check interval based on service stability"""
        if service_name not in self._metrics:
            return self._base_interval

        metrics = self._metrics[service_name]

        # Adjust interval based on uptime and consecutive failures
        if metrics.uptime_percentage > 0.95 and metrics.consecutive_failures == 0:
            # Very stable service - check less frequently
            return min(self._max_interval, self._base_interval * 2)
        elif metrics.uptime_percentage < 0.8 or metrics.consecutive_failures > 1:
            # Unstable service - check more frequently
            return max(5, self._base_interval / 2)
        else:
            # Normal service
            return self._base_interval

    def _record_metrics(self, service_name: str, result: HealthCheckResult):
        """Record service performance metrics"""
        with self._metrics_lock:
            if service_name not in self._metrics:
                self._metrics[service_name] = ServiceMetrics(service_name=service_name)

            metrics = self._metrics[service_name]
            metrics.total_checks += 1
            metrics.last_check_time = time.time()

            if result.status == ServiceStatus.HEALTHY:
                metrics.healthy_checks += 1
                metrics.consecutive_failures = 0
            else:
                metrics.consecutive_failures += 1
                metrics.total_failures += 1

            # Update average response time
            if metrics.average_response_time == 0:
                metrics.average_response_time = result.response_time
            else:
                metrics.average_response_time = (
                    metrics.average_response_time * (metrics.total_checks - 1) + result.response_time
                ) / metrics.total_checks

            # Calculate uptime percentage (over last 100 checks)
            if metrics.total_checks > 0:
                recent_checks = min(100, metrics.total_checks)
                recent_healthy = metrics.healthy_checks
                metrics.uptime_percentage = recent_healthy / recent_checks

    def get_service_metrics(self, service_name: str = None) -> Dict[str, ServiceMetrics]:
        """Get service performance metrics"""
        with self._metrics_lock:
            if service_name:
                return {service_name: self._metrics.get(service_name, ServiceMetrics(service_name=service_name))}
            else:
                return self._metrics.copy()

    def _categorize_error(self, exception: Exception, service_info: ServiceInfo) -> ErrorCategory:
        """Categorize health check errors"""
        if isinstance(exception, requests.exceptions.Timeout):
            return ErrorCategory.TIMEOUT
        elif isinstance(exception, requests.exceptions.ConnectionError):
            return ErrorCategory.NETWORK
        elif isinstance(exception, requests.exceptions.HTTPError):
            status_code = getattr(exception.response, 'status_code', 0)
            if status_code in [401, 403]:
                return ErrorCategory.AUTHENTICATION
            elif status_code >= 500:
                return ErrorCategory.SERVICE_ERROR
            else:
                return ErrorCategory.CONFIGURATION
        else:
            return ErrorCategory.UNKNOWN

    def check_service_health(self, service_name: str, use_cache: bool = True) -> HealthCheckResult:
        """Check health of a specific service with caching and circuit breaker support"""
        if service_name not in self.services:
            return HealthCheckResult(
                service=ServiceInfo(name=f"Unknown: {service_name}", port=0, endpoint=""),
                status=ServiceStatus.UNKNOWN,
                response_time=0.0,
                error_message=f"Service '{service_name}' not defined",
                timestamp=time.time()
            )

        # Check cache first
        if use_cache:
            with self._cache_lock:
                if service_name in self._health_cache:
                    cached_result = self._health_cache[service_name]
                    if time.time() - (cached_result.timestamp or 0) < self._cache_ttl:
                        return cached_result

        # Check circuit breaker
        if self._is_circuit_open(service_name):
            return HealthCheckResult(
                service=self.services[service_name],
                status=ServiceStatus.CIRCUIT_OPEN,
                response_time=0.0,
                error_message="Circuit breaker is open",
                error_category=ErrorCategory.SERVICE_ERROR,
                timestamp=time.time()
            )

        service_info = self.services[service_name]
        result = self._check_single_service(service_info)

        # Update circuit breaker and metrics
        success = result.status == ServiceStatus.HEALTHY
        self._update_circuit_breaker(service_name, success)
        self._record_metrics(service_name, result)

        # Cache the result
        with self._cache_lock:
            self._health_cache[service_name] = result

        return result

    def check_all_services(self) -> Dict[str, HealthCheckResult]:
        """Check health of all services"""
        results = {}
        for service_name in self.services.keys():
            results[service_name] = self.check_service_health(service_name)
        return results

    def get_service_status(self, service_name: str) -> Dict[str, Any]:
        """Get detailed status information for a service"""
        result = self.check_service_health(service_name)
        metrics = self._metrics.get(service_name, ServiceMetrics(service_name=service_name))

        status_info = {
            'name': result.service.name,
            'port': result.service.port,
            'status': result.status.value,
            'response_time': result.response_time,
            'description': result.service.description,
            'check_type': result.service.check_type.value,
            'uptime_percentage': metrics.uptime_percentage,
            'consecutive_failures': metrics.consecutive_failures,
            'total_checks': metrics.total_checks,
            'adaptive_interval': self._get_adaptive_interval(service_name)
        }

        if result.status_code is not None:
            status_info['status_code'] = result.status_code

        if result.error_message:
            status_info['error_message'] = result.error_message

        if result.error_category:
            status_info['error_category'] = result.error_category.value

        if result.details:
            status_info['details'] = result.details

        # Add circuit breaker info
        cb = self._get_circuit_breaker(service_name)
        status_info['circuit_breaker'] = {
            'state': cb.state,
            'failures': cb.failures,
            'last_failure_time': cb.last_failure_time
        }

        # Add dependency info
        status_info['dependencies'] = list(self._dependency_graph.get(service_name, set()))

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
        """Check health of a single service with support for multiple protocols"""
        start_time = time.time()

        try:
            if service.check_type == HealthCheckType.RPC or service.name == 'Anvil':
                # RPC health check for blockchain nodes
                return self._check_rpc_health(service, start_time)
            elif service.check_type == HealthCheckType.WEBSOCKET:
                # WebSocket health check
                return self._check_websocket_health(service, start_time)
            elif service.check_type in [HealthCheckType.HTTP, HealthCheckType.HTTPS]:
                # Standard HTTP/HTTPS health check
                return self._check_http_health(service, start_time)
            else:
                return HealthCheckResult(
                    service=service,
                    status=ServiceStatus.UNKNOWN,
                    response_time=time.time() - start_time,
                    error_message=f"Unsupported check type: {service.check_type}",
                    error_category=ErrorCategory.CONFIGURATION,
                    timestamp=time.time()
                )

        except Exception as e:
            response_time = time.time() - start_time
            error_category = self._categorize_error(e, service)
            return HealthCheckResult(
                service=service,
                status=ServiceStatus.UNHEALTHY,
                response_time=response_time,
                error_message=str(e),
                error_category=error_category,
                timestamp=time.time()
            )

    def _check_http_health(self, service: ServiceInfo, start_time: float) -> HealthCheckResult:
        """Check health via HTTP request with enhanced error handling"""
        protocol = "https" if service.check_type == HealthCheckType.HTTPS else "http"
        url = f"{protocol}://127.0.0.1:{service.port}{service.endpoint}"

        try:
            # Adaptive timeout if enabled
            timeout = service.timeout
            if service.adaptive_timeout and service.name in self._metrics:
                metrics = self._metrics[service.name]
                # Increase timeout for unstable services
                if metrics.consecutive_failures > 0:
                    timeout = min(timeout * 2, 30)

            response = requests.get(url, timeout=timeout)
            response_time = time.time() - start_time

            if response.status_code == service.expected_status:
                status = ServiceStatus.HEALTHY
                error_message = None
                error_category = None
            else:
                status = ServiceStatus.UNHEALTHY
                error_message = f"Unexpected status code: {response.status_code}"
                error_category = ErrorCategory.SERVICE_ERROR if response.status_code >= 500 else ErrorCategory.CONFIGURATION

            return HealthCheckResult(
                service=service,
                status=status,
                response_time=response_time,
                status_code=response.status_code,
                error_message=error_message,
                error_category=error_category,
                details={
                    'url': url,
                    'content_length': len(response.content),
                    'headers': dict(response.headers)
                },
                timestamp=time.time()
            )

        except requests.exceptions.Timeout:
            response_time = time.time() - start_time
            return HealthCheckResult(
                service=service,
                status=ServiceStatus.STARTING,
                response_time=response_time,
                error_message="Request timeout",
                error_category=ErrorCategory.TIMEOUT,
                timestamp=time.time()
            )

        except requests.exceptions.ConnectionError:
            response_time = time.time() - start_time
            return HealthCheckResult(
                service=service,
                status=ServiceStatus.UNHEALTHY,
                response_time=response_time,
                error_message="Connection refused",
                error_category=ErrorCategory.NETWORK,
                timestamp=time.time()
            )

        except requests.exceptions.HTTPError as e:
            response_time = time.time() - start_time
            status_code = getattr(e.response, 'status_code', 0)
            return HealthCheckResult(
                service=service,
                status=ServiceStatus.UNHEALTHY,
                response_time=response_time,
                status_code=status_code,
                error_message=str(e),
                error_category=self._categorize_error(e, service),
                timestamp=time.time()
            )

        except Exception as e:
            response_time = time.time() - start_time
            return HealthCheckResult(
                service=service,
                status=ServiceStatus.UNHEALTHY,
                response_time=response_time,
                error_message=f"Unexpected error: {str(e)}",
                error_category=ErrorCategory.UNKNOWN,
                timestamp=time.time()
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
                error_message=f"RPC error: {str(e)}",
                error_category=self._categorize_error(e, service),
                timestamp=time.time()
            )

    def _check_websocket_health(self, service: ServiceInfo, start_time: float) -> HealthCheckResult:
        """Check health via WebSocket connection"""
        ws_url = f"ws://127.0.0.1:{service.port}{service.endpoint}"

        try:
            # Use asyncio to test WebSocket connection
            async def test_ws():
                try:
                    async with websockets.connect(ws_url, timeout=service.timeout) as websocket:
                        # Send a simple ping/health check message if endpoint expects it
                        if service.endpoint == '/health':
                            await websocket.send('{"type": "ping"}')
                            response = await websocket.recv()
                            return True, response
                        else:
                            # Just test connection
                            return True, None
                except Exception as e:
                    return False, str(e)

            # Run the async test
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                success, response = loop.run_until_complete(test_ws())
                response_time = time.time() - start_time

                if success:
                    return HealthCheckResult(
                        service=service,
                        status=ServiceStatus.HEALTHY,
                        response_time=response_time,
                        details={'websocket_url': ws_url, 'response': response},
                        timestamp=time.time()
                    )
                else:
                    return HealthCheckResult(
                        service=service,
                        status=ServiceStatus.UNHEALTHY,
                        response_time=response_time,
                        error_message=f"WebSocket connection failed: {response}",
                        error_category=ErrorCategory.NETWORK,
                        timestamp=time.time()
                    )
            finally:
                loop.close()

        except Exception as e:
            response_time = time.time() - start_time
            return HealthCheckResult(
                service=service,
                status=ServiceStatus.UNHEALTHY,
                response_time=response_time,
                error_message=f"WebSocket error: {str(e)}",
                error_category=ErrorCategory.NETWORK,
                timestamp=time.time()
            )

    def _check_rpc_health(self, service: ServiceInfo, start_time: float) -> HealthCheckResult:
        """Check health via RPC calls (for blockchain nodes, etc.)"""
        try:
            # For Anvil or other RPC services
            if service.name == 'Anvil':
                return self._check_anvil_health(service, start_time)

            # Generic RPC health check
            rpc_url = f"http://127.0.0.1:{service.port}"
            payload = {
                "jsonrpc": "2.0",
                "method": "system_health",  # Generic health method
                "params": [],
                "id": 1
            }

            response = requests.post(rpc_url, json=payload, timeout=service.timeout)
            response_time = time.time() - start_time

            if response.status_code == 200:
                result = response.json()
                if 'result' in result or 'error' not in result:
                    return HealthCheckResult(
                        service=service,
                        status=ServiceStatus.HEALTHY,
                        response_time=response_time,
                        status_code=response.status_code,
                        details={'rpc_url': rpc_url, 'response': result},
                        timestamp=time.time()
                    )

            return HealthCheckResult(
                service=service,
                status=ServiceStatus.UNHEALTHY,
                response_time=response_time,
                status_code=response.status_code,
                error_message="Invalid RPC response",
                error_category=ErrorCategory.SERVICE_ERROR,
                timestamp=time.time()
            )

        except requests.exceptions.Timeout:
            response_time = time.time() - start_time
            return HealthCheckResult(
                service=service,
                status=ServiceStatus.STARTING,
                response_time=response_time,
                error_message="RPC timeout",
                error_category=ErrorCategory.TIMEOUT,
                timestamp=time.time()
            )

        except requests.exceptions.ConnectionError:
            response_time = time.time() - start_time
            return HealthCheckResult(
                service=service,
                status=ServiceStatus.UNHEALTHY,
                response_time=response_time,
                error_message="RPC connection refused",
                error_category=ErrorCategory.NETWORK,
                timestamp=time.time()
            )

        except Exception as e:
            response_time = time.time() - start_time
            return HealthCheckResult(
                service=service,
                status=ServiceStatus.UNHEALTHY,
                response_time=response_time,
                error_message=f"RPC error: {str(e)}",
                error_category=self._categorize_error(e, service),
                timestamp=time.time()
            )

    def print_health_report(self, results: Optional[Dict[str, HealthCheckResult]] = None,
                           include_metrics: bool = True) -> None:
        """Print a formatted health report with enhanced information"""
        if results is None:
            results = self.check_all_services()

        print("\n" + "="*80)
        print("🩺 SYNTHVERSE SERVICE HEALTH REPORT")
        print("="*80)

        healthy_count = 0
        total_count = len(results)

        for service_name, result in results.items():
            status_icon = {
                ServiceStatus.HEALTHY: "✅",
                ServiceStatus.UNHEALTHY: "❌",
                ServiceStatus.STARTING: "⏳",
                ServiceStatus.UNKNOWN: "❓",
                ServiceStatus.CIRCUIT_OPEN: "🔌"
            }.get(result.status, "❓")

            uptime_str = ""
            if include_metrics and service_name in self._metrics:
                metrics = self._metrics[service_name]
                uptime_str = f" ({metrics.uptime_percentage:.1%} uptime)"

            print(f"{status_icon} {result.service.name:<18} "
                  f"(Port {result.service.port:<5}) - "
                  f"{result.status.value.upper():<12} "
                  f"({result.response_time:.2f}s){uptime_str}")

            if result.error_message:
                error_cat = f" [{result.error_category.value}]" if result.error_category else ""
                print(f"    Error{error_cat}: {result.error_message}")

            if result.details and result.status == ServiceStatus.HEALTHY:
                # Show key details for healthy services
                for key, value in result.details.items():
                    if key in ['block_number', 'accounts', 'content_length']:
                        print(f"    {key}: {value}")

            # Show circuit breaker status for unhealthy services
            if result.status in [ServiceStatus.UNHEALTHY, ServiceStatus.CIRCUIT_OPEN]:
                cb = self._get_circuit_breaker(service_name)
                if cb.failures > 0:
                    print(f"    Circuit breaker: {cb.state} ({cb.failures} failures)")

            if result.status == ServiceStatus.HEALTHY:
                healthy_count += 1

        print("="*80)
        print(f"Summary: {healthy_count}/{total_count} services healthy")

        if include_metrics:
            # Show overall metrics
            total_checks = sum(m.total_checks for m in self._metrics.values())
            if total_checks > 0:
                avg_response = sum(m.average_response_time for m in self._metrics.values()) / len(self._metrics)
                print(f"Average response time: {avg_response:.2f}s across {total_checks} checks")

        print("="*80)

# Global instance for convenience
health_checker = ServiceHealthChecker()

# Convenience functions
def check_service_health(service_name: str, use_cache: bool = True) -> HealthCheckResult:
    """Check health of a specific service"""
    return health_checker.check_service_health(service_name, use_cache)

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

def print_health_report(results: Optional[Dict[str, HealthCheckResult]] = None,
                       include_metrics: bool = True) -> None:
    """Print a formatted health report"""
    health_checker.print_health_report(results, include_metrics)

# New convenience functions for enhanced features
def add_service_dependency(service: str, depends_on: str):
    """Add a service dependency"""
    health_checker.add_dependency(service, depends_on)

def get_startup_order() -> List[str]:
    """Get optimal service startup order"""
    return health_checker.get_startup_order()

def get_service_metrics(service_name: str = None) -> Dict[str, ServiceMetrics]:
    """Get service performance metrics"""
    return health_checker.get_service_metrics(service_name)

def get_adaptive_health_check_interval(service_name: str) -> float:
    """Get adaptive health check interval for service"""
    return health_checker._get_adaptive_interval(service_name)







