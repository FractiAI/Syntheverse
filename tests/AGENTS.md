# Tests Agents

## Purpose

Test suites for validating system functionality, API endpoints, submission flows, and integration testing. Tests use real implementations with dependency management and service startup.

## Key Modules

### Core Test Framework

- **`test_framework.py`**: Test framework with base classes (`SyntheverseTestCase`, `APITestCase`, `DataTestCase`), retry mechanisms, and utilities
- **`test_runner.py`**: Test orchestrator with filtering, caching, parallel execution, and HTML reporting
- **`run_tests.sh`**: Shell script for test execution with colored output
- **`test_config.json`**: Configuration with test scenarios, thresholds, and environment settings

### Unit Test Modules

- **`test_core_modules.py`**: Core business logic testing (PoCArchive, TokenomicsState, SandboxMap, PoCEvaluator, TokenAllocator, PoCServer)
- **`test_anvil_manager.py`**: Blockchain node management and lifecycle testing
- **`test_port_manager.py`**: Port allocation, process monitoring, and conflict resolution
- **`test_service_health.py`**: Service health checking and monitoring functionality

### Integration Test Modules

- **`test_poc_api.py`**: PoC API endpoints, error scenarios, rate limiting, and concurrent requests
- **`test_rag_api.py`**: RAG API connectivity, query variations, and error handling
- **`test_rag_pod_query.py`**: RAG PoD-specific query functionality
- **`test_frontend_integration.py`**: Frontend-backend integration and UI testing
- **`test_blockchain.py`**: Blockchain layer1 integration and contract testing

### End-to-End Test Modules

- **`test_submission_flow.py`**: Complete submission workflow validation
- **`test_full_submission_flow.py`**: Full end-to-end process testing
- **`test_submission.py`**: Submission testing with error scenarios

### Specialized Test Modules

- **`test_data_management.py`**: File operations, JSON integrity, backup/recovery, and concurrent access
- **`test_security.py`**: Input sanitization, authentication bypass prevention, data exposure protection
- **`test_performance.py`**: API response times, load testing, memory/CPU usage, and scalability analysis
- **`test_rag_timeout.py`**: RAG timeout handling and recovery mechanisms

### Infrastructure Test Modules

- **`test_startup_scripts.py`**: Service startup validation and environment configuration
- **`test_main_menu.py`**: ScriptMenu class testing (init, validation, execution, navigation, errors, performance)
- **`test_deployment.py`**: Smart contract deployment and validation
- **`test_fixtures.py`**: Test data generators and environment management utilities

### Test Documentation

- **`CONTRIBUTING_TESTS.md`**: Comprehensive guide for writing and maintaining tests
- **`TEST_POC_FRONTEND.md`**: PoC frontend testing guide
- **`TEST_POC_UI.md`**: PoC UI testing guide
- **`TEST_WEB_UI.md`**: Web UI testing guide

### Test Scripts

- **`test_poc_frontend.sh`**: Frontend test script
- **`test_poc_quick.sh`**: Quick validation script
- **`run_tests.sh`**: Main test execution script

### Test Outputs

- **`results/`**: Test execution logs, JSON/HTML reports, and performance metrics
- **`outputs/`**: Legacy test outputs and historical data
- **`test_outputs/`**: Test-generated data files and archives

## Integration Points

- Tests validate API endpoints
- Tests verify submission flows
- Tests check RAG functionality
- Tests validate blockchain integration

## Development Guidelines

- Write real tests for new functionality (no mocking)
- Follow test-driven development (TDD) with real dependencies
- Test both happy paths and error scenarios using real implementations
- Keep tests maintainable and readable
- Use automatic dependency management and service startup
- Document test dependencies and isolation requirements
- Never skip tests - ensure dependencies are available or installable

## Common Patterns

- Unit tests for individual functions
- Integration tests for component interactions
- End-to-end tests for complete flows
- API endpoint testing
- Error scenario testing

## File Structure

```
tests/
├── test_*.py                    # Test modules
├── *.sh                         # Test execution scripts
├── results/                     # Test reports and outputs
├── outputs/                     # Legacy test data
├── AGENTS.md                    # This documentation
├── CONTRIBUTING_TESTS.md        # Testing guidelines
├── test_config.json             # Test configuration
└── conftest.py                  # Pytest configuration
```

## Test Categories

| Category | Count | Purpose |
|----------|-------|---------|
| Unit Tests | ~15 | Individual component testing |
| Integration Tests | ~8 | Component interaction testing |
| End-to-End Tests | ~3 | Complete workflow testing |
| Performance Tests | ~2 | Load and scalability testing |
| Security Tests | ~1 | Security validation |

## Blueprint Alignment

### Testing the Complete Workflow ([Blueprint §7](docs/Blueprint for Syntheverse))
- **End-to-End Validation**: `test_full_submission_flow.py` + `test_submission_flow.py` validate complete PoC pipeline
- **Component Integration**: `test_poc_api.py` + `test_frontend_integration.py` test API and UI integration
- **Blockchain Validation**: `test_blockchain.py` verifies Layer 1 registration and token allocation
- **Archive-First Testing**: All tests validate immediate storage and redundancy detection

### PoC Evaluation Testing ([Blueprint §1.3](docs/Blueprint for Syntheverse))
- **Hydrogen Holographic Scoring**: `test_core_modules.py` validates 0-10,000 scoring across novelty/density/coherence/alignment
- **AI Integration Testing**: `test_rag_api.py` + `test_rag_timeout.py` test GROQ API integration
- **Evaluation Engine**: `test_core_modules.py` tests the complete Layer 2 evaluation pipeline

### Tokenomics Testing ([Blueprint §3.3](docs/Blueprint for Syntheverse))
- **SYNTH Allocation**: Tests validate epoch-based distribution and metallic amplifications
- **Threshold Scaling**: Core/leaf contribution scaling from high-impact to supporting work
- **Operator Control**: Epoch and threshold management testing

### Financial Framework Testing ([Blueprint §4](docs/Blueprint for Syntheverse))
- **Registration Fees**: $200 per approved PoC validation (submissions free for evaluation)
- **Tier System**: Copper/Silver/Gold contribution package testing foundation

### Security & Reliability ([Blueprint §6](docs/Blueprint for Syntheverse))
- **Input Sanitization**: `test_security.py` prevents injection attacks and data exposure
- **Human Oversight**: Tests validate approval workflow and governance controls
- **Transparency**: On-chain auditability testing for SYNTH allocations

### AI Integration Testing ([Blueprint §5](docs/Blueprint for Syntheverse))
- **Archive Training**: All PoCs stored and validated for AI training data
- **GROQ API**: Required for evaluation services with timeout and error handling
- **Fractal Evaluation**: Measurable, reproducible hydrogen holographic methodology

### Test-Driven Development ([Blueprint Vision §0](docs/Blueprint for Syntheverse))
- **TDD Implementation**: Real implementations tested, no mocks (Blueprint compliance)
- **Real Dependencies**: Tests use actual services, APIs, and blockchain interactions
- **Continuous Validation**: Complete workflow testing ensures system reliability

### Implementation Status Validation
- **✅ Fully Tested**: Core evaluation pipeline, API endpoints, blockchain integration
- **🟡 Phase 2 Testing**: Metallic amplifications, contributor tiers, advanced workflows
- **📋 Test Coverage**: See `docs/BLUEPRINT_IMPLEMENTATION_STATUS.md` for current validation status

## Cross-References

- **Blueprint Document**: [docs/Blueprint for Syntheverse](../docs/Blueprint for Syntheverse) - Central system vision
- **Implementation Status**: [docs/BLUEPRINT_IMPLEMENTATION_STATUS.md](../docs/BLUEPRINT_IMPLEMENTATION_STATUS.md)
- **Test Framework**: [CONTRIBUTING_TESTS.md](CONTRIBUTING_TESTS.md) - Testing guidelines and standards
- **Parent**: [Root AGENTS.md](../AGENTS.md) - System overview
- **Related**:
  - [scripts/startup/AGENTS.md](../scripts/startup/AGENTS.md) - Service startup testing
  - [src/AGENTS.md](../src/AGENTS.md) - Code under test
  - [docs/AGENTS.md](../docs/AGENTS.md) - System documentation

