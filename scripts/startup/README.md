# Syntheverse Startup Scripts

A production-grade service orchestration platform for the Syntheverse platform, featuring intelligent port management, comprehensive health monitoring, parallel startup orchestration, and blockchain state management.

## Quick Start

### Basic Usage

```bash
# Start all services in development mode
python start_servers.py

# Start PoC system only (API + Frontend)
python start_servers.py --mode poc

# Start minimal system (PoC API only)
python start_servers.py --mode minimal
```

### Advanced Usage

```bash
# Production deployment
python start_servers.py --mode full --profile prod

# Testing environment
python start_servers.py --mode poc --profile test

# Restart specific services
python start_servers.py --restart poc_api frontend

# Headless operation (no browser auto-open)
python start_servers.py --no-browser
```

## Service Profiles

### Development Profile (`--profile dev`)
- **Best for**: Local development and debugging
- **Features**: Parallel startup, fast health checks, auto-restart enabled
- **Timeouts**: 30 seconds for health checks
- **Ports**: Standard development ports

### Testing Profile (`--profile test`)
- **Best for**: Automated testing and CI/CD
- **Features**: Sequential startup for predictability, auto-restart disabled
- **Timeouts**: 60 seconds for health checks
- **Ports**: Offset ports (+1000) to avoid conflicts

### Production Profile (`--profile prod`)
- **Best for**: Live deployments
- **Features**: Parallel startup with dependency ordering, robust error handling
- **Timeouts**: 120 seconds for health checks
- **Ports**: Standard production ports

### Minimal Profile (`--profile minimal`)
- **Best for**: Resource-constrained environments
- **Features**: Sequential startup, minimal services
- **Timeouts**: 15 seconds for health checks
- **Ports**: Only essential services

## Service Architecture

```
🌐 SYNTHVERSE SERVERS RUNNING:
┌─────────────────────────────────────┐
│ PoC API          http://127.0.0.1:5001 │
│ API Health       http://127.0.0.1:5001/health │
│ RAG API          http://127.0.0.1:8000 │
│ RAG Docs         http://127.0.0.1:8000/docs │
│ Next.js UI       http://127.0.0.1:3001 │
│ Anvil Node       http://127.0.0.1:8545 │
└─────────────────────────────────────┘
```

### Service Dependencies

```
frontend → poc_api    (UI needs API data)
poc_api  → rag_api    (PoC may use RAG for evaluation)
```

## Environment Setup

### Required Environment Variables

```bash
# Copy and edit .env file
cp .env.example .env

# Required for all modes
GROQ_API_KEY=gsk_your-groq-api-key-here
```

### Optional Environment Variables

```bash
# Flask environment
FLASK_ENV=development|testing|production

# Node.js environment
NODE_ENV=development|production

# Custom port assignments (overrides defaults)
POC_API_PORT=5001
RAG_API_PORT=8000
FRONTEND_PORT=3001
ANVIL_PORT=8545
```

## Port Management

### Automatic Port Resolution

The system automatically handles port conflicts:

```bash
# Check port status
python -c "
from scripts.startup.port_manager import get_port_status
status = get_port_status(5001, 'poc_api')
print(f'Port 5001: {status[\"available\"]}, Process: {status[\"process_count\"]}')
"
```

### Manual Port Management

```python
from scripts.startup.port_manager import port_manager

# Reserve a port for your service
port_manager.reserve_port(5001, "my_service", os.getpid())

# Check multiple ports simultaneously
results = port_manager.check_ports_batch([5001, 8000, 3001])
print(f"Available ports: {[p for p, avail in results.items() if avail]}")

# Get performance metrics
metrics = port_manager.get_metrics(port=5001)
for metric in metrics:
    print(f"Cleanup took {metric.cleanup_duration:.2f}s, {metric.processes_killed} processes killed")
```

## Health Monitoring

### Real-time Health Checks

```python
from scripts.startup.service_health import health_checker

# Check all services
results = health_checker.check_all_services()
for service, result in results.items():
    status = "✅" if result.status.name == "HEALTHY" else "❌"
    print(f"{status} {service}: {result.response_time:.2f}s")

# Get detailed service metrics
metrics = health_checker.get_service_metrics('poc_api')
print(f"Uptime: {metrics.uptime_percentage:.1%}, Avg response: {metrics.average_response_time:.2f}s")
```

### Service Dependencies

```python
# Add custom service dependency
health_checker.add_dependency('my_service', 'poc_api')

# Get optimal startup order
order = health_checker.get_startup_order()
print(f"Start services in order: {order}")
```

## Blockchain Management

### Anvil Node Operations

```python
from scripts.startup.anvil_manager import anvil_manager

# Start with custom configuration
anvil_manager.start_anvil(
    accounts=5,
    block_time=2,  # 2 second blocks
    gas_limit="10000000"
)

# Create blockchain snapshot
snapshot_id = anvil_manager.create_snapshot("before_deployment")

# Enable mainnet fork for testing
anvil_manager.enable_fork_mode(
    "https://mainnet.infura.io/v3/YOUR_PROJECT_ID",
    fork_mode="mainnet"
)

# Monitor gas usage
metrics = anvil_manager.get_gas_metrics()
print(f"Current gas price: {metrics.average_gas_price}")
```

### Snapshot Management

```python
# List all snapshots
snapshots = anvil_manager.list_snapshots()
for snap in snapshots:
    print(f"{snap['id']}: Block {snap['block_number']} ({snap['created']})")

# Restore previous state
success = anvil_manager.restore_snapshot("before_deployment")
```

## Monitoring and Debugging

### Performance Metrics

```bash
# View startup performance
python -c "
from scripts.startup.start_servers import ServerManager
import json
manager = ServerManager()
print('Startup Metrics:')
print(f'  Total time: {manager.metrics.total_startup_time:.2f}s')
print(f'  Port cleanup: {manager.metrics.port_cleanup_time:.2f}s')
print(f'  Health checks: {manager.metrics.health_check_time:.2f}s')
print(f'  Services started: {manager.metrics.services_started}')
"
```

### Service State Inspection

```bash
# Check running services
python -c "
from scripts.startup.start_servers import ServerManager
manager = ServerManager()
for name, state in manager.service_states.items():
    uptime = time.time() - state.start_time
    print(f'{name}: PID {state.pid}, port {state.port}, {uptime:.1f}s uptime')
"
```

### Log Analysis

```bash
# View recent logs
tail -f ~/.syntheverse/logs/startup.log

# Filter by service
grep "poc_api" ~/.syntheverse/logs/startup.log
```

## Troubleshooting

### Common Issues

#### Services Won't Start

```bash
# Check port availability
lsof -i :5001

# Force cleanup
python -c "from scripts.startup.port_manager import free_port; free_port(5001, 'poc_api')"

# Check environment
echo $GROQ_API_KEY
```

#### Slow Startup

```bash
# Use minimal profile for faster startup
python start_servers.py --mode minimal --profile minimal

# Check what's slowing down startup
python -c "
import time
start = time.time()
from scripts.startup.start_servers import ServerManager
manager = ServerManager()
print(f'Initialization: {time.time() - start:.2f}s')
"
```

#### Health Check Failures

```bash
# Get detailed health status
python -c "
from scripts.startup.service_health import get_service_status
status = get_service_status('poc_api')
print(f'Status: {status[\"status\"]}')
print(f'Error: {status.get(\"error_message\", \"None\")}')
print(f'Uptime: {status[\"uptime_percentage\"]:.1%}')
"
```

#### Blockchain Connection Issues

```bash
# Reset Anvil
python -c "
from scripts.startup.anvil_manager import anvil_manager
anvil_manager.stop_anvil()
anvil_manager.start_anvil()
"

# Check Anvil status
curl -X POST -H "Content-Type: application/json" \
     --data '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' \
     http://127.0.0.1:8545
```

### Recovery Procedures

#### Complete System Reset

```bash
# Stop all services
pkill -f "python.*start_servers.py"
pkill -f "anvil"
pkill -f "next"

# Clear state
rm -f ~/.syntheverse/startup_state.json
rm -rf ~/.syntheverse/anvil/snapshots/

# Clean ports
for port in 5001 8000 3001 8545; do
    lsof -ti:$port | xargs kill -9 2>/dev/null || true
done

# Restart
python start_servers.py --mode full --profile dev
```

#### Emergency Port Cleanup

```bash
#!/bin/bash
# emergency_port_cleanup.sh

PORTS=(5001 8000 3001 8545)

for port in "${PORTS[@]}"; do
    echo "Cleaning port $port..."
    # Kill all processes on port
    lsof -ti:$port | xargs kill -9 2>/dev/null || true
    sleep 1
    # Verify port is free
    if lsof -i:$port >/dev/null 2>&1; then
        echo "WARNING: Port $port still in use"
    else
        echo "✓ Port $port cleaned"
    fi
done
```

## Development

### Running Tests

```bash
# Run all startup tests
python -m pytest tests/test_startup_scripts.py -v

# Run port manager tests
python -m pytest tests/test_port_manager.py -v

# Run service health tests
python -m pytest tests/test_service_health.py -v

# Run anvil manager tests
python -m pytest tests/test_anvil_manager.py -v

# Run with coverage
python -m pytest tests/ --cov=scripts/startup --cov-report=html
```

### Adding New Services

```python
# 1. Define service in ServerManager.__init__
self.services['my_service'] = ServiceInfo(
    name='My Service',
    port=6001,
    endpoint='/health',
    dependencies=['poc_api']  # Optional
)

# 2. Add startup logic in start_services_parallel
elif service_name == 'my_service':
    success = self.start_server("python my_service.py", "My Service", 6001)

# 3. Add to ports dict
self.ports['my_service'] = 6001
```

### Custom Health Checks

```python
from scripts.startup.service_health import ServiceInfo, HealthCheckType

# Add custom service with WebSocket health check
health_checker.services['websocket_service'] = ServiceInfo(
    name='WebSocket Service',
    port=8080,
    endpoint='/ws',
    check_type=HealthCheckType.WEBSOCKET
)
```

## API Reference

See [`AGENTS.md`](AGENTS.md) for comprehensive API documentation including:
- All public methods and their parameters
- Return types and error conditions
- Integration examples
- Performance characteristics

## Contributing

1. **Code Standards**: Follow existing patterns and add comprehensive tests
2. **Documentation**: Update both `README.md` and `AGENTS.md` for new features
3. **Testing**: Maintain 90%+ test coverage, add integration tests for new features
4. **Performance**: Ensure new features don't degrade startup performance
5. **Compatibility**: Maintain backward compatibility with existing configurations

## License

See project root [`LICENSE`](../../LICENSE) file.