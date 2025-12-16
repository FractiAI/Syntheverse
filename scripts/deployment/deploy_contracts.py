#!/usr/bin/env python3
"""
Simple contract deployment script for Syntheverse
Deploys SYNTH and POCRegistry contracts to Anvil
"""

import json
import time
from pathlib import Path
from web3 import Web3

def deploy_contracts():
    # Connect to Anvil
    w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))

    if not w3.is_connected():
        print("❌ Cannot connect to Anvil")
        return False

    print("✅ Connected to Anvil")

    # Get the first account (deployer)
    accounts = w3.eth.accounts
    deployer = accounts[0]
    print(f"📝 Deployer account: {deployer}")

    # Load SYNTH contract
    contracts_dir = Path("contracts")
    synth_artifact_path = contracts_dir / "artifacts" / "src" / "SYNTH.sol" / "SYNTH.json"

    if not synth_artifact_path.exists():
        print(f"❌ SYNTH artifact not found at {synth_artifact_path}")
        return False

    with open(synth_artifact_path) as f:
        synth_artifact = json.load(f)

    # Deploy SYNTH contract
    print("🚀 Deploying SYNTH contract...")
    synth_contract = w3.eth.contract(
        abi=synth_artifact['abi'],
        bytecode=synth_artifact['bytecode']
    )

    # Constructor params: initialSupply (90 trillion), epochDuration (1 week)
    initial_supply = 90_000_000_000_000 * 10**18  # 90T with 18 decimals
    epoch_duration = 60 * 60 * 24 * 7  # 1 week in seconds

    tx_hash = synth_contract.constructor(initial_supply, epoch_duration).transact({
        'from': deployer,
        'gas': 2000000
    })

    # Wait for transaction
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    synth_address = tx_receipt.contractAddress
    print(f"✅ SYNTH deployed at: {synth_address}")

    # Load POCRegistry contract
    poc_registry_artifact_path = contracts_dir / "artifacts" / "src" / "POCRegistry.sol" / "POCRegistry.json"

    if not poc_registry_artifact_path.exists():
        print(f"❌ POCRegistry artifact not found at {poc_registry_artifact_path}")
        return False

    with open(poc_registry_artifact_path) as f:
        poc_registry_artifact = json.load(f)

    # Deploy POCRegistry contract
    print("🚀 Deploying POCRegistry contract...")
    poc_registry_contract = w3.eth.contract(
        abi=poc_registry_artifact['abi'],
        bytecode=poc_registry_artifact['bytecode']
    )

    # Constructor params: synthAddress, pocEvaluator, treasury
    tx_hash = poc_registry_contract.constructor(
        synth_address,  # SYNTH token address
        deployer,       # PoC evaluator (deployer for now)
        deployer        # Treasury (deployer for now)
    ).transact({
        'from': deployer,
        'gas': 3000000
    })

    # Wait for transaction
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    poc_registry_address = tx_receipt.contractAddress
    print(f"✅ POCRegistry deployed at: {poc_registry_address}")

    # Update artifact files with deployed addresses
    synth_artifact['address'] = synth_address
    with open(synth_artifact_path, 'w') as f:
        json.dump(synth_artifact, f, indent=2)

    poc_registry_artifact['address'] = poc_registry_address
    with open(poc_registry_artifact_path, 'w') as f:
        json.dump(poc_registry_artifact, f, indent=2)

    print("\n🎉 CONTRACTS DEPLOYED SUCCESSFULLY!")
    print("=" * 50)
    print(f"SYNTH Token:     {synth_address}")
    print(f"POCRegistry:     {poc_registry_address}")
    print("\n📄 Artifact files updated with deployed addresses")

    return True

if __name__ == "__main__":
    deploy_contracts()
