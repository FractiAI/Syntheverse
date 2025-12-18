# Blockchain Test Suite

Smart contract testing framework and validation infrastructure for Syntheverse Layer 1.

## Overview

This directory contains the comprehensive testing suite for blockchain smart contracts, including unit tests, integration tests, and deployment validation for SYNTH token and POC registry contracts.

## Test Structure

### Contract Tests
```
test/
├── SynthToken.test.js      # SYNTH token contract tests
├── POCRegistry.test.js     # POC registry contract tests
├── deployment.test.js      # Deployment validation tests
└── integration.test.js     # Cross-contract integration tests
```

### Test Utilities
```
├── fixtures/               # Test data and fixtures
├── helpers/               # Test helper functions
├── utils/                 # Testing utilities
└── config/                # Test configuration
```

## Test Categories

### Unit Tests
Individual contract function testing with full coverage:
- Token minting and transfer functionality
- Access control and permission validation
- Mathematical calculations and edge cases
- Event emission and state changes

### Integration Tests
Cross-contract interaction and system-level validation:
- Token allocation through POC registration
- Multi-user contribution scenarios
- Epoch progression and threshold validation
- Gas optimization and performance testing

### Deployment Tests
Contract deployment and network validation:
- Constructor parameter validation
- Initial state verification
- Network-specific configuration testing
- Upgrade mechanism validation

## Test Execution

### Local Testing
```bash
# Install dependencies
npm install

# Start local blockchain
npx hardhat node

# Run all tests
npx hardhat test

# Run specific test file
npx hardhat test test/SynthToken.test.js

# Run with coverage
npx hardhat coverage
```

### CI/CD Integration
```yaml
# GitHub Actions example
- name: Run Contract Tests
  run: |
    npm install
    npx hardhat compile
    npx hardhat test --network localhost
```

## Test Configuration

### Hardhat Configuration
```javascript
// hardhat.config.js
require("@nomiclabs/hardhat-waffle");
require("solidity-coverage");

module.exports = {
  solidity: "0.8.19",
  networks: {
    hardhat: {
      chainId: 31337
    },
    localhost: {
      url: "http://127.0.0.1:8545",
      chainId: 31337
    }
  },
  paths: {
    tests: "./test"
  }
};
```

### Test Helpers
```javascript
// test/helpers.js
const { ethers } = require("hardhat");

async function deployContracts() {
  const [owner, user1, user2] = await ethers.getSigners();

  const SynthToken = await ethers.getContractFactory("SynthToken");
  const synthToken = await SynthToken.deploy();
  await synthToken.deployed();

  const POCRegistry = await ethers.getContractFactory("POCRegistry");
  const pocRegistry = await POCRegistry.deploy(synthToken.address);
  await pocRegistry.deployed();

  return { synthToken, pocRegistry, owner, user1, user2 };
}

module.exports = { deployContracts };
```

## Test Examples

### Token Contract Test
```javascript
const { expect } = require("chai");
const { deployContracts } = require("./helpers");

describe("SynthToken", function () {
  let synthToken, owner, user1;

  beforeEach(async function () {
    ({ synthToken, owner, user1 } = await deployContracts());
  });

  it("Should have correct initial supply", async function () {
    const totalSupply = await synthToken.totalSupply();
    expect(totalSupply).to.equal(ethers.utils.parseEther("90000000")); // 90M tokens
  });

  it("Should allow token transfers", async function () {
    const amount = ethers.utils.parseEther("100");
    await synthToken.transfer(user1.address, amount);

    const balance = await synthToken.balanceOf(user1.address);
    expect(balance).to.equal(amount);
  });
});
```

### Integration Test
```javascript
describe("POC Registration Flow", function () {
  let synthToken, pocRegistry, owner, contributor;

  beforeEach(async function () {
    ({ synthToken, pocRegistry, owner, contributor } = await deployContracts());
  });

  it("Should complete full POC registration", async function () {
    // 1. Register contribution
    const contributionId = "test-contribution-123";
    const score = 8500; // Gold level

    await pocRegistry.registerContribution(contributionId, score, contributor.address);

    // 2. Verify registration
    const registration = await pocRegistry.getContribution(contributionId);
    expect(registration.score).to.equal(score);
    expect(registration.metal).to.equal(2); // Gold = 2

    // 3. Check token allocation
    const allocation = await pocRegistry.calculateAllocation(contributionId);
    expect(allocation).to.be.gt(0);
  });
});
```

## Coverage Requirements

- **Statement Coverage**: Minimum 90% for all contracts
- **Branch Coverage**: Minimum 85% for conditional logic
- **Function Coverage**: 100% for all public functions
- **Line Coverage**: Minimum 90% overall

## Performance Testing

### Gas Usage Testing
```javascript
it("Should not exceed gas limits", async function () {
  const tx = await contract.expensiveOperation();
  const receipt = await tx.wait();

  expect(receipt.gasUsed).to.be.lt(3000000); // 3M gas limit
});
```

### Load Testing
```javascript
it("Should handle multiple registrations", async function () {
  const promises = [];
  for (let i = 0; i < 100; i++) {
    promises.push(
      pocRegistry.registerContribution(
        `contribution-${i}`,
        8000,
        contributors[i % contributors.length].address
      )
    );
  }

  await Promise.all(promises);
  // Verify all registrations completed successfully
});
```

## Documentation

- [AGENTS.md](AGENTS.md) - Detailed component documentation
- [FRACTAL.md](FRACTAL.md) - Fractal analysis and patterns
- [Hardhat Documentation](https://hardhat.org/docs) - Testing framework reference
- [Solidity Testing Best Practices](https://docs.soliditylang.org/en/latest/) - Contract testing guidelines
