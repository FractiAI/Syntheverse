# Deployment Scripts

## Purpose

Scripts for deploying smart contracts to blockchain networks and managing deployments.

## Scripts

- **`deploy_contracts.py`**: Deploy smart contracts to blockchain

## Usage

### Deploy Contracts

```bash
cd scripts/deployment
python deploy_contracts.py
```

Or from project root:

```bash
python scripts/deployment/deploy_contracts.py
```

## Configuration

Set environment variables:
- `PRIVATE_KEY`: Private key for deployment (without 0x prefix)
- `ETHERSCAN_API_KEY`: Etherscan API key for verification
- `RPC_URL`: RPC endpoint for target network

## Networks

- **Local (Anvil)**: http://localhost:8545 (default)
- **Base Sepolia**: https://sepolia.base.org
- **Base Mainnet**: https://mainnet.base.org

## Contract Paths

The script looks for contracts at:
- `src/blockchain/contracts/artifacts/src/SYNTH.sol/SYNTH.json`
- `src/blockchain/contracts/artifacts/src/POCRegistry.sol/POCRegistry.json`

## Integration

- Deploys SYNTH token contract
- Deploys POCRegistry contract
- Verifies contracts on block explorer
- Stores deployment addresses

## Documentation

See `src/blockchain/contracts/README.md` for detailed deployment instructions.

