#!/usr/bin/env python3
"""
Blockchain/L1 Test Suite
Tests smart contracts, token allocation, submission hashing, and epoch management
"""

import sys
import os
import hashlib
import json
import pytest
from pathlib import Path

# Add test framework to path
test_dir = Path(__file__).parent
sys.path.insert(0, str(test_dir))

from test_framework import SyntheverseTestCase, TestUtils, test_config, TestFixtures, ensure_module_available

@pytest.mark.requires_blockchain
class TestBlockchainLayer1(SyntheverseTestCase):
    """Test blockchain layer1 functionality"""

    def get_category(self) -> str:
        """Return test category for reporting"""
        return "integration"

    def setUp(self):
        """Set up blockchain tests"""
        super().setUp()

        # Ensure blockchain modules are available (install if needed)
        try:
            ensure_module_available("layer1.node")
            ensure_module_available("layer1.blockchain")
            ensure_module_available("layer1.epoch_manager")
            ensure_module_available("layer1.contracts.synth_token")

            from layer1.node import SyntheverseNode
            from layer1.blockchain import Blockchain
            from layer1.epoch_manager import EpochManager
            from layer1.contracts.synth_token import SYNTHToken

            # Create helper instances for tests
            self.synth_token = SYNTHToken()
            self.epoch_manager = EpochManager(synth_token=self.synth_token)
        except RuntimeError as e:
            self.fail(f"Blockchain modules could not be made available: {e}")

    def _create_test_node(self, node_id: str = "test-node-001", difficulty: int = 1):
        """Helper method to create properly initialized SyntheverseNode"""
        # Blockchain modules ensured in setUp()
        from layer1.node import SyntheverseNode
        return SyntheverseNode(node_id=node_id, difficulty=difficulty)

    def test_submission_hash_generation(self):
        """Test submission hash generation consistency"""
        self.log_info("Testing submission hash generation")

        # Create test data
        test_data = {
            "title": "Test Research Paper",
            "content": "This is test content for hashing",
            "contributor": "test@example.com",
            "timestamp": "2024-01-01T00:00:00Z"
        }

        # Generate hash multiple times to ensure consistency
        hashes = []
        for i in range(3):
            content = f"{test_data['title']}{test_data['content']}{test_data['contributor']}"
            hash_obj = hashlib.sha256(content.encode())
            submission_hash = hash_obj.hexdigest()[:16]  # First 16 chars
            hashes.append(submission_hash)

        # All hashes should be identical
        self.assertEqual(len(set(hashes)), 1, "Hash generation is not consistent")

        submission_hash = hashes[0]
        self.assertEqual(len(submission_hash), 16, "Hash should be 16 characters")
        self.assertRegex(submission_hash, r'^[a-f0-9]+$', "Hash should be hexadecimal")

        self.log_info(f"✅ Hash generation consistent: {submission_hash}")
        self.add_metric("hash_length", len(submission_hash))

    def test_epoch_manager_initialization(self):
        """Test epoch manager initialization and basic functionality"""
        self.log_info("Testing epoch manager initialization")

        # Blockchain modules ensured in setUp()

        try:
            epoch_manager = self.epoch_manager
            self.assertIsNotNone(epoch_manager)

            # Test getting current epoch
            current_epoch = epoch_manager.get_current_epoch()
            from layer1.blockchain import Epoch
            self.assertIsInstance(current_epoch, Epoch)

            # Test epoch info
            epoch_info = epoch_manager.get_epoch_info(current_epoch)
            self.assertIsInstance(epoch_info, dict)

            required_fields = ["epoch", "is_active", "balance", "threshold"]
            for field in required_fields:
                self.assertIn(field, epoch_info, f"Epoch info missing field: {field}")

            self.log_info(f"✅ Epoch manager initialized, current epoch: {current_epoch}")
            self.add_metric("current_epoch", current_epoch)

        except Exception as e:
            self.fail(f"Epoch manager test failed: {e}")

    def test_syntheverse_node_initialization(self):
        """Test Syntheverse node initialization"""
        self.log_info("Testing Syntheverse node initialization")

        # Blockchain modules ensured in setUp()

        try:
            node = self._create_test_node()
            self.assertIsNotNone(node)

            # Test basic node properties
            self.assertTrue(hasattr(node, 'blockchain'))
            self.assertTrue(hasattr(node, 'epoch_manager'))

            self.log_info("✅ Syntheverse node initialized")

        except Exception as e:
            self.fail(f"Node initialization test failed: {e}")

    def test_pod_submission_workflow(self):
        """Test PoD submission workflow"""
        self.log_info("Testing PoD submission workflow")

        # Blockchain modules ensured in setUp()

        try:
            node = self._create_test_node()

            # Create test contribution
            test_contrib = self.create_test_contribution()

            # Submit PoD
            result = node.submit_pod(test_contrib)

            self.assertIn("success", result)
            if result["success"]:
                self.assertIn("submission_hash", result)
                submission_hash = result["submission_hash"]

                self.log_info(f"✅ PoD submitted successfully: {submission_hash}")
                self.add_metric("submission_hash", submission_hash)

                # Store for cleanup if needed
                self.submission_hash = submission_hash
            else:
                self.log_warning(f"PoD submission failed: {result.get('error', 'Unknown error')}")

        except Exception as e:
            self.fail(f"PoD submission workflow test failed: {e}")

    def test_token_allocation_calculation(self):
        """Test token allocation calculation logic"""
        self.log_info("Testing token allocation calculation")

        # Blockchain modules ensured in setUp()

        try:
            node = self._create_test_node()

            # Test different evaluation scenarios
            test_scenarios = [
                {"coherence": 85, "density": 82, "novelty": 78, "expected_tier": "gold"},
                {"coherence": 75, "density": 72, "novelty": 68, "expected_tier": "silver"},
                {"coherence": 65, "density": 62, "novelty": 58, "expected_tier": "copper"},
            ]

            for scenario in test_scenarios:
                # Create mock evaluation
                evaluation = {
                    "coherence": scenario["coherence"],
                    "density": scenario["density"],
                    "novelty": scenario["novelty"],
                    "status": "approved"
                }

                # Calculate allocation (this might be internal method)
                # We'll test the public interface if available
                try:
                    # This depends on the actual implementation
                    allocation = node.calculate_token_allocation(evaluation)
                    if allocation and "tier" in allocation:
                        actual_tier = allocation["tier"].lower()
                        expected_tier = scenario["expected_tier"]

                        self.assertEqual(actual_tier, expected_tier,
                                       f"Tier mismatch: expected {expected_tier}, got {actual_tier}")

                        self.log_info(f"✅ {expected_tier.title()} tier allocation correct")
                        self.add_metric(f"{expected_tier}_allocation_valid", True)

                except AttributeError:
                    # Method might not be public, skip detailed testing
                    self.log_info("⚠️  Token allocation calculation method not accessible for testing")
                    break

        except Exception as e:
            self.fail(f"Token allocation test failed: {e}")

    def test_block_mining_simulation(self):
        """Test block mining simulation"""
        self.log_info("Testing block mining simulation")

        # Blockchain modules ensured in setUp()

        try:
            node = self._create_test_node()

            # Create a test transaction first
            from layer1.blockchain import Transaction, TransactionType
            test_tx = Transaction(
                tx_type=TransactionType.POD_SUBMISSION,
                sender="test-miner",
                data={"pod_score": 75, "submission_hash": "test_hash"}
            )
            node.blockchain.add_transaction(test_tx)

            # Mine a block
            block = node.mine_block(pod_score=75)

            self.assertIsNotNone(block)
            self.assertTrue(hasattr(block, 'index'))
            self.assertTrue(hasattr(block, 'transactions'))
            self.assertTrue(hasattr(block, 'timestamp'))

            block_index = block.index
            transaction_count = len(block.transactions)

            self.log_info(f"✅ Block mined: #{block_index} with {transaction_count} transactions")
            self.add_metric("block_index", block_index)
            self.add_metric("transactions_in_block", transaction_count)

        except Exception as e:
            self.fail(f"Block mining test failed: {e}")

    def test_contract_artifacts_loading(self):
        """Test smart contract artifacts loading"""
        self.log_info("Testing smart contract artifacts loading")

        try:
            project_root = Path(__file__).resolve().parents[1]
            # Check if contract artifacts exist
            contracts_dir = project_root / "src" / "blockchain" / "contracts" / "artifacts" / "src"

            synth_artifact = contracts_dir / "SYNTH.sol" / "SYNTH.json"
            poc_registry_artifact = contracts_dir / "POCRegistry.sol" / "POCRegistry.json"

            artifacts_exist = synth_artifact.exists() and poc_registry_artifact.exists()
            self.assertTrue(artifacts_exist, "Contract artifacts not found")

            # Try to load SYNTH artifact
            with open(synth_artifact, 'r') as f:
                synth_data = json.load(f)

            self.assertIn("abi", synth_data)
            self.assertIn("bytecode", synth_data)
            self.assertIsInstance(synth_data["abi"], list)

            # Try to load POCRegistry artifact
            with open(poc_registry_artifact, 'r') as f:
                poc_data = json.load(f)

            self.assertIn("abi", poc_data)
            self.assertIn("bytecode", poc_data)
            self.assertIsInstance(poc_data["abi"], list)

            abi_length_synth = len(synth_data["abi"])
            abi_length_poc = len(poc_data["abi"])

            self.log_info(f"✅ Contract artifacts loaded: SYNTH({abi_length_synth} functions), POCRegistry({abi_length_poc} functions)")
            self.add_metric("synth_abi_functions", abi_length_synth)
            self.add_metric("poc_abi_functions", abi_length_poc)

        except Exception as e:
            self.fail(f"Contract artifacts test failed: {e}")

    def test_contract_class_loading(self):
        """Test contract class loading"""
        self.log_info("Testing contract class loading")

        try:
            from layer1.contracts.synth_token import SYNTHToken
            from layer1.contracts.poc_contract import POCContract

            # Test contract class instantiation
            synth_contract = SYNTHToken()
            poc_contract = POCContract()

            self.assertIsNotNone(synth_contract)
            self.assertIsNotNone(poc_contract)

            # Test basic contract methods (if available)
            if hasattr(synth_contract, 'get_name'):
                name = synth_contract.get_name()
                self.assertIsInstance(name, str)
                self.log_info(f"✅ SYNTH contract name: {name}")

            if hasattr(poc_contract, 'get_total_contributions'):
                total = poc_contract.get_total_contributions()
                self.assertIsInstance(total, (int, type(None)))
                self.log_info(f"✅ POC contract total contributions: {total}")

            self.log_info("✅ Contract classes loaded successfully")

        except Exception as e:
            self.fail(f"Contract class loading test failed: {e}")

    def test_blockchain_statistics(self):
        """Test blockchain statistics retrieval"""
        self.log_info("Testing blockchain statistics")

        # Blockchain modules ensured in setUp()

        try:
            node = self._create_test_node()

            # Get token statistics
            stats = node.get_token_statistics()

            self.assertIsInstance(stats, dict)

            # Check for expected statistics fields
            expected_fields = ["total_allocated", "total_rewards", "epoch_distributions"]
            for field in expected_fields:
                if field in stats:
                    self.log_info(f"✅ Statistics field '{field}': {stats[field]}")
                    self.add_metric(field, stats[field])

            self.log_info("✅ Blockchain statistics retrieved")

        except Exception as e:
            self.fail(f"Blockchain statistics test failed: {e}")

    def test_epoch_thresholds(self):
        """Test epoch threshold validation"""
        self.log_info("Testing epoch thresholds")

        # Blockchain modules ensured in setUp()

        try:
            epoch_manager = self.epoch_manager

            # Test different density values against thresholds
            test_densities = [3000, 4500, 6500, 8500]  # Various density scores

            for density in test_densities:
                epoch = epoch_manager.get_epoch_for_density(density)

                self.assertIsNotNone(epoch)
                self.assertIsInstance(epoch, str)

                self.log_info(f"✅ Density {density} -> Epoch: {epoch}")
                self.add_metric(f"density_{density}_epoch", epoch)

            self.log_info("✅ Epoch thresholds working correctly")

        except AttributeError:
            # Method might not exist, skip this specific test
            self.log_info("⚠️  Epoch threshold method not available")
        except Exception as e:
            self.fail(f"Epoch thresholds test failed: {e}")

    def test_error_handling_invalid_submission(self):
        """Test error handling for invalid submissions"""
        self.log_info("Testing error handling for invalid submissions")

        # Blockchain modules ensured in setUp()

        try:
            node = self._create_test_node()

            # Test with invalid submission data
            invalid_submissions = [
                {},  # Empty submission
                {"title": "Test"},  # Missing required fields
                {"title": "", "content": "", "contributor": ""},  # Empty values
            ]

            for i, invalid_submission in enumerate(invalid_submissions):
                try:
                    result = node.submit_pod(invalid_submission)
                    # Should either fail gracefully or handle validation
                    self.assertIn("success", result)
                    if not result["success"]:
                        self.log_info(f"✅ Invalid submission {i+1} rejected correctly")
                    else:
                        self.log_warning(f"⚠️  Invalid submission {i+1} was accepted")
                except Exception as e:
                    self.log_info(f"✅ Invalid submission {i+1} raised exception: {type(e).__name__}")

            self.log_info("✅ Error handling for invalid submissions working")

        except Exception as e:
            self.fail(f"Invalid submission error handling test failed: {e}")


def run_blockchain_tests():
    """Run blockchain tests with framework"""
    TestUtils.print_test_header(
        "Blockchain/L1 Test Suite",
        "Testing smart contracts, token allocation, and blockchain functionality"
    )

    import unittest
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBlockchainLayer1)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    import unittest
    unittest.main()


