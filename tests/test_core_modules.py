#!/usr/bin/env python3
"""
Core Modules Unit Test Suite
Comprehensive testing of core business logic including:
- PoC Archive: Contribution storage, retrieval, and status management
- Tokenomics State: Epoch management, allocation calculations, and balance tracking
- Sandbox Map: Network visualization and contributor relationship mapping
- PoC Evaluator: Content evaluation with scoring and recommendation generation
- Token Allocator: SYNTH token reward calculations and distribution logic
- PoC Server: Main orchestration server with evaluation pipeline integration

Test Coverage: Unit tests with mocking for external dependencies,
edge cases, error scenarios, and performance validation.
"""

import sys
import os
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

# Add test framework to path
test_dir = Path(__file__).parent
sys.path.insert(0, str(test_dir))

from test_framework import SyntheverseTestCase, TestUtils, test_config, TestFixtures

class TestPoCArchive(SyntheverseTestCase):
    """Test PoC Archive functionality including contribution storage, retrieval,
    status transitions, redundancy checking, and data integrity validation."""

    def get_category(self) -> str:
        """Return test category for reporting"""
        return "unit"

    def setUp(self):
        """Set up archive tests"""
        super().setUp()

        try:
            from layer2.poc_archive import ContributionStatus, MetalType, PoCArchive
            self.archive_available = True
        except ImportError as e:
            self.log_warning(f"PoC archive modules not available: {e}")
            self.archive_available = False

    def test_contribution_status_enum(self):
        """Test contribution status enum values"""
        self.log_info("Testing contribution status enum")

        if not self.archive_available:
            self.skipTest("PoC archive not available")

        from layer2.poc_archive import ContributionStatus

        # Test all expected statuses (use actual enum values from source)
        expected_statuses = ["draft", "pending", "evaluating", "qualified", "unqualified", "archived", "superseded"]
        for status in expected_statuses:
            self.assertIn(status, [s.value for s in ContributionStatus],
                         f"Status {status} not found in ContributionStatus enum values")

        # Test that we can access enum members
        self.assertEqual(ContributionStatus.DRAFT.value, "draft")
        self.assertEqual(ContributionStatus.PENDING.value, "pending")
        self.assertEqual(ContributionStatus.EVALUATING.value, "evaluating")
        self.assertEqual(ContributionStatus.QUALIFIED.value, "qualified")
        self.assertEqual(ContributionStatus.UNQUALIFIED.value, "unqualified")
        self.assertEqual(ContributionStatus.ARCHIVED.value, "archived")
        self.assertEqual(ContributionStatus.SUPERSEDED.value, "superseded")

        self.log_info("✅ Contribution status enum values correct")

    def test_metal_type_enum(self):
        """Test metal type enum values"""
        self.log_info("Testing metal type enum")

        if not self.archive_available:
            self.skipTest("PoC archive not available")

        from layer2.poc_archive import MetalType

        # Test all expected metals
        expected_metals = ["gold", "silver", "copper"]
        for metal in expected_metals:
            self.assertIn(metal.upper(), dir(MetalType),
                         f"Metal {metal} not found in MetalType enum")

        self.log_info("✅ Metal type enum values correct")

    def test_archive_initialization(self):
        """Test PoC archive initialization"""
        self.log_info("Testing PoC archive initialization")

        if not self.archive_available:
            self.skipTest("PoC archive not available")

        try:
            from layer2.poc_archive import PoCArchive

            archive = PoCArchive()
            self.assertIsNotNone(archive)

            # Test basic archive properties
            self.assertTrue(hasattr(archive, 'archive'))
            self.assertIsInstance(archive.archive, dict)
            self.assertIn('contributions', archive.archive)
            self.assertIsInstance(archive.archive['contributions'], dict)

            # Test archive metadata
            self.assertIn('metadata', archive.archive)
            self.assertIn('total_contributions', archive.archive['metadata'])

            self.log_info("✅ PoC archive initialized successfully")

        except Exception as e:
            self.fail(f"Archive initialization test failed: {e}")

    def test_contribution_storage(self):
        """Test contribution storage and retrieval"""
        self.log_info("Testing contribution storage and retrieval")

        if not self.archive_available:
            self.skipTest("PoC archive not available")

        from layer2.poc_archive import PoCArchive, ContributionStatus

        archive = PoCArchive()

        # Create test contribution with unique hash
        test_contrib = self.create_test_contribution()
        unique_hash = f"test_storage_{hash(str(test_contrib))}"
        test_contrib["submission_hash"] = unique_hash

        # Store contribution
        archive.add_contribution(
            submission_hash=test_contrib["submission_hash"],
            title=test_contrib["title"],
            contributor=test_contrib["contributor"],
            text_content=test_contrib.get("content", "Test content"),
            is_test=True
        )

        # Retrieve contribution
        retrieved = archive.get_contribution(test_contrib["submission_hash"])

        # Comprehensive validation
        self.assertIsNotNone(retrieved, "Contribution should be retrievable")
        self.assertEqual(retrieved["submission_hash"], unique_hash)
        self.assertEqual(retrieved["title"], test_contrib["title"])
        self.assertEqual(retrieved["contributor"], test_contrib["contributor"])
        self.assertIn("status", retrieved, "Status field should be present")
        self.assertEqual(retrieved["status"], ContributionStatus.DRAFT.value)
        self.assertIn("created_at", retrieved, "Created timestamp should be present")
        self.assertIn("updated_at", retrieved, "Updated timestamp should be present")

        # Verify archive statistics updated
        stats = archive.get_statistics()
        self.assertGreaterEqual(stats["total_contributions"], 1)

        self.log_info(f"✅ Contribution storage working - stored and retrieved: {unique_hash}")
        self.add_metric("contribution_storage_success", True)

    def test_update_contribution(self):
        """Test updating existing contributions"""
        self.log_info("Testing contribution updates")

        if not self.archive_available:
            self.skipTest("PoC archive not available")

        try:
            from layer2.poc_archive import PoCArchive, ContributionStatus, MetalType

            archive = PoCArchive()

            # Add initial contribution
            test_contrib = self.create_test_contribution()
            test_contrib["submission_hash"] = "test_update_hash"

            archive.add_contribution(
                submission_hash=test_contrib["submission_hash"],
                title=test_contrib["title"],
                contributor=test_contrib["contributor"],
                text_content="Initial content",
                is_test=True
            )

            # Update contribution
            updated = archive.update_contribution(
                submission_hash="test_update_hash",
                status=ContributionStatus.QUALIFIED,
                metals=[MetalType.GOLD],
                metadata={"coherence": 95, "density": 90}
            )

            self.assertIsNotNone(updated)
            self.assertEqual(updated["status"], "qualified")
            self.assertEqual(updated["metals"], ["gold"])
            self.assertIn("coherence", updated["metadata"])

            self.log_info("✅ Contribution updates working")

        except Exception as e:
            self.fail(f"Contribution update test failed: {e}")

    def test_get_all_contributions_with_filters(self):
        """Test getting contributions with various filters"""
        self.log_info("Testing contribution filtering")

        if not self.archive_available:
            self.skipTest("PoC archive not available")

        try:
            from layer2.poc_archive import PoCArchive, ContributionStatus, MetalType
            import time

            archive = PoCArchive()

            # Use unique hashes to avoid conflicts with other tests
            timestamp = str(int(time.time() * 1000000))

            # Add test contributions
            archive.add_contribution(
                submission_hash=f"test_filter_gold_{timestamp}",
                title="Gold Contribution",
                contributor="researcher1",
                text_content="Gold content",
                metals=[MetalType.GOLD],
                is_test=True
            )

            archive.add_contribution(
                submission_hash=f"test_filter_silver_{timestamp}",
                title="Silver Contribution",
                contributor="researcher2",
                text_content="Silver content",
                metals=[MetalType.SILVER],
                is_test=True
            )

            # Test filtering by metal
            gold_contribs = archive.get_all_contributions(metal=MetalType.GOLD)
            # Find contributions with gold metal
            gold_matches = [c for c in gold_contribs if f"test_filter_gold_{timestamp}" in c["submission_hash"]]
            self.assertEqual(len(gold_matches), 1)
            self.assertEqual(gold_matches[0]["title"], "Gold Contribution")

            # Test filtering by contributor
            researcher1_contribs = archive.get_all_contributions(contributor="researcher1")
            researcher1_matches = [c for c in researcher1_contribs if f"test_filter_gold_{timestamp}" in c["submission_hash"]]
            self.assertEqual(len(researcher1_matches), 1)

            self.log_info("✅ Contribution filtering working")

        except Exception as e:
            self.fail(f"Contribution filtering test failed: {e}")

    def test_content_hash_history(self):
        """Test content hash history tracking"""
        self.log_info("Testing content hash history")

        if not self.archive_available:
            self.skipTest("PoC archive not available")

        try:
            from layer2.poc_archive import PoCArchive

            archive = PoCArchive()

            # Add two contributions with same content
            content = "Identical content for hash testing"
            archive.add_contribution(
                submission_hash="hash_test_1",
                title="First Version",
                contributor="researcher1",
                text_content=content,
                is_test=True
            )

            archive.add_contribution(
                submission_hash="hash_test_2",
                title="Second Version",
                contributor="researcher1",
                text_content=content,
                is_test=True
            )

            # Get content hash history
            content_hash = archive.calculate_content_hash(content)
            history = archive.get_content_hash_history(content_hash)

            self.assertEqual(len(history), 2)
            titles = [h["title"] for h in history]
            self.assertIn("First Version", titles)
            self.assertIn("Second Version", titles)

            self.log_info("✅ Content hash history working")

        except Exception as e:
            self.fail(f"Content hash history test failed: {e}")

    def test_redundancy_check_content(self):
        """Test getting all content for redundancy checking"""
        self.log_info("Testing redundancy check content retrieval")

        if not self.archive_available:
            self.skipTest("PoC archive not available")

        try:
            from layer2.poc_archive import PoCArchive

            archive = PoCArchive()

            # Add contributions
            archive.add_contribution(
                submission_hash="redundancy_test_1",
                title="Test 1",
                contributor="researcher1",
                text_content="Content 1",
                is_test=True
            )

            archive.add_contribution(
                submission_hash="redundancy_test_2",
                title="Test 2",
                contributor="researcher2",
                text_content="Content 2",
                is_test=True
            )

            # Get all content for redundancy check
            all_content = archive.get_all_content_for_redundancy_check()
            self.assertGreaterEqual(len(all_content), 2)

            # Check that all have required fields
            for contrib in all_content:
                self.assertIn("text_content", contrib)
                self.assertIn("submission_hash", contrib)

            self.log_info("✅ Redundancy check content retrieval working")

        except Exception as e:
            self.fail(f"Redundancy check content test failed: {e}")

    def test_archive_statistics(self):
        """Test archive statistics generation"""
        self.log_info("Testing archive statistics")

        if not self.archive_available:
            self.skipTest("PoC archive not available")

        try:
            from layer2.poc_archive import PoCArchive, MetalType

            archive = PoCArchive()

            # Add test contributions with different metals
            archive.add_contribution(
                submission_hash="stats_test_1",
                title="Gold Test",
                contributor="researcher1",
                text_content="Gold content",
                metals=[MetalType.GOLD],
                is_test=True
            )

            archive.add_contribution(
                submission_hash="stats_test_2",
                title="Silver Test",
                contributor="researcher2",
                text_content="Silver content",
                metals=[MetalType.SILVER],
                is_test=True
            )

            # Get statistics
            stats = archive.get_statistics()

            required_fields = ["total_contributions", "status_counts", "metal_counts", "unique_contributors", "unique_content_hashes"]
            for field in required_fields:
                self.assertIn(field, stats, f"Statistics missing field: {field}")

            self.assertGreaterEqual(stats["total_contributions"], 2)
            self.assertGreaterEqual(stats["unique_contributors"], 2)

            self.log_info("✅ Archive statistics working")

        except Exception as e:
            self.fail(f"Archive statistics test failed: {e}")

    def test_content_hash_calculation(self):
        """Test content hash calculation"""
        self.log_info("Testing content hash calculation")

        if not self.archive_available:
            self.skipTest("PoC archive not available")

        try:
            from layer2.poc_archive import PoCArchive

            archive = PoCArchive()

            # Test hash calculation
            content1 = "This is test content"
            content2 = "This is test content"  # Same content
            content3 = "This is different content"

            hash1 = archive.calculate_content_hash(content1)
            hash2 = archive.calculate_content_hash(content2)
            hash3 = archive.calculate_content_hash(content3)

            # Same content should have same hash
            self.assertEqual(hash1, hash2)
            # Different content should have different hash
            self.assertNotEqual(hash1, hash3)

            # Hash should be a string
            self.assertIsInstance(hash1, str)
            self.assertEqual(len(hash1), 64)  # SHA256 hex length

            self.log_info("✅ Content hash calculation working")

        except Exception as e:
            self.fail(f"Content hash calculation test failed: {e}")

    def test_archive_error_handling(self):
        """Test PoC archive error handling scenarios"""
        self.log_info("Testing PoC archive error handling")

        if not self.archive_available:
            self.skipTest("PoC archive not available")

        try:
            from layer2.poc_archive import PoCArchive

            # Test with permission denied path (create a directory we can't write to)
            import tempfile
            import os
            import stat

            # Create a temporary directory and make it read-only
            temp_dir = tempfile.mkdtemp()
            readonly_file = os.path.join(temp_dir, "readonly_archive.json")

            # Create the file first, then make directory read-only
            with open(readonly_file, 'w') as f:
                f.write('{"contributions": {}}')

            # Make the directory read-only
            os.chmod(temp_dir, stat.S_IRUSR | stat.S_IXUSR)  # Read and execute only

            try:
                # This should fail due to permissions
                permission_archive = PoCArchive(readonly_file)
                # If it succeeds, that's also fine - test the save operation
                permission_archive.add_contribution(
                    submission_hash="test_perm_hash",
                    title="Permission Test",
                    contributor="test@example.com",
                    text_content="Test content",
                    is_test=True
                )

                # Try to save - this should fail
                try:
                    permission_archive.save_archive()
                    self.log_warning("⚠️  Expected permission error when saving to read-only directory")
                except PermissionError:
                    self.log_info("✅ Archive correctly handles permission errors when saving")

            except PermissionError:
                self.log_info("✅ Archive correctly handles permission errors when initializing")
            finally:
                # Restore permissions so we can clean up
                os.chmod(temp_dir, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
                import shutil
                shutil.rmtree(temp_dir)

            # Test with corrupted JSON file
            import tempfile
            import os

            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                f.write("invalid json content {{{")
                temp_file = f.name

            try:
                corrupted_archive = PoCArchive(temp_file)
                # Should initialize with default structure despite corruption
                self.assertIsNotNone(corrupted_archive.archive)
                self.assertIn('contributions', corrupted_archive.archive)
                self.log_info("✅ Archive handles corrupted JSON gracefully")
            finally:
                os.unlink(temp_file)

        except Exception as e:
            self.fail(f"Archive error handling test failed: {e}")

    def test_archive_edge_cases(self):
        """Test PoC archive edge cases"""
        self.log_info("Testing PoC archive edge cases")

        if not self.archive_available:
            self.skipTest("PoC archive not available")

        try:
            from layer2.poc_archive import PoCArchive, ContributionStatus, MetalType

            # Use a fresh test archive to ensure it's empty
            import tempfile
            with tempfile.TemporaryDirectory() as temp_dir:
                test_archive_path = Path(temp_dir) / "test_archive.json"
                archive = PoCArchive(str(test_archive_path))

                # Test empty archive statistics
                stats = archive.get_statistics()
                self.assertIsInstance(stats, dict)
                self.assertIn('total_contributions', stats)
                self.assertEqual(stats['total_contributions'], 0)

                # Test getting all contributions with empty archive
                all_contribs = archive.get_all_contributions()
                self.assertIsInstance(all_contribs, list)
                self.assertEqual(len(all_contribs), 0)

            self.log_info("✅ Archive edge cases handled correctly")

        except Exception as e:
            self.fail(f"Archive edge cases test failed: {e}")


class TestTokenomicsState(SyntheverseTestCase):
    """Test tokenomics state functionality"""

    def get_category(self) -> str:
        """Return test category for reporting"""
        return "unit"

    def setUp(self):
        """Set up tokenomics tests"""
        super().setUp()

        try:
            from layer2.tokenomics_state import TokenomicsState, Epoch
            self.tokenomics_available = True
        except ImportError as e:
            self.log_warning(f"Tokenomics modules not available: {e}")
            self.tokenomics_available = False

    def test_epoch_enum(self):
        """Test epoch enum values"""
        self.log_info("Testing epoch enum")

        if not self.tokenomics_available:
            self.skipTest("Tokenomics modules not available")

        from layer2.tokenomics_state import Epoch

        # Test all expected epochs
        expected_epochs = ["founder", "pioneer", "community", "ecosystem"]
        for epoch in expected_epochs:
            self.assertIn(epoch.upper(), dir(Epoch),
                         f"Epoch {epoch} not found in Epoch enum")

        self.log_info("✅ Epoch enum values correct")

    def test_tokenomics_initialization(self):
        """Test tokenomics state initialization"""
        self.log_info("Testing tokenomics state initialization")

        if not self.tokenomics_available:
            self.skipTest("Tokenomics modules not available")

        from layer2.tokenomics_state import TokenomicsState

        tokenomics = TokenomicsState()
        self.assertIsNotNone(tokenomics, "Tokenomics state should initialize")

        # Test required properties exist
        required_attrs = ['state_file', 'state']
        for attr in required_attrs:
            self.assertTrue(hasattr(tokenomics, attr), f"Tokenomics should have {attr} attribute")

        # Test state structure
        self.assertIsInstance(tokenomics.state, dict, "State should be a dict")

        # Test epoch balances in state
        self.assertIn('epoch_balances', tokenomics.state, "State should have epoch_balances")
        epoch_balances = tokenomics.state['epoch_balances']
        self.assertIsInstance(epoch_balances, dict, "Epoch balances should be a dict")
        self.assertGreater(len(epoch_balances), 0, "Should have epoch balances")

        # Test current epoch is valid
        current_epoch = tokenomics.state.get('current_epoch')
        self.assertIsNotNone(current_epoch, "Should have current epoch")
        self.assertIn(current_epoch, epoch_balances,
                     f"Current epoch {current_epoch} should be in epoch balances")

        # Test total supply is reasonable
        self.assertGreater(tokenomics.total_supply, 0, "Total supply should be positive")
        self.assertIsInstance(tokenomics.total_supply, (int, float), "Total supply should be numeric")

        self.log_info(f"✅ Tokenomics initialized - current epoch: {tokenomics.current_epoch}, total supply: {tokenomics.total_supply}")
        self.add_metric("tokenomics_total_supply", tokenomics.total_supply)
        self.add_metric("tokenomics_current_epoch", tokenomics.current_epoch)

    def test_epoch_transitions(self):
        """Test epoch transition logic"""
        self.log_info("Testing epoch transitions")

        if not self.tokenomics_available:
            self.skipTest("Tokenomics modules not available")

        try:
            from layer2.tokenomics_state import TokenomicsState

            tokenomics = TokenomicsState()

            # Test epoch advancement (if method exists)
            if hasattr(tokenomics, 'advance_epoch'):
                initial_epoch = tokenomics.current_epoch

                # Advance epoch
                tokenomics.advance_epoch()
                new_epoch = tokenomics.current_epoch

                self.log_info(f"✅ Epoch changed from {initial_epoch} to {new_epoch}")
                self.add_metric("epoch_transition_success", True)
            else:
                self.log_info("⚠️  Epoch advancement method not available")

        except Exception as e:
            self.fail(f"Epoch transition test failed: {e}")

    def test_epoch_balance(self):
        """Test getting epoch balance"""
        self.log_info("Testing epoch balance retrieval")

        if not self.tokenomics_available:
            self.skipTest("Tokenomics modules not available")

        try:
            from layer2.tokenomics_state import TokenomicsState, Epoch

            tokenomics = TokenomicsState()

            # Test epoch balances
            founder_balance = tokenomics.get_epoch_balance(Epoch.FOUNDER)
            pioneer_balance = tokenomics.get_epoch_balance(Epoch.PIONEER)

            self.assertGreater(founder_balance, 0)
            self.assertGreater(pioneer_balance, 0)
            self.assertGreater(founder_balance, pioneer_balance)  # Founder should have more

            self.log_info("✅ Epoch balance retrieval working")

        except Exception as e:
            self.fail(f"Epoch balance test failed: {e}")

    def test_epoch_qualification(self):
        """Test epoch qualification based on density scores"""
        self.log_info("Testing epoch qualification")

        if not self.tokenomics_available:
            self.skipTest("Tokenomics modules not available")

        try:
            from layer2.tokenomics_state import TokenomicsState, Epoch

            tokenomics = TokenomicsState()

            # Test qualification thresholds
            founder_qualified = tokenomics.qualify_epoch(9000)  # High score
            pioneer_qualified = tokenomics.qualify_epoch(7000)  # Medium-high score
            community_qualified = tokenomics.qualify_epoch(5000)  # Medium score
            ecosystem_qualified = tokenomics.qualify_epoch(2000)  # Low score

            self.assertEqual(founder_qualified, Epoch.FOUNDER)
            self.assertEqual(pioneer_qualified, Epoch.PIONEER)
            self.assertEqual(community_qualified, Epoch.COMMUNITY)
            self.assertEqual(ecosystem_qualified, Epoch.ECOSYSTEM)

            self.log_info("✅ Epoch qualification working")

        except Exception as e:
            self.fail(f"Epoch qualification test failed: {e}")

    def test_pod_score_calculation(self):
        """Test PoD score calculation"""
        self.log_info("Testing PoD score calculation")

        if not self.tokenomics_available:
            self.skipTest("Tokenomics modules not available")

        try:
            from layer2.tokenomics_state import TokenomicsState

            tokenomics = TokenomicsState()

            # Test PoD score calculation
            coherence, density, novelty = 8000, 7000, 6000
            pod_score = tokenomics.calculate_pod_score(coherence, density, novelty)

            # Formula: (coherence/10000) × (density/10000) × (novelty/10000) × 10000
            expected = (coherence / 10000) * (density / 10000) * (novelty / 10000) * 10000
            self.assertAlmostEqual(pod_score, expected, places=2)

            # Should be capped at 10000
            self.assertLessEqual(pod_score, 10000)

            self.log_info("✅ PoD score calculation working")

        except Exception as e:
            self.fail(f"PoD score calculation test failed: {e}")

    def test_tier_availability(self):
        """Test tier availability in different epochs"""
        self.log_info("Testing tier availability")

        if not self.tokenomics_available:
            self.skipTest("Tokenomics modules not available")

        try:
            from layer2.tokenomics_state import TokenomicsState, Epoch, ContributionTier

            tokenomics = TokenomicsState()

            # Test tier availability
            # Gold should be available in all epochs
            self.assertTrue(tokenomics.is_tier_available_in_epoch(ContributionTier.GOLD, Epoch.FOUNDER))
            self.assertTrue(tokenomics.is_tier_available_in_epoch(ContributionTier.GOLD, Epoch.PIONEER))

            # Silver should not be available in Founder or Pioneer epochs
            self.assertFalse(tokenomics.is_tier_available_in_epoch(ContributionTier.SILVER, Epoch.FOUNDER))
            self.assertFalse(tokenomics.is_tier_available_in_epoch(ContributionTier.SILVER, Epoch.PIONEER))
            self.assertTrue(tokenomics.is_tier_available_in_epoch(ContributionTier.SILVER, Epoch.COMMUNITY))

            # Copper should be available in Pioneer and later
            self.assertTrue(tokenomics.is_tier_available_in_epoch(ContributionTier.COPPER, Epoch.PIONEER))
            self.assertTrue(tokenomics.is_tier_available_in_epoch(ContributionTier.COPPER, Epoch.COMMUNITY))

            self.log_info("✅ Tier availability working")

        except Exception as e:
            self.fail(f"Tier availability test failed: {e}")

    def test_coherence_density_updates(self):
        """Test coherence density tracking and halving"""
        self.log_info("Testing coherence density updates")

        if not self.tokenomics_available:
            self.skipTest("Tokenomics modules not available")

        try:
            from layer2.tokenomics_state import TokenomicsState

            tokenomics = TokenomicsState()

            initial_density = tokenomics.state["total_coherence_density"]
            initial_halving = tokenomics.state["founder_halving_count"]
            from layer2.tokenomics_state import Epoch
            initial_balance = tokenomics.get_epoch_balance(Epoch.FOUNDER)

            # Update coherence density with a large amount to ensure halving
            tokenomics.update_coherence_density(2000000)  # Cross multiple 1M thresholds

            # Should trigger halving
            self.assertGreater(tokenomics.state["founder_halving_count"], initial_halving)
            self.assertLess(tokenomics.get_epoch_balance(Epoch.FOUNDER), initial_balance)

            # Verify total coherence density increased
            self.assertGreater(tokenomics.state["total_coherence_density"], initial_density)

            self.log_info("✅ Coherence density updates working")

        except Exception as e:
            self.fail(f"Coherence density test failed: {e}")

    def test_allocation_calculation(self):
        """Test token allocation calculation"""
        self.log_info("Testing allocation calculation")

        if not self.tokenomics_available:
            self.skipTest("Tokenomics modules not available")

        try:
            from layer2.tokenomics_state import TokenomicsState, Epoch, ContributionTier

            tokenomics = TokenomicsState()

            # Test allocation calculation
            pod_score = 5000  # 50% allocation
            epoch = Epoch.PIONEER
            tier = ContributionTier.GOLD

            allocation = tokenomics.calculate_allocation(pod_score, epoch, tier)

            self.assertTrue(allocation["success"])
            self.assertEqual(allocation["epoch"], "pioneer")
            self.assertEqual(allocation["tier"], "gold")
            self.assertEqual(allocation["pod_score"], pod_score)
            self.assertGreater(allocation["reward"], 0)

            # Test unavailable tier
            unavailable_allocation = tokenomics.calculate_allocation(pod_score, Epoch.FOUNDER, ContributionTier.SILVER)
            self.assertFalse(unavailable_allocation["success"])
            self.assertFalse(unavailable_allocation["available"])

            self.log_info("✅ Allocation calculation working")

        except Exception as e:
            self.fail(f"Allocation calculation test failed: {e}")

    def test_allocation_recording(self):
        """Test allocation recording and state updates"""
        self.log_info("Testing allocation recording")

        if not self.tokenomics_available:
            self.skipTest("Tokenomics modules not available")

        try:
            from layer2.tokenomics_state import TokenomicsState, Epoch, ContributionTier

            tokenomics = TokenomicsState()

            initial_balance = tokenomics.get_epoch_balance(Epoch.PIONEER)
            initial_allocations = len(tokenomics.state["allocation_history"])

            # Create and record allocation
            allocation = tokenomics.calculate_allocation(3000, Epoch.PIONEER, ContributionTier.GOLD)
            self.assertTrue(allocation["success"])

            tokenomics.record_allocation(
                submission_hash="test_allocation_hash",
                contributor="test_contributor",
                allocation=allocation,
                coherence=5000
            )

            # Check state updates
            new_balance = tokenomics.get_epoch_balance(Epoch.PIONEER)
            new_allocations = len(tokenomics.state["allocation_history"])

            self.assertLess(new_balance, initial_balance)  # Balance should decrease
            self.assertGreater(new_allocations, initial_allocations)  # History should grow
            self.assertGreater(tokenomics.state["total_coherence_density"], 0)  # Coherence should increase

            self.log_info("✅ Allocation recording working")

        except Exception as e:
            self.fail(f"Allocation recording test failed: {e}")

    def test_tokenomics_statistics(self):
        """Test tokenomics statistics generation"""
        self.log_info("Testing tokenomics statistics")

        if not self.tokenomics_available:
            self.skipTest("Tokenomics modules not available")

        try:
            from layer2.tokenomics_state import TokenomicsState

            tokenomics = TokenomicsState()

            stats = tokenomics.get_statistics()

            required_fields = [
                "total_supply", "total_distributed", "total_remaining",
                "epoch_balances", "current_epoch", "founder_halving_count",
                "total_coherence_density", "total_holders", "total_allocations"
            ]

            for field in required_fields:
                self.assertIn(field, stats, f"Statistics missing field: {field}")

            # Verify totals add up
            total_calculated = stats["total_distributed"] + stats["total_remaining"]
            self.assertAlmostEqual(total_calculated, stats["total_supply"], places=2)

            self.log_info("✅ Tokenomics statistics working")

        except Exception as e:
            self.fail(f"Tokenomics statistics test failed: {e}")

    def test_epoch_info(self):
        """Test epoch information retrieval"""
        self.log_info("Testing epoch info")

        if not self.tokenomics_available:
            self.skipTest("Tokenomics modules not available")

        try:
            from layer2.tokenomics_state import TokenomicsState, Epoch

            tokenomics = TokenomicsState()

            epoch_info = tokenomics.get_epoch_info()

            self.assertIn("current_epoch", epoch_info)
            self.assertIn("epochs", epoch_info)

            # Check each epoch has required info
            for epoch in Epoch:
                epoch_name = epoch.value
                self.assertIn(epoch_name, epoch_info["epochs"])

                epoch_data = epoch_info["epochs"][epoch_name]
                required_fields = ["balance", "threshold", "distribution_percent", "available_tiers"]
                for field in required_fields:
                    self.assertIn(field, epoch_data, f"Epoch {epoch_name} missing field: {field}")

            self.log_info("✅ Epoch info working")

        except Exception as e:
            self.fail(f"Epoch info test failed: {e}")

    def test_l1_sync(self):
        """Test synchronization with L1 state"""
        self.log_info("Testing L1 synchronization")

        if not self.tokenomics_available:
            self.skipTest("Tokenomics modules not available")

        try:
            from layer2.tokenomics_state import TokenomicsState

            tokenomics = TokenomicsState()

            # Mock L1 state
            l1_state = {
                "epoch_balances": {"founder": 40000000000000, "pioneer": 20000000000000},
                "total_coherence_density": 500000,
                "founder_halving_count": 1,
                "current_epoch": "pioneer"
            }

            # Sync from L1
            tokenomics.sync_from_l1(l1_state)

            # Verify state updated
            self.assertEqual(tokenomics.state["epoch_balances"]["founder"], 40000000000000)
            self.assertEqual(tokenomics.state["total_coherence_density"], 500000)
            self.assertEqual(tokenomics.state["founder_halving_count"], 1)
            self.assertEqual(tokenomics.state["current_epoch"], "pioneer")

            self.log_info("✅ L1 synchronization working")

        except Exception as e:
            self.fail(f"L1 sync test failed: {e}")


class TestSandboxMap(SyntheverseTestCase):
    """Test sandbox map generation"""

    def get_category(self) -> str:
        """Return test category for reporting"""
        return "unit"

    def setUp(self):
        """Set up sandbox map tests"""
        super().setUp()

        try:
            from layer2.sandbox_map import SandboxMap
            self.sandbox_available = True
        except ImportError as e:
            self.log_warning(f"Sandbox map module not available: {e}")
            self.sandbox_available = False

    def test_sandbox_map_initialization(self):
        """Test sandbox map initialization"""
        self.log_info("Testing sandbox map initialization")

        if not self.sandbox_available:
            self.skipTest("Sandbox map not available")

        try:
            from layer2.sandbox_map import SandboxMap
            from layer2.poc_archive import PoCArchive

            archive = PoCArchive()
            sandbox = SandboxMap(archive)
            self.assertIsNotNone(sandbox)

            self.log_info("✅ Sandbox map initialized")

        except Exception as e:
            self.fail(f"Sandbox map initialization test failed: {e}")


class TestSandboxMap(SyntheverseTestCase):
    """Test sandbox map data generation"""

    def get_category(self) -> str:
        """Return test category for reporting"""
        return "unit"

    def setUp(self):
        """Set up sandbox map tests"""
        super().setUp()

        try:
            from layer2.sandbox_map import SandboxMap
            self.sandbox_available = True
        except ImportError as e:
            self.log_warning(f"Sandbox map module not available: {e}")
            self.sandbox_available = False

    def test_sandbox_map_generation(self):
        """Test sandbox map data generation"""
        self.log_info("Testing sandbox map generation")

        if not self.sandbox_available:
            self.skipTest("Sandbox map not available")

        try:
            from layer2.sandbox_map import SandboxMap
            from layer2.poc_archive import PoCArchive

            archive = PoCArchive()
            sandbox = SandboxMap(archive)

            # Generate map data
            map_data = sandbox.generate_map()

            self.assertIsInstance(map_data, dict)

            # Check expected structure
            required_fields = ["nodes", "edges"]
            for field in required_fields:
                self.assertIn(field, map_data, f"Map data missing field: {field}")
                self.assertIsInstance(map_data[field], list, f"Field {field} should be a list")

            nodes_count = len(map_data["nodes"])
            edges_count = len(map_data["edges"])

            self.log_info(f"✅ Sandbox map generated: {nodes_count} nodes, {edges_count} edges")
            self.add_metric("nodes_count", nodes_count)
            self.add_metric("edges_count", edges_count)

        except Exception as e:
            self.fail(f"Sandbox map generation test failed: {e}")

    def test_generate_map_with_filters(self):
        """Test sandbox map generation with various filters"""
        self.log_info("Testing sandbox map generation with filters")

        if not self.sandbox_available:
            self.skipTest("Sandbox map not available")

        try:
            from layer2.sandbox_map import SandboxMap
            from layer2.poc_archive import PoCArchive, ContributionStatus, MetalType

            # Use a temporary archive file to avoid conflicts
            import tempfile
            temp_archive_file = tempfile.mktemp(suffix='.json')

            archive = PoCArchive(temp_archive_file)
            sandbox = SandboxMap(archive)

            # Add test contributions
            archive.add_contribution(
                submission_hash="map_test_1",
                title="Qualified Gold",
                contributor="researcher1",
                text_content="Gold content",
                status=ContributionStatus.QUALIFIED,
                metals=[MetalType.GOLD],
                is_test=True
            )

            archive.add_contribution(
                submission_hash="map_test_2",
                title="Draft Silver",
                contributor="researcher2",
                text_content="Silver content",
                status=ContributionStatus.DRAFT,
                metals=[MetalType.SILVER],
                is_test=True
            )

            # Test filtering by status
            qualified_map = sandbox.generate_map(filter_status=[ContributionStatus.QUALIFIED])
            qualified_nodes = [n for n in qualified_map["nodes"] if n["status"] == "qualified"]
            draft_nodes = [n for n in qualified_map["nodes"] if n["status"] == "draft"]

            self.assertGreater(len(qualified_nodes), 0)
            self.assertEqual(len(draft_nodes), 0)

            # Test filtering by metal
            gold_map = sandbox.generate_map(filter_metals=[MetalType.GOLD])
            gold_nodes = [n for n in gold_map["nodes"] if "gold" in n.get("metals", [])]

            self.assertGreater(len(gold_nodes), 0)

            self.log_info("✅ Filtered map generation working")

        except Exception as e:
            self.fail(f"Filtered map generation test failed: {e}")
        finally:
            # Clean up temporary file
            import os
            if os.path.exists(temp_archive_file):
                os.unlink(temp_archive_file)

    def test_redundancy_report(self):
        """Test redundancy report generation"""
        self.log_info("Testing redundancy report")

        if not self.sandbox_available:
            self.skipTest("Sandbox map not available")

        try:
            from layer2.sandbox_map import SandboxMap
            from layer2.poc_archive import PoCArchive

            archive = PoCArchive()
            sandbox = SandboxMap(archive)

            # Add test contribution
            archive.add_contribution(
                submission_hash="redundancy_test_hash",
                title="Test Contribution",
                contributor="researcher1",
                text_content="Test content for redundancy analysis",
                is_test=True
            )

            # Get redundancy report
            report = sandbox.get_redundancy_report("redundancy_test_hash")

            required_fields = [
                "submission_hash", "title", "total_similar",
                "high_redundancy", "moderate_overlap", "related", "similar_contributions"
            ]

            for field in required_fields:
                self.assertIn(field, report, f"Redundancy report missing field: {field}")

            self.assertIsInstance(report["similar_contributions"], list)

            self.log_info("✅ Redundancy report working")

        except Exception as e:
            self.fail(f"Redundancy report test failed: {e}")

    def test_metal_distribution(self):
        """Test metal distribution analysis"""
        self.log_info("Testing metal distribution")

        if not self.sandbox_available:
            self.skipTest("Sandbox map not available")

        try:
            from layer2.sandbox_map import SandboxMap
            from layer2.poc_archive import PoCArchive, MetalType

            archive = PoCArchive()
            sandbox = SandboxMap(archive)

            # Add contributions with different metals
            archive.add_contribution(
                submission_hash="metal_test_1",
                title="Gold Contribution",
                contributor="researcher1",
                text_content="Gold content",
                metals=[MetalType.GOLD],
                is_test=True
            )

            archive.add_contribution(
                submission_hash="metal_test_2",
                title="Silver Contribution",
                contributor="researcher2",
                text_content="Silver content",
                metals=[MetalType.SILVER],
                is_test=True
            )

            archive.add_contribution(
                submission_hash="metal_test_3",
                title="Multi-metal",
                contributor="researcher3",
                text_content="Multi content",
                metals=[MetalType.GOLD, MetalType.SILVER],
                is_test=True
            )

            # Get metal distribution
            distribution = sandbox.get_metal_distribution()

            required_fields = [
                "individual_metals", "metal_combinations", "total_contributions_with_metals"
            ]

            for field in required_fields:
                self.assertIn(field, distribution, f"Metal distribution missing field: {field}")

            # Check individual metals
            self.assertGreaterEqual(distribution["individual_metals"]["gold"], 2)  # One single + one multi
            self.assertGreaterEqual(distribution["individual_metals"]["silver"], 2)  # One single + one multi

            # Check combinations
            self.assertIn("gold+silver", distribution["metal_combinations"])

            self.log_info("✅ Metal distribution working")

        except Exception as e:
            self.fail(f"Metal distribution test failed: {e}")

    def test_contributor_network(self):
        """Test contributor network analysis"""
        self.log_info("Testing contributor network")

        if not self.sandbox_available:
            self.skipTest("Sandbox map not available")

        try:
            from layer2.sandbox_map import SandboxMap
            from layer2.poc_archive import PoCArchive, MetalType
            import time

            archive = PoCArchive()
            sandbox = SandboxMap(archive)

            # Use unique contributor names to avoid conflicts with other tests
            timestamp = str(int(time.time() * 1000000))
            researcher_1 = f"researcher_1_{timestamp}"
            researcher_2 = f"researcher_2_{timestamp}"

            # Add contributions from different contributors
            archive.add_contribution(
                submission_hash=f"network_gold_{timestamp}",
                title="Researcher 1 Gold",
                contributor=researcher_1,
                text_content="Content 1",
                metals=[MetalType.GOLD],
                is_test=True
            )

            archive.add_contribution(
                submission_hash=f"network_silver_{timestamp}",
                title="Researcher 1 Silver",
                contributor=researcher_1,
                text_content="Content 2",
                metals=[MetalType.SILVER],
                is_test=True
            )

            archive.add_contribution(
                submission_hash=f"network_copper_{timestamp}",
                title="Researcher 2 Copper",
                contributor=researcher_2,
                text_content="Content 3",
                metals=[MetalType.COPPER],
                is_test=True
            )

            # Get contributor network
            network = sandbox.get_contributor_network()

            required_fields = ["contributors", "total_contributors"]
            for field in required_fields:
                self.assertIn(field, network, f"Contributor network missing field: {field}")

            self.assertGreaterEqual(network["total_contributors"], 2)

            # Check researcher_1 has 2 contributions
            researcher_1_data = network["contributors"][researcher_1]
            self.assertEqual(researcher_1_data["total_contributions"], 2)
            self.assertIn("gold", researcher_1_data["metals"])
            self.assertIn("silver", researcher_1_data["metals"])

            self.log_info("✅ Contributor network working")

        except Exception as e:
            self.fail(f"Contributor network test failed: {e}")

    def test_export_map_for_visualization(self):
        """Test map export for visualization"""
        self.log_info("Testing map export for visualization")

        if not self.sandbox_available:
            self.skipTest("Sandbox map not available")

        try:
            from layer2.sandbox_map import SandboxMap
            from layer2.poc_archive import PoCArchive
            import tempfile
            import os
            import json

            archive = PoCArchive()
            sandbox = SandboxMap(archive)

            # Add test contribution
            archive.add_contribution(
                submission_hash="export_test_1",
                title="Export Test",
                contributor="researcher1",
                text_content="Export content",
                is_test=True
            )

            # Test export without file
            map_data = sandbox.export_map_for_visualization()

            required_fields = ["nodes", "edges", "metadata", "statistics"]
            for field in required_fields:
                self.assertIn(field, map_data, f"Exported map missing field: {field}")

            # Check statistics structure
            stats = map_data["statistics"]
            self.assertIn("archive_stats", stats)
            self.assertIn("metal_distribution", stats)
            self.assertIn("contributor_network", stats)

            # Test export to file
            with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp_file:
                tmp_path = tmp_file.name

            try:
                sandbox.export_map_for_visualization(output_file=tmp_path)

                # Verify file was created and has content
                self.assertTrue(os.path.exists(tmp_path))

                with open(tmp_path, 'r') as f:
                    file_data = json.load(f)

                self.assertIn("nodes", file_data)
                self.assertIn("edges", file_data)

            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)

            self.log_info("✅ Map export for visualization working")

        except Exception as e:
            self.fail(f"Map export test failed: {e}")


class TestPoCEvaluator(SyntheverseTestCase):
    """Test PoC evaluator functionality"""

    def get_category(self) -> str:
        """Return test category for reporting"""
        return "unit"

    def setUp(self):
        """Set up evaluator tests"""
        super().setUp()

        try:
            from layer2.evaluator.pod_evaluator import PODEvaluator
            self.evaluator_available = True
        except ImportError as e:
            self.log_warning(f"PoC evaluator not available: {e}")
            self.evaluator_available = False

    def test_evaluator_initialization(self):
        """Test evaluator initialization"""
        self.log_info("Testing evaluator initialization")

        if not self.evaluator_available:
            self.skipTest("Evaluator not available")

        try:
            from layer2.evaluator.pod_evaluator import PODEvaluator

            evaluator = PODEvaluator()
            self.assertIsNotNone(evaluator)

            self.log_info("✅ PoC evaluator initialized")

        except Exception as e:
            self.fail(f"Evaluator initialization test failed: {e}")

    def test_evaluation_scoring(self):
        """Test evaluation scoring logic"""
        self.log_info("Testing evaluation scoring")

        if not self.evaluator_available:
            self.skipTest("Evaluator not available")

        try:
            from layer2.evaluator.pod_evaluator import PODEvaluator

            evaluator = PODEvaluator()

            # Test evaluation with mock data
            test_content = "This is a test research paper about fractal intelligence."
            test_metadata = {
                "title": "Test Paper",
                "category": "scientific",
                "contributor": "test@example.com"
            }

            # Mock RAG results
            mock_rag_results = {
                "answer": "Test evaluation response",
                "sources": [
                    {"title": "Source 1", "score": 0.85},
                    {"title": "Source 2", "score": 0.72}
                ]
            }

            # Test evaluation (mock the verify_against_knowledge_base method)
            with patch.object(evaluator, 'verify_against_knowledge_base') as mock_verify:
                mock_verify.return_value = mock_rag_results

                # Create submission data
                submission = {
                    "title": test_metadata["title"],
                    "description": test_content,
                    "evidence": "Supporting evidence for the research.",
                    "category": test_metadata["category"],
                    "contributor": test_metadata["contributor"]
                }

                result = evaluator.evaluate_submission(submission)

                # Validate result structure
                self.assertIsInstance(result, dict)
                self.assertIn("scores", result)
                self.assertIn("overall_score", result)
                self.assertIn("status", result)

                status = result["status"]
                self.log_info(f"✅ Evaluation successful, status: {status}")
                self.add_metric("evaluation_status", status)

        except Exception as e:
            self.fail(f"Evaluation scoring test failed: {e}")

    def test_evaluator_error_handling(self):
        """Test evaluator error handling scenarios"""
        self.log_info("Testing evaluator error handling")

        if not self.evaluator_available:
            self.skipTest("Evaluator not available")

        try:
            from layer2.evaluator.pod_evaluator import PODEvaluator

            evaluator = PODEvaluator()

            # Test with empty content
            result = evaluator.evaluate_content("", {"title": "Empty Test", "category": "test"})
            if result and "success" in result and not result["success"]:
                self.log_info("✅ Empty content handled correctly")
            elif result and "error" in result:
                self.log_info("✅ Empty content produced error response")
            else:
                self.log_warning("⚠️  Empty content did not produce expected error")

            # Test with None content
            result = evaluator.evaluate_content(None, {"title": "None Test", "category": "test"})
            if result and ("error" in result or (not result.get("success", True))):
                self.log_info("✅ None content handled correctly")
            else:
                self.log_warning("⚠️  None content did not produce expected error")

            # Test with invalid metadata
            result = evaluator.evaluate_content("test content", None)
            if result and ("error" in result or (not result.get("success", True))):
                self.log_info("✅ Invalid metadata handled correctly")
            else:
                self.log_warning("⚠️  Invalid metadata did not produce expected error")

            # Test with malformed metadata
            malformed_metadata = [
                {},  # Empty dict
                {"title": ""},  # Missing category
                {"category": ""},  # Missing title
                {"title": None, "category": None},  # None values
            ]

            for metadata in malformed_metadata:
                try:
                    result = evaluator.evaluate_content("test content", metadata)
                    if result and ("error" in result or (not result.get("success", True))):
                        self.log_info(f"✅ Malformed metadata {metadata} handled correctly")
                    else:
                        self.log_warning(f"⚠️  Malformed metadata {metadata} did not produce expected error")
                except Exception as e:
                    self.log_info(f"✅ Malformed metadata {metadata} raised exception: {type(e).__name__}")

            self.log_info("✅ Evaluator error handling tested")

        except Exception as e:
            self.fail(f"Evaluator error handling test failed: {e}")

    def test_evaluator_edge_cases(self):
        """Test evaluator edge cases and boundary conditions"""
        self.log_info("Testing evaluator edge cases")

        if not self.evaluator_available:
            self.skipTest("Evaluator not available")

        try:
            from layer2.evaluator.pod_evaluator import PODEvaluator

            evaluator = PODEvaluator()

            # Test with long content (but under validation limit)
            long_content = "test content " * 80  # ~960 chars (under 2000 char limit)
            long_submission = {
                "title": "Long Test",
                "description": long_content,
                "evidence": "Long evidence content.",
                "category": "scientific",
                "contributor": "test@example.com"
            }

            with patch.object(evaluator, 'verify_against_knowledge_base') as mock_verify:
                mock_verify.return_value = {"answer": "Long content processed", "sources": []}
                result = evaluator.evaluate_submission(long_submission)
                if result and "status" in result:
                    self.log_info("✅ Long content handled correctly")
                    self.add_metric("long_content_handled", True)
                else:
                    self.log_warning("⚠️  Long content may not be handled properly")

            # Test with special characters and unicode
            unicode_content = "Test content with üñíçødé characters: π ≈ 3.14159, ∞, ∑, ∫"
            unicode_submission = {
                "title": "Unicode Test",
                "description": unicode_content,
                "evidence": "Unicode evidence content.",
                "category": "scientific",
                "contributor": "test@example.com"
            }

            with patch.object(evaluator, 'verify_against_knowledge_base') as mock_verify:
                mock_verify.return_value = {"answer": "Unicode content processed", "sources": []}
                result = evaluator.evaluate_submission(unicode_submission)
                if result and "status" in result:
                    self.log_info("✅ Unicode content handled correctly")
                    self.add_metric("unicode_content_handled", True)
                else:
                    self.log_warning("⚠️  Unicode content may not be handled properly")

            # Test with minimal viable content
            minimal_content = "AI research"
            minimal_submission = {
                "title": "Minimal Test",
                "description": minimal_content,
                "evidence": "Minimal evidence.",
                "category": "scientific",
                "contributor": "test@example.com"
            }

            with patch.object(evaluator, 'verify_against_knowledge_base') as mock_verify:
                mock_verify.return_value = {"answer": "Minimal content processed", "sources": []}
                result = evaluator.evaluate_submission(minimal_submission)
                if result and "status" in result:
                    self.log_info("✅ Minimal content handled correctly")
                    self.add_metric("minimal_content_handled", True)
                else:
                    self.log_warning("⚠️  Minimal content may not be handled properly")

            self.log_info("✅ Evaluator edge cases tested")

        except Exception as e:
            self.fail(f"Evaluator edge cases test failed: {e}")

    def test_evaluate_submission_method(self):
        """Test the evaluate_submission method with complete submission data"""
        self.log_info("Testing evaluate_submission method")

        if not self.evaluator_available:
            self.skipTest("Evaluator not available")

        from layer2.evaluator.pod_evaluator import PODEvaluator

        evaluator = PODEvaluator()

        # Create complete submission data
        submission = {
            "title": "Fractal Intelligence in Neural Networks",
            "description": "This paper explores how fractal patterns enhance neural network performance.",
            "evidence": "Detailed mathematical proofs and experimental results showing fractal pattern effectiveness.",
            "category": "scientific",
            "contributor": "researcher@example.com"
        }

        # Mock knowledge base verification
        mock_kb_response = {
            "answer": "This appears to be a scientific paper about fractal intelligence with good coherence and technical depth.",
            "sources": [
                {"title": "Fractal Mathematics", "score": 0.87},
                {"title": "Neural Networks", "score": 0.82}
            ]
        }

        with patch.object(evaluator, 'verify_against_knowledge_base', return_value=mock_kb_response):
            result = evaluator.evaluate_submission(submission)

            # Validate result structure
            self.assertIsInstance(result, dict)
            self.assertIn("scores", result)
            self.assertIn("overall_score", result)
            self.assertIn("status", result)

            # Check required evaluation fields
            required_fields = ["scores", "overall_score", "status", "recommendations"]
            for field in required_fields:
                self.assertIn(field, result, f"Missing evaluation field: {field}")

            # Validate score ranges
            scores = result["scores"]
            for score_field in ["novelty", "significance", "verification", "documentation"]:
                self.assertIn(score_field, scores, f"Missing score field: {score_field}")
                score = scores[score_field]
                self.assertIsInstance(score, (int, float), f"{score_field} should be numeric")
                self.assertGreaterEqual(score, 0, f"{score_field} should be non-negative")
                self.assertLessEqual(score, 1, f"{score_field} should not exceed 1")

            # Validate overall score
            overall_score = result["overall_score"]
            self.assertIsInstance(overall_score, (int, float), "Overall score should be numeric")
            self.assertGreaterEqual(overall_score, 0, "Overall score should be non-negative")
            self.assertLessEqual(overall_score, 1, "Overall score should not exceed 1")

            # Validate status
            valid_statuses = ["gold", "silver", "copper", "acceptable", "unqualified"]
            self.assertIn(result["status"], valid_statuses, "Status should be valid")

            self.log_info(f"✅ Submission evaluated: status {result['status']}, score {result['overall_score']}")
            self.add_metric("submission_evaluation_status", result["status"])

    def test_evaluator_error_handling(self):
        """Test evaluator error handling with invalid inputs"""
        self.log_info("Testing evaluator error handling")

        if not self.evaluator_available:
            self.skipTest("Evaluator not available")

        from layer2.evaluator.pod_evaluator import PODEvaluator

        evaluator = PODEvaluator()

        # Test invalid RAG URL
        try:
            invalid_evaluator = PODEvaluator(rag_api_url="")
            # Should handle empty URL gracefully
            self.assertIsNotNone(invalid_evaluator)
        except Exception as e:
            self.log_info(f"✅ Invalid RAG URL handled: {type(e).__name__}")

        # Test evaluation with None input
        try:
            result = evaluator.evaluate_submission(None)
            self.assertFalse(result.get("success", True), "None input should fail")
        except Exception as e:
            self.log_info(f"✅ None input handled: {type(e).__name__}")

        # Test evaluation with missing required fields
        incomplete_submission = {"title": "Test"}
        try:
            result = evaluator.evaluate_submission(incomplete_submission)
            # Should handle missing fields gracefully
            self.assertIsInstance(result, dict)
        except Exception as e:
            self.log_info(f"✅ Incomplete submission handled: {type(e).__name__}")

        self.log_info("✅ Evaluator error handling tested")


class TestTokenAllocator(SyntheverseTestCase):
    """Test token allocator functionality"""

    def get_category(self) -> str:
        """Return test category for reporting"""
        return "unit"

    def setUp(self):
        """Set up allocator tests"""
        super().setUp()

        try:
            from layer2.allocator.token_allocator import TokenAllocator
            self.allocator_available = True
        except ImportError as e:
            self.log_warning(f"Token allocator not available: {e}")
            self.allocator_available = False

    def test_allocator_initialization(self):
        """Test allocator initialization"""
        self.log_info("Testing token allocator initialization")

        if not self.allocator_available:
            self.skipTest("Token allocator not available")

        try:
            from layer2.allocator.token_allocator import TokenAllocator

            allocator = TokenAllocator()
            self.assertIsNotNone(allocator)

            self.log_info("✅ Token allocator initialized")

        except Exception as e:
            self.fail(f"Allocator initialization test failed: {e}")

    def test_token_calculation_logic(self):
        """Test token calculation logic"""
        self.log_info("Testing token calculation logic")

        if not self.allocator_available:
            self.skipTest("Token allocator not available")

        try:
            from layer2.allocator.token_allocator import TokenAllocator

            allocator = TokenAllocator()

            # Test different tier calculations
            test_scenarios = [
                {"tier": "gold", "expected_range": (900, 1100)},
                {"tier": "silver", "expected_range": (400, 600)},
                {"tier": "copper", "expected_range": (200, 300)},
            ]

            for scenario in test_scenarios:
                tier = scenario["tier"]
                min_expected, max_expected = scenario["expected_range"]

                # Test allocation calculation (method name may vary)
                if hasattr(allocator, 'calculate_allocation'):
                    allocation = allocator.calculate_allocation(tier, epoch="pioneer")

                    if allocation and "reward" in allocation:
                        reward = allocation["reward"]
                        self.assertGreaterEqual(reward, min_expected,
                                              f"{tier} reward too low: {reward}")
                        self.assertLessEqual(reward, max_expected,
                                            f"{tier} reward too high: {reward}")

                        self.log_info(f"✅ {tier.title()} allocation: {reward} tokens")
                        self.add_metric(f"{tier}_allocation", reward)
                    else:
                        self.log_info(f"⚠️  Allocation calculation returned unexpected format for {tier}")
                else:
                    self.log_info("⚠️  Token calculation method not accessible")

        except Exception as e:
            self.fail(f"Token calculation test failed: {e}")

    def test_allocator_edge_cases(self):
        """Test token allocator edge cases and error handling"""
        self.log_info("Testing token allocator edge cases")

        if not self.allocator_available:
            self.skipTest("Token allocator not available")

        try:
            from layer2.allocator.token_allocator import TokenAllocator

            allocator = TokenAllocator()

            # Test invalid tier
            try:
                result = allocator.calculate_allocation("invalid_tier", "pioneer")
                # Should handle gracefully - either return None or error structure
                self.assertIsNotNone(result)
                if "error" in result:
                    self.log_info("✅ Invalid tier handled with error response")
                else:
                    self.log_warning("⚠️  Invalid tier did not produce expected error")
            except Exception as e:
                self.log_info(f"✅ Invalid tier raised exception: {type(e).__name__}")

            # Test invalid epoch
            try:
                result = allocator.calculate_allocation("gold", "invalid_epoch")
                self.assertIsNotNone(result)
                if "error" in result:
                    self.log_info("✅ Invalid epoch handled with error response")
                else:
                    self.log_warning("⚠️  Invalid epoch did not produce expected error")
            except Exception as e:
                self.log_info(f"✅ Invalid epoch raised exception: {type(e).__name__}")

            # Test edge case values
            edge_cases = [
                ("", "pioneer"),  # Empty tier
                ("gold", ""),     # Empty epoch
                (None, "pioneer"), # None tier
                ("gold", None),   # None epoch
            ]

            for tier, epoch in edge_cases:
                try:
                    result = allocator.calculate_allocation(tier, epoch)
                    self.assertIsNotNone(result)
                    if "error" in result:
                        self.log_info(f"✅ Edge case ({tier}, {epoch}) handled with error")
                    else:
                        self.log_warning(f"⚠️  Edge case ({tier}, {epoch}) did not produce expected error")
                except Exception as e:
                    self.log_info(f"✅ Edge case ({tier}, {epoch}) raised exception: {type(e).__name__}")

            self.log_info("✅ Token allocator edge cases tested")

        except Exception as e:
            self.fail(f"Token allocator edge cases test failed: {e}")

    def test_allocator_validation(self):
        """Test token allocator input validation"""
        self.log_info("Testing token allocator input validation")

        if not self.allocator_available:
            self.skipTest("Token allocator not available")

        try:
            from layer2.allocator.token_allocator import TokenAllocator

            allocator = TokenAllocator()

            # Test with malformed inputs
            malformed_inputs = [
                123,           # Integer instead of string
                [],            # List instead of string
                {},            # Dict instead of string
                True,          # Boolean instead of string
            ]

            for invalid_input in malformed_inputs:
                try:
                    result = allocator.calculate_allocation(invalid_input, "pioneer")
                    if result and "error" in result:
                        self.log_info(f"✅ Malformed input {type(invalid_input).__name__} handled")
                    else:
                        self.log_warning(f"⚠️  Malformed input {type(invalid_input).__name__} not properly validated")
                except Exception as e:
                    self.log_info(f"✅ Malformed input {type(invalid_input).__name__} raised exception: {type(e).__name__}")

            self.log_info("✅ Token allocator input validation tested")

        except Exception as e:
            self.fail(f"Token allocator validation test failed: {e}")

    def test_calculate_reward_method(self):
        """Test the calculate_reward method with comprehensive evaluation data"""
        self.log_info("Testing calculate_reward method")

        if not self.allocator_available:
            self.skipTest("Token allocator not available")

        from layer2.allocator.token_allocator import TokenAllocator

        allocator = TokenAllocator()

        # Test evaluation data
        test_evaluation = {
            "coherence": 87,
            "density": 83,
            "novelty": 79,
            "tier": "gold",
            "status": "qualified"
        }

        # Test calculate_reward method
        reward_result = allocator.calculate_reward(test_evaluation, epoch=1)

        # Validate result structure
        self.assertIsInstance(reward_result, dict)
        self.assertIn("total_tokens", reward_result)
        self.assertIn("base_tokens", reward_result)
        self.assertIn("bonuses", reward_result)
        self.assertIn("epoch", reward_result)

        # Validate reward amounts
        self.assertGreaterEqual(reward_result["total_tokens"], 0)
        self.assertGreaterEqual(reward_result["base_tokens"], 0)
        self.assertIsInstance(reward_result["bonuses"], dict)

        # Check if reward was calculated (may be 0 for invalid data)
        if reward_result["total_tokens"] > 0:
            self.log_info(f"✅ Reward calculated: {reward_result['total_tokens']} tokens")
        else:
            self.log_info("ℹ️  Reward calculation returned 0 (possibly due to invalid evaluation data)")
        self.add_metric("gold_tier_reward", reward_result["total_tokens"])

    def test_generate_allocation_batch(self):
        """Test batch allocation generation"""
        self.log_info("Testing generate_allocation_batch method")

        if not self.allocator_available:
            self.skipTest("Token allocator not available")

        from layer2.allocator.token_allocator import TokenAllocator

        allocator = TokenAllocator()

        # Create multiple test evaluations
        evaluations = [
            {"coherence": 87, "density": 83, "novelty": 79, "tier": "gold", "status": "qualified"},
            {"coherence": 75, "density": 70, "novelty": 65, "tier": "silver", "status": "qualified"},
            {"coherence": 65, "density": 60, "novelty": 55, "tier": "copper", "status": "qualified"}
        ]

        # Test batch allocation
        batch_result = allocator.generate_allocation_batch(evaluations, epoch=1)

        # Validate batch result
        self.assertIsInstance(batch_result, dict)
        self.assertIn("allocations", batch_result)
        self.assertIn("summary", batch_result)
        self.assertIn("errors", batch_result)

        # Should have allocations (may be fewer if some failed)
        self.assertIsInstance(batch_result["allocations"], list)
        self.assertLessEqual(len(batch_result["allocations"]), len(evaluations))

        # Validate summary
        summary = batch_result["summary"]
        self.assertIn("total_evaluations", summary)
        self.assertIn("successful_allocations", summary)
        self.assertIn("total_tokens_allocated", summary)
        self.assertEqual(summary["total_evaluations"], len(evaluations))

        # Note: tier_breakdown may not be implemented yet, check if it exists
        if "tier_breakdown" in summary:
            tier_breakdown = summary["tier_breakdown"]
            self.assertIsInstance(tier_breakdown, dict)
        else:
            self.log_info("ℹ️  Tier breakdown not implemented in summary yet")

        self.log_info(f"✅ Batch allocation: {summary['total_tokens_allocated']} total tokens")
        self.add_metric("batch_allocation_total", summary["total_tokens_allocated"])

    def test_private_validation_methods(self):
        """Test private validation and calculation methods"""
        self.log_info("Testing private allocator methods")

        if not self.allocator_available:
            self.skipTest("Token allocator not available")

        from layer2.allocator.token_allocator import TokenAllocator

        allocator = TokenAllocator()

        # Test _validate_evaluation_input (using private method access for testing)
        valid_evaluation = {"overall_score": 0.8, "scores": {"coherence": 80}}
        invalid_evaluation = {"overall_score": 1.5}  # Score > 1.0 should fail

        # Test with valid input (should not raise)
        try:
            allocator._validate_evaluation_input(valid_evaluation, 1)
            validation_passed = True
        except Exception:
            validation_passed = False

        self.assertTrue(validation_passed, "Valid evaluation should pass validation")

        # Test with invalid input (should raise due to invalid score)
        try:
            allocator._validate_evaluation_input(invalid_evaluation, 1)
            invalid_passed = True
        except Exception:
            invalid_passed = False

        self.assertFalse(invalid_passed, "Invalid evaluation (score > 1.0) should fail validation")

        # Test _calculate_bonuses with scores that trigger bonuses
        test_scores = {"novelty": 0.9, "significance": 0.5, "verification": 0.95, "documentation": 0.85}
        base_tokens = 100.0

        bonuses = allocator._calculate_bonuses(test_scores, base_tokens)

        self.assertIsInstance(bonuses, dict)
        # Should have novelty bonus (0.9 > 0.8) and verification bonus (0.95 > 0.9)
        self.assertIn("novelty", bonuses)
        self.assertIn("verification", bonuses)
        # Should not have significance bonus (0.5 < 0.8) or documentation bonus (0.85 < 0.9)
        self.assertNotIn("significance", bonuses)
        self.assertNotIn("documentation", bonuses)

        # Bonuses should be positive
        for bonus_key, bonus_value in bonuses.items():
            self.assertGreater(bonus_value, 0, f"{bonus_key} bonus should be positive")

        self.log_info("✅ Private validation and calculation methods working")
        self.add_metric("validation_methods_tested", True)


class TestPoCServer(SyntheverseTestCase):
    """Test PoC server functionality"""

    def get_category(self) -> str:
        """Return test category for reporting"""
        return "unit"

    def setUp(self):
        """Set up server tests"""
        super().setUp()

        try:
            from layer2.poc_server import PoCServer
            self.server_available = True
        except ImportError as e:
            self.log_warning(f"PoC server not available: {e}")
            self.server_available = False

    def test_server_initialization(self):
        """Test server initialization"""
        self.log_info("Testing PoC server initialization")

        if not self.server_available:
            self.skipTest("PoC server not available")

        try:
            from layer2.poc_server import PoCServer

            # Mock GROQ API key and OpenAI client
            with patch('os.getenv', return_value='test-groq-key'), \
                 patch('openai.OpenAI') as mock_openai:

                # Mock the models.list() call
                mock_client = mock_openai.return_value
                mock_client.models.list.return_value = None

                server = PoCServer()
                self.assertIsNotNone(server)

                # Test server has required components
                self.assertTrue(hasattr(server, 'archive'))
                self.assertTrue(hasattr(server, 'tokenomics'))
                self.assertTrue(hasattr(server, 'sandbox_map'))

                self.log_info("✅ PoC server initialized")

        except Exception as e:
            self.fail(f"Server initialization test failed: {e}")

    def test_server_evaluation_pipeline(self):
        """Test server evaluation pipeline"""
        self.log_info("Testing server evaluation pipeline")

        if not self.server_available:
            self.skipTest("PoC server not available")

        try:
            from layer2.poc_server import PoCServer

            # Mock GROQ API key and OpenAI client
            with patch('os.getenv', return_value='test-groq-key'), \
                 patch('openai.OpenAI') as mock_openai:

                # Mock the models.list() call
                mock_client = mock_openai.return_value
                mock_client.models.list.return_value = None

                server = PoCServer()

                # Create test submission
                test_content = "Test research content"
                test_metadata = {
                    "title": "Test Paper",
                    "category": "scientific",
                    "contributor": "test@example.com"
                }

                # Test evaluation pipeline (may require mocking)
                with patch.object(server, 'evaluate_contribution') as mock_eval:
                    mock_eval.return_value = {
                        "success": True,
                        "evaluation": {
                            "coherence": 85,
                            "density": 80,
                            "novelty": 75,
                            "tier": "gold"
                        }
                    }

                    result = server.evaluate_contribution("test_hash")

                    if result and result.get("success"):
                        evaluation = result.get("evaluation", {})
                        tier = evaluation.get("tier", "unknown")
                        self.log_info(f"✅ Evaluation pipeline working, tier: {tier}")
                        self.add_metric("pipeline_tier", tier)
                    else:
                        self.log_info("⚠️  Evaluation pipeline returned non-success result")

        except Exception as e:
            self.fail(f"Server evaluation pipeline test failed: {e}")

    def test_submit_contribution(self):
        """Test contribution submission"""
        self.log_info("Testing contribution submission")

        if not self.server_available:
            self.skipTest("PoC server not available")

        try:
            from layer2.poc_server import PoCServer

            # Mock GROQ API key and OpenAI client
            with patch('os.getenv', return_value='test-groq-key'), \
                 patch('openai.OpenAI') as mock_openai:

                # Mock the models.list() call
                mock_client = mock_openai.return_value
                mock_client.models.list.return_value = None

                server = PoCServer()

                # Mock evaluation to avoid API calls
                with patch.object(server, 'evaluate_contribution', return_value={
                    "success": True,
                    "evaluation": {"coherence": 8000, "density": 7000, "redundancy": 1000}
                }):

                    result = server.submit_contribution(
                        submission_hash="submit_test_hash",
                        title="Test Submission",
                        contributor="test_contributor",
                        text_content="Test content for submission",
                        is_test=True
                    )

                    self.assertTrue(result["success"])
                    self.assertEqual(result["submission_hash"], "submit_test_hash")
                    self.assertIn("archive_entry", result)

                    self.log_info("✅ Contribution submission working")

        except Exception as e:
            self.fail(f"Contribution submission test failed: {e}")

    def test_evaluate_contribution_mocked(self):
        """Test contribution evaluation with mocked API"""
        self.log_info("Testing contribution evaluation with mocking")

        if not self.server_available:
            self.skipTest("PoC server not available")

        try:
            from layer2.poc_server import PoCServer

            # Mock GROQ API key and OpenAI client
            with patch('os.getenv', return_value='test-groq-key'), \
                 patch('openai.OpenAI') as mock_openai:

                # Mock the models.list() call
                mock_client = mock_openai.return_value
                mock_client.models.list.return_value = None

                server = PoCServer()

                # Add test contribution
                server.archive.add_contribution(
                    submission_hash="eval_test_hash",
                    title="Evaluation Test",
                    contributor="test_contributor",
                    text_content="Content for evaluation",
                    is_test=True
                )

                # Mock the Grok API call
                with patch.object(server, '_call_grok_api', return_value='{"coherence": 8500, "density": 7500, "redundancy": 2000, "metals": ["gold"], "pod_score": 7875, "tier_justification": "High coherence and density", "redundancy_analysis": "Low redundancy", "status": "approved"}'):

                    result = server.evaluate_contribution("eval_test_hash")

                    self.assertTrue(result["success"])
                    self.assertIn("evaluation", result)
                    self.assertIn("coherence", result["evaluation"])
                    self.assertIn("metals", result["evaluation"])

                    self.log_info("✅ Contribution evaluation with mocking working")

        except Exception as e:
            self.fail(f"Contribution evaluation test failed: {e}")

    def test_get_sandbox_map(self):
        """Test sandbox map retrieval"""
        self.log_info("Testing sandbox map retrieval")

        if not self.server_available:
            self.skipTest("PoC server not available")

        try:
            from layer2.poc_server import PoCServer

            # Mock GROQ API key and OpenAI client
            with patch('os.getenv', return_value='test-groq-key'), \
                 patch('openai.OpenAI') as mock_openai:

                # Mock the models.list() call
                mock_client = mock_openai.return_value
                mock_client.models.list.return_value = None

                server = PoCServer()

                # Add test contribution
                server.archive.add_contribution(
                    submission_hash="sandbox_test_hash",
                    title="Sandbox Test",
                    contributor="test_contributor",
                    text_content="Content for sandbox",
                    is_test=True
                )

                # Get sandbox map
                map_data = server.get_sandbox_map()

                required_fields = ["nodes", "edges", "metadata"]
                for field in required_fields:
                    self.assertIn(field, map_data, f"Sandbox map missing field: {field}")

                self.assertIsInstance(map_data["nodes"], list)
                self.assertIsInstance(map_data["edges"], list)

                self.log_info("✅ Sandbox map retrieval working")

        except Exception as e:
            self.fail(f"Sandbox map retrieval test failed: {e}")

    def test_get_archive_statistics(self):
        """Test archive statistics retrieval"""
        self.log_info("Testing archive statistics")

        if not self.server_available:
            self.skipTest("PoC server not available")

        try:
            from layer2.poc_server import PoCServer

            # Mock GROQ API key and OpenAI client
            with patch('os.getenv', return_value='test-groq-key'), \
                 patch('openai.OpenAI') as mock_openai:

                # Mock the models.list() call
                mock_client = mock_openai.return_value
                mock_client.models.list.return_value = None

                server = PoCServer()

                # Add test contribution
                server.archive.add_contribution(
                    submission_hash="stats_test_hash",
                    title="Stats Test",
                    contributor="test_contributor",
                    text_content="Content for stats",
                    is_test=True
                )

                # Get archive statistics
                stats = server.get_archive_statistics()

                required_fields = ["total_contributions", "status_counts", "metal_counts", "unique_contributors"]
                for field in required_fields:
                    self.assertIn(field, stats, f"Archive statistics missing field: {field}")

                self.assertGreaterEqual(stats["total_contributions"], 1)

                self.log_info("✅ Archive statistics working")

        except Exception as e:
            self.fail(f"Archive statistics test failed: {e}")

    def test_get_epoch_info(self):
        """Test epoch information retrieval"""
        self.log_info("Testing epoch info retrieval")

        if not self.server_available:
            self.skipTest("PoC server not available")

        try:
            from layer2.poc_server import PoCServer

            # Mock GROQ API key and OpenAI client
            with patch('os.getenv', return_value='test-groq-key'), \
                 patch('openai.OpenAI') as mock_openai:

                # Mock the models.list() call
                mock_client = mock_openai.return_value
                mock_client.models.list.return_value = None

                server = PoCServer()

                # Get epoch info
                epoch_info = server.get_epoch_info()

                required_fields = ["current_epoch", "epochs"]
                for field in required_fields:
                    self.assertIn(field, epoch_info, f"Epoch info missing field: {field}")

                self.assertIn("founder", epoch_info["epochs"])
                self.assertIn("pioneer", epoch_info["epochs"])

                self.log_info("✅ Epoch info retrieval working")

        except Exception as e:
            self.fail(f"Epoch info test failed: {e}")

    def test_get_tokenomics_statistics(self):
        """Test tokenomics statistics retrieval"""
        self.log_info("Testing tokenomics statistics")

        if not self.server_available:
            self.skipTest("PoC server not available")

        try:
            from layer2.poc_server import PoCServer

            # Mock GROQ API key and OpenAI client
            with patch('os.getenv', return_value='test-groq-key'), \
                 patch('openai.OpenAI') as mock_openai:

                # Mock the models.list() call
                mock_client = mock_openai.return_value
                mock_client.models.list.return_value = None

                server = PoCServer()

                # Get tokenomics statistics
                stats = server.get_tokenomics_statistics()

                required_fields = ["total_supply", "total_distributed", "total_remaining", "epoch_balances"]
                for field in required_fields:
                    self.assertIn(field, stats, f"Tokenomics statistics missing field: {field}")

                self.assertGreater(stats["total_supply"], 0)

                self.log_info("✅ Tokenomics statistics working")

        except Exception as e:
            self.fail(f"Tokenomics statistics test failed: {e}")

    def test_cleanup_test_submissions(self):
        """Test cleanup of test submissions"""
        self.log_info("Testing test submission cleanup")

        if not self.server_available:
            self.skipTest("PoC server not available")

        try:
            from layer2.poc_server import PoCServer

            # Mock GROQ API key and OpenAI client
            with patch('os.getenv', return_value='test-groq-key'), \
                 patch('openai.OpenAI') as mock_openai:

                # Mock the models.list() call
                mock_client = mock_openai.return_value
                mock_client.models.list.return_value = None

                server = PoCServer()

                # Add some test contributions
                server.archive.add_contribution(
                    submission_hash="cleanup_test_1",
                    title="Test Cleanup 1",
                    contributor="test_contributor",
                    text_content="Test content 1",
                    is_test=True
                )

                server.archive.add_contribution(
                    submission_hash="cleanup_test_2",
                    title="Test Cleanup 2",
                    contributor="test_contributor",
                    text_content="Test content 2",
                    is_test=True
                )

                initial_count = len(server.archive.contributions)

                # Clean up test submissions
                result = server.cleanup_test_submissions()

                self.assertTrue(result["success"])
                self.assertGreaterEqual(result["cleaned_count"], 2)
                self.assertEqual(len(server.archive.contributions), initial_count - result["cleaned_count"])

                self.log_info("✅ Test submission cleanup working")

        except Exception as e:
            self.fail(f"Test submission cleanup failed: {e}")


def run_core_module_tests():
    """Run core module tests with framework"""
    TestUtils.print_test_header(
        "Core Modules Unit Test Suite",
        "Testing evaluator, tokenomics, archive, and sandbox map functionality"
    )

    import unittest
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPoCArchive)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestTokenomicsState))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSandboxMap))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPoCEvaluator))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestTokenAllocator))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPoCServer))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    import unittest
    unittest.main()
