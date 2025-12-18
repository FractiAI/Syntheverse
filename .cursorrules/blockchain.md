# Blockchain Development Standards

## Foundry Development

### Project Structure
- `src/` - Solidity contracts
- `test/` - Test files
- `script/` - Deployment scripts
- `lib/` - Dependencies (git submodules)

### Testing
- Write tests in Solidity using Forge
- Test all public functions
- Test edge cases and error conditions
- Use fuzzing for complex logic
- Measure gas usage

### Deployment
- Use deployment scripts for consistency
- Store contract addresses in configuration
- Verify contracts on block explorers
- Document deployment addresses

## Hardhat Integration

### Configuration
- Configure networks in `hardhat.config.js`
- Set up environment variables for keys
- Configure compiler settings
- Set up verification for block explorers

### Scripts
- Use Hardhat scripts for deployment
- Implement upgrade patterns
- Handle network-specific logic
- Test deployments locally first

## Syntheverse Blockchain Architecture

### Layer 1 (Python Implementation)
- Implements blockchain logic in Python
- Manages epochs and token distribution
- Handles PoC submissions and evaluations
- Provides node interface for blockchain operations

### Smart Contracts (Solidity)
- `SYNTH.sol` - Internal accounting token
- `POCRegistry.sol` - Contribution registry
- Deployed on Base Layer 2
- Uses OpenZeppelin contracts for security

### Integration Points
- Layer 2 sends evaluation results to Layer 1
- Smart contracts register contributions on-chain
- Frontend connects to blockchain via Web3
- APIs interact with blockchain for registration

### Fee Structure
- First 3 submissions: FREE
- Subsequent submissions: $50 per certificate
- Gas fees: Minimal on Base (~$0.005)
- Fee collection in smart contracts

### Security Considerations
- Non-transferable tokens (internal accounting)
- Access control for token allocation
- Input validation on all functions
- Reentrancy protection
- Emergency controls for owner

### Testing Strategy
- Unit tests for contract logic
- Integration tests for full flow
- Test on Anvil (local) first
- Test on Base Sepolia (testnet)
- Security audit before mainnet








