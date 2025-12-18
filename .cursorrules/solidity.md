# Solidity Smart Contract Standards

## Code Style

### Naming Conventions
- Contracts: PascalCase (e.g., `POCRegistry`)
- Functions: camelCase (e.g., `submitContribution`)
- Variables: camelCase (e.g., `contributionCount`)
- Constants: UPPER_SNAKE_CASE (e.g., `MAX_SUPPLY`)
- Events: PascalCase (e.g., `ContributionSubmitted`)

### Layout
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

// Imports
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

// Interfaces
interface IRegistry {
    function register(address) external;
}

// Libraries
library Math {
    function add(uint256 a, uint256 b) internal pure returns (uint256) {
        return a + b;
    }
}

// Contracts
contract MyContract {
    // State variables
    uint256 public totalSupply;
    
    // Events
    event Transfer(address indexed from, address indexed to, uint256 value);
    
    // Modifiers
    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }
    
    // Constructor
    constructor() {
        // ...
    }
    
    // Functions
    function publicFunction() public {
        // ...
    }
    
    function internalFunction() internal {
        // ...
    }
}
```

## Security Best Practices

### Access Control
- Use OpenZeppelin's `Ownable` or `AccessControl`
- Implement role-based access control
- Validate all inputs
- Use `require()` for user-facing errors
- Use `assert()` for internal invariants

### Reentrancy Protection
- Use OpenZeppelin's `ReentrancyGuard`
- Follow checks-effects-interactions pattern
- Be cautious with external calls
- Use `transfer()` instead of `call()` when possible

### Integer Overflow
- Use Solidity 0.8+ (built-in overflow protection)
- Use SafeMath for older versions
- Validate arithmetic operations
- Check for underflow conditions

### Gas Optimization
- Use `uint256` for storage (not smaller types)
- Pack structs efficiently
- Use events instead of storage for logs
- Cache storage variables in memory
- Use `unchecked` blocks carefully

## Syntheverse Contract Patterns

### Token Contracts
- Inherit from OpenZeppelin's `ERC20`
- Implement custom logic for internal accounting
- Use non-transferable pattern for SYNTH token
- Track epoch-based allocations

### Registry Contracts
- Store contribution hashes
- Emit events for all state changes
- Implement tiered fee structure
- Validate submissions before registration

### Testing
- Write comprehensive test suites
- Test edge cases and error conditions
- Use Foundry for fast testing
- Test gas usage
- Verify contract behavior on different networks

### Documentation
- Use NatSpec comments for all public functions
- Document state variables
- Explain complex logic
- Include usage examples








