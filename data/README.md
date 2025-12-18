# Runtime Blockchain State

This directory contains persistent blockchain state files for the Syntheverse Layer 1 implementation.

## Directory Contents

- `blockchain/` - Layer 1 blockchain state and configuration files

## Purpose

Stores runtime state for the blockchain Layer 1 system, including:
- Blockchain configuration and state
- Persistent node data
- Token allocation records
- Certificate registration data

## File Management

- Files in this directory are generated at runtime
- State files are preserved across system restarts
- Regular backups recommended for production deployments

## Related Documentation

- [Layer 1 Implementation](../../src/blockchain/layer1/AGENTS.md)
- [Blockchain Architecture](../../src/blockchain/AGENTS.md)
- [Tokenomics State](../../src/core/layer2/tokenomics_state.py)
