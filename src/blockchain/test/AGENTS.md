# Blockchain Test Suite

## Purpose

Solidity test files for smart contract validation and verification.

## Key Files

### SYNTH Token Tests (`SYNTH.t.sol`)

Comprehensive test suite for SYNTH token contract:

- Token deployment and initialization
- Minting and burning functionality
- Transfer operations and balances
- Access control and permissions
- Integration with POCRegistry

## Integration Points

- **Parent Directory**: [../AGENTS.md](../AGENTS.md) - Blockchain layer module
- **Contracts**: [../contracts/AGENTS.md](../contracts/AGENTS.md) - Smart contracts under test
- **Test Framework**: Foundry test framework for Solidity testing

## Development Guidelines

- Use Foundry/Forge testing framework
- Follow Solidity testing best practices
- Include both unit and integration tests
- Test edge cases and failure scenarios
- Maintain test coverage standards

## File Structure

```
test/
├── SYNTH.t.sol              # SYNTH token test suite
└── AGENTS.md                # This documentation
```

## Cross-References

- **Parent**: [blockchain/AGENTS.md](../AGENTS.md) - Blockchain layer overview
- **Related**:
  - [contracts/AGENTS.md](../contracts/AGENTS.md) - Smart contracts under test
  - [tests/AGENTS.md](../../../tests/AGENTS.md) - Test framework documentation
