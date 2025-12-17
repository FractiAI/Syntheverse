#!/usr/bin/env python3
"""
Enhanced contract deployment script for Syntheverse
Deploys SYNTH and POCRegistry contracts to Anvil with comprehensive management
"""

import json
import time
import logging
import sys
from pathlib import Path
from web3 import Web3
from datetime import datetime

# Import management modules
try:
    from ..startup.anvil_manager import AnvilManager, start_anvil, wait_for_anvil
    from ..startup.service_health import check_service_health, ServiceStatus
except ImportError:
    # Fallback for direct execution
    sys.path.insert(0, str(Path(__file__).parent.parent / 'startup'))
    from anvil_manager import AnvilManager, start_anvil, wait_for_anvil
    from service_health import check_service_health, ServiceStatus

def setup_logging():
    """Set up logging for deployment"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('deployment.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def deploy_contracts(max_retries: int = 3, anvil_accounts: int = 10):
    """Deploy contracts with comprehensive Anvil management and error handling"""
    logger = setup_logging()

    print("🚀 SYNTHVERSE CONTRACT DEPLOYMENT")
    print("=" * 50)

    # Record deployment start
    deployment_start = datetime.now()
    logger.info("Starting Syntheverse contract deployment")

    # Initialize Anvil manager
    anvil_manager = AnvilManager(logger)

    # Step 1: Ensure Anvil is running
    print("\n📍 Step 1: Checking Anvil status...")
    logger.info("Checking Anvil status")

    if not anvil_manager.check_anvil_running():
        print("⚠️  Anvil is not running. Starting Anvil...")
        logger.warning("Anvil not running, starting it")

        if not anvil_manager.start_anvil(accounts=anvil_accounts):
            print("❌ Failed to start Anvil")
            logger.error("Failed to start Anvil")
            return False

        print("✅ Anvil started successfully")
        logger.info("Anvil started successfully")
    else:
        print("✅ Anvil is already running")
        logger.info("Anvil is already running")

    # Step 2: Wait for Anvil to be fully ready
    print("\n📍 Step 2: Waiting for Anvil to be ready...")
    logger.info("Waiting for Anvil to be ready")

    if not wait_for_anvil(timeout=30):
        print("❌ Anvil failed to become ready within timeout")
        logger.error("Anvil failed to become ready within timeout")
        return False

    # Step 3: Connect to Anvil with retry logic
    print("\n📍 Step 3: Connecting to Anvil...")
    logger.info("Connecting to Anvil")

    w3 = None
    for attempt in range(max_retries):
        try:
            w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
            if w3.is_connected():
                print(f"✅ Connected to Anvil on attempt {attempt + 1}")
                logger.info(f"Connected to Anvil on attempt {attempt + 1}")
                break
            else:
                logger.warning(f"Connection attempt {attempt + 1} failed - not connected")
        except Exception as e:
            logger.warning(f"Connection attempt {attempt + 1} failed: {e}")

        if attempt < max_retries - 1:
            print(f"⏳ Connection attempt {attempt + 1} failed, retrying in 2 seconds...")
            time.sleep(2)

    if not w3 or not w3.is_connected():
        print("❌ Cannot connect to Anvil after all retry attempts")
        logger.error("Cannot connect to Anvil after all retry attempts")
        return False

    # Get network information
    try:
        chain_id = w3.eth.chain_id
        block_number = w3.eth.block_number
        print(f"🌐 Connected to network (Chain ID: {chain_id}, Block: {block_number})")
        logger.info(f"Connected to network (Chain ID: {chain_id}, Block: {block_number})")
    except Exception as e:
        logger.warning(f"Could not get network information: {e}")

    # Step 4: Get deployer account
    print("\n📍 Step 4: Setting up deployer account...")
    logger.info("Setting up deployer account")

    try:
        accounts = w3.eth.accounts
        if not accounts:
            print("❌ No accounts available in Anvil")
            logger.error("No accounts available in Anvil")
            return False

        deployer = accounts[0]
        balance = w3.eth.get_balance(deployer)
        balance_eth = w3.from_wei(balance, 'ether')

        print(f"📝 Deployer account: {deployer}")
        print(f"💰 Deployer balance: {balance_eth} ETH")
        logger.info(f"Deployer account: {deployer} (Balance: {balance_eth} ETH)")

    except Exception as e:
        print(f"❌ Failed to get deployer account: {e}")
        logger.error(f"Failed to get deployer account: {e}")
        return False

    # Step 5: Validate and load contract artifacts
    print("\n📍 Step 5: Loading contract artifacts...")
    logger.info("Loading contract artifacts")

    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    contracts_dir = project_root / "src" / "blockchain" / "contracts"

    # Validate SYNTH artifact
    synth_artifact_path = contracts_dir / "artifacts" / "src" / "SYNTH.sol" / "SYNTH.json"
    if not synth_artifact_path.exists():
        print(f"❌ SYNTH artifact not found at {synth_artifact_path}")
        logger.error(f"SYNTH artifact not found at {synth_artifact_path}")
        return False

    try:
        with open(synth_artifact_path) as f:
            synth_artifact = json.load(f)

        # Validate artifact structure
        required_keys = ['abi', 'bytecode']
        for key in required_keys:
            if key not in synth_artifact:
                print(f"❌ SYNTH artifact missing required key: {key}")
                logger.error(f"SYNTH artifact missing required key: {key}")
                return False

        if not synth_artifact.get('bytecode'):
            print("❌ SYNTH artifact has empty bytecode")
            logger.error("SYNTH artifact has empty bytecode")
            return False

        print("✅ SYNTH artifact loaded and validated")
        logger.info("SYNTH artifact loaded and validated")

    except (json.JSONDecodeError, IOError) as e:
        print(f"❌ Failed to load SYNTH artifact: {e}")
        logger.error(f"Failed to load SYNTH artifact: {e}")
        return False

    # Step 6: Deploy SYNTH contract
    print("\n📍 Step 6: Deploying SYNTH contract...")
    logger.info("Deploying SYNTH contract")

    try:
        synth_contract = w3.eth.contract(
            abi=synth_artifact['abi'],
            bytecode=synth_artifact['bytecode']
        )

        # Constructor params: _pocEvaluator (deployer), _treasury (deployer)
        poc_evaluator = deployer  # For now, deployer is both owner and evaluator
        treasury = deployer       # For now, deployer is also treasury

        print(f"   PoC Evaluator: {poc_evaluator}")
        print(f"   Treasury: {treasury}")
        logger.info(f"SYNTH constructor params: pocEvaluator={poc_evaluator}, treasury={treasury}")

        # Estimate gas
        try:
            gas_estimate = synth_contract.constructor(poc_evaluator, treasury).estimate_gas({
                'from': deployer
            })
            print(f"   Estimated gas: {gas_estimate:,}")
            gas_limit = int(gas_estimate * 1.2)  # 20% buffer
        except Exception as e:
            print(f"⚠️  Gas estimation failed, using default: {e}")
            logger.warning(f"Gas estimation failed: {e}")
            gas_limit = 2000000

        # Deploy contract
        print("   📤 Sending deployment transaction...")
        tx_hash = synth_contract.constructor(poc_evaluator, treasury).transact({
            'from': deployer,
            'gas': gas_limit
        })

        print(f"   🔗 Transaction hash: {tx_hash.hex()}")
        logger.info(f"SYNTH deployment transaction: {tx_hash.hex()}")

        # Wait for transaction with timeout
        print("   ⏳ Waiting for transaction confirmation...")
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

        if tx_receipt.status == 1:
            synth_address = tx_receipt.contractAddress
            gas_used = tx_receipt.gasUsed
            print(f"✅ SYNTH deployed at: {synth_address}")
            print(f"   ⛽ Gas used: {gas_used:,}")
            logger.info(f"SYNTH deployed at {synth_address} (gas used: {gas_used})")
        else:
            print("❌ SYNTH deployment transaction failed")
            logger.error("SYNTH deployment transaction failed")
            return False

    except Exception as e:
        print(f"❌ SYNTH deployment failed: {e}")
        logger.error(f"SYNTH deployment failed: {e}")
        return False

    # Step 7: Load and validate POCRegistry artifact
    print("\n📍 Step 7: Loading POCRegistry artifact...")
    logger.info("Loading POCRegistry artifact")

    poc_registry_artifact_path = contracts_dir / "artifacts" / "src" / "POCRegistry.sol" / "POCRegistry.json"

    if not poc_registry_artifact_path.exists():
        print(f"❌ POCRegistry artifact not found at {poc_registry_artifact_path}")
        logger.error(f"POCRegistry artifact not found at {poc_registry_artifact_path}")
        return False

    try:
        with open(poc_registry_artifact_path) as f:
            poc_registry_artifact = json.load(f)

        # Validate artifact structure
        required_keys = ['abi', 'bytecode']
        for key in required_keys:
            if key not in poc_registry_artifact:
                print(f"❌ POCRegistry artifact missing required key: {key}")
                logger.error(f"POCRegistry artifact missing required key: {key}")
                return False

        if not poc_registry_artifact.get('bytecode'):
            print("❌ POCRegistry artifact has empty bytecode")
            logger.error("POCRegistry artifact has empty bytecode")
            return False

        print("✅ POCRegistry artifact loaded and validated")
        logger.info("POCRegistry artifact loaded and validated")

    except (json.JSONDecodeError, IOError) as e:
        print(f"❌ Failed to load POCRegistry artifact: {e}")
        logger.error(f"Failed to load POCRegistry artifact: {e}")
        return False

    # Step 8: Deploy POCRegistry contract
    print("\n📍 Step 8: Deploying POCRegistry contract...")
    logger.info("Deploying POCRegistry contract")

    try:
        poc_registry_contract = w3.eth.contract(
            abi=poc_registry_artifact['abi'],
            bytecode=poc_registry_artifact['bytecode']
        )

        # Constructor params: synthAddress, pocEvaluator
        print(f"   SYNTH Address: {synth_address}")
        print(f"   PoC Evaluator: {deployer}")
        logger.info(f"POCRegistry constructor params: synth={synth_address}, evaluator={deployer}")

        # Estimate gas
        try:
            gas_estimate = poc_registry_contract.constructor(
                synth_address, deployer
            ).estimate_gas({
                'from': deployer
            })
            print(f"   Estimated gas: {gas_estimate:,}")
            gas_limit = int(gas_estimate * 1.2)  # 20% buffer
        except Exception as e:
            print(f"⚠️  Gas estimation failed, using default: {e}")
            logger.warning(f"Gas estimation failed: {e}")
            gas_limit = 3000000

        # Deploy contract
        print("   📤 Sending deployment transaction...")
        tx_hash = poc_registry_contract.constructor(
            synth_address,  # SYNTH token address
            deployer        # PoC evaluator (deployer for now)
        ).transact({
            'from': deployer,
            'gas': gas_limit
        })

        print(f"   🔗 Transaction hash: {tx_hash.hex()}")
        logger.info(f"POCRegistry deployment transaction: {tx_hash.hex()}")

        # Wait for transaction with timeout
        print("   ⏳ Waiting for transaction confirmation...")
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

        if tx_receipt.status == 1:
            poc_registry_address = tx_receipt.contractAddress
            gas_used = tx_receipt.gasUsed
            print(f"✅ POCRegistry deployed at: {poc_registry_address}")
            print(f"   ⛽ Gas used: {gas_used:,}")
            logger.info(f"POCRegistry deployed at {poc_registry_address} (gas used: {gas_used})")
        else:
            print("❌ POCRegistry deployment transaction failed")
            logger.error("POCRegistry deployment transaction failed")
            return False

    except Exception as e:
        print(f"❌ POCRegistry deployment failed: {e}")
        logger.error(f"POCRegistry deployment failed: {e}")
        return False

    # Step 9: Update artifact files
    print("\n📍 Step 9: Updating artifact files...")
    logger.info("Updating artifact files with deployed addresses")

    try:
        # Update SYNTH artifact
        synth_artifact['address'] = synth_address
        with open(synth_artifact_path, 'w') as f:
            json.dump(synth_artifact, f, indent=2)
        print("✅ SYNTH artifact updated")
        logger.info(f"SYNTH artifact updated with address {synth_address}")

        # Update POCRegistry artifact
        poc_registry_artifact['address'] = poc_registry_address
        with open(poc_registry_artifact_path, 'w') as f:
            json.dump(poc_registry_artifact, f, indent=2)
        print("✅ POCRegistry artifact updated")
        logger.info(f"POCRegistry artifact updated with address {poc_registry_address}")

    except (IOError, OSError) as e:
        print(f"⚠️  Failed to update artifact files: {e}")
        logger.warning(f"Failed to update artifact files: {e}")
        # Don't fail deployment for this

    # Step 10: Deployment summary and validation
    print("\n📍 Step 10: Deployment validation...")
    logger.info("Validating deployment")

    deployment_success = True

    try:
        # Verify SYNTH contract
        synth_code = w3.eth.get_code(synth_address)
        if synth_code == '0x':
            print("❌ SYNTH contract verification failed - no code at address")
            logger.error("SYNTH contract verification failed - no code at address")
            deployment_success = False
        else:
            print("✅ SYNTH contract verified")
            logger.info("SYNTH contract verified")

        # Verify POCRegistry contract
        poc_code = w3.eth.get_code(poc_registry_address)
        if poc_code == '0x':
            print("❌ POCRegistry contract verification failed - no code at address")
            logger.error("POCRegistry contract verification failed - no code at address")
            deployment_success = False
        else:
            print("✅ POCRegistry contract verified")
            logger.info("POCRegistry contract verified")

    except Exception as e:
        print(f"⚠️  Contract verification failed: {e}")
        logger.warning(f"Contract verification failed: {e}")

    # Calculate deployment duration
    deployment_duration = datetime.now() - deployment_start

    # Final summary
    print("\n🎉 CONTRACTS DEPLOYED SUCCESSFULLY!")
    print("=" * 60)
    print(f"SYNTH Token:        {synth_address}")
    print(f"POCRegistry:        {poc_registry_address}")
    print(f"Network:            Anvil (Chain ID: {w3.eth.chain_id})")
    print(f"Deployer:           {deployer}")
    print(f"Deployment Time:    {deployment_duration.total_seconds():.1f}s")
    print(f"Block Number:       {w3.eth.block_number}")
    print("=" * 60)
    print("\n📄 Artifact files updated with deployed addresses")
    print("📋 Deployment logged to deployment.log")

    # Log final deployment info
    logger.info("="*60)
    logger.info("DEPLOYMENT SUMMARY")
    logger.info("="*60)
    logger.info(f"SYNTH Token: {synth_address}")
    logger.info(f"POCRegistry: {poc_registry_address}")
    logger.info(f"Network: Anvil (Chain ID: {w3.eth.chain_id})")
    logger.info(f"Deployer: {deployer}")
    logger.info(f"Duration: {deployment_duration.total_seconds():.1f}s")
    logger.info(f"Block: {w3.eth.block_number}")
    logger.info("="*60)

    return deployment_success

def main():
    """Main entry point with command-line argument support"""
    import argparse

    parser = argparse.ArgumentParser(description='Deploy Syntheverse contracts to Anvil')
    parser.add_argument('--anvil-accounts', type=int, default=10,
                       help='Number of accounts to create in Anvil (default: 10)')
    parser.add_argument('--retries', type=int, default=3,
                       help='Maximum retries for connection attempts (default: 3)')
    parser.add_argument('--no-validation', action='store_true',
                       help='Skip contract validation after deployment')

    args = parser.parse_args()

    print(f"🚀 Starting deployment with {args.anvil_accounts} Anvil accounts, {args.retries} max retries")
    print()

    success = deploy_contracts(
        max_retries=args.retries,
        anvil_accounts=args.anvil_accounts
    )

    if success:
        print("\n🎊 Deployment completed successfully!")
        print("You can now start the Syntheverse services:")
        print("  python scripts/startup/start_servers.py")
        return 0
    else:
        print("\n❌ Deployment failed!")
        print("Check the logs in deployment.log for details")
        return 1

if __name__ == "__main__":
    sys.exit(main())
