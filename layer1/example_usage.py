"""
Example usage of Syntheverse Layer 1 Blockchain
Demonstrates POD submission, evaluation, and token allocation with epochs and tiers.
"""

import json
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layer1.node import SyntheverseNode


def main():
    """Demonstrate Layer 1 blockchain functionality."""
    
    # Initialize node
    print("Initializing Syntheverse Node...")
    node = SyntheverseNode(node_id="node-001", difficulty=1)
    
    # Display initial state
    print("\n=== Initial State ===")
    status = node.get_node_status()
    print(f"Current Epoch: {status['epoch']['current_epoch']}")
    print(f"Chain Length: {status['blockchain']['chain_length']}")
    print(f"Total Supply: {status['token']['total_supply']:,} SYNTH")
    
    # Example 1: Scientific Contribution (Gold Tier)
    print("\n=== Example 1: Scientific Contribution (Gold Tier) ===")
    scientific_submission = {
        "title": "Hydrogen-Holographic Fractal Awareness System",
        "description": "A novel approach to whole-brain AI using hydrogen-holographic fractals",
        "category": "scientific",
        "contributor": "researcher-001",
        "evidence": "Research paper with experimental validation",
    }
    
    result = node.submit_pod(scientific_submission)
    print(f"Submitted POD: {result['submission_hash']}")
    
    # Evaluate submission
    evaluation = {
        "coherence": 8500.0,
        "density": 9000.0,  # Qualifies for Founder epoch
        "novelty": 8000.0,
        "status": "approved",
    }
    
    node.evaluate_pod(result['submission_hash'], evaluation)
    print("Evaluation recorded")
    
    # Allocate tokens
    allocation = node.allocate_tokens(result['submission_hash'])
    if allocation['success']:
        print(f"Allocated: {allocation['allocation']['reward']:,.2f} SYNTH")
        print(f"Epoch: {allocation['allocation']['epoch']}")
        print(f"Tier: {allocation['allocation']['tier']}")
        print(f"PoD Score: {allocation['allocation']['pod_score']:.2f}")
    
    # Example 2: Tech Contribution (Silver Tier)
    print("\n=== Example 2: Tech Contribution (Silver Tier) ===")
    tech_submission = {
        "title": "Blockchain Consensus Optimization",
        "description": "Improved consensus mechanism for faster block times",
        "category": "tech",
        "contributor": "developer-001",
        "evidence": "Implementation and benchmarks",
    }
    
    result2 = node.submit_pod(tech_submission)
    print(f"Submitted POD: {result2['submission_hash']}")
    
    evaluation2 = {
        "coherence": 7500.0,
        "density": 6500.0,  # Qualifies for Pioneer epoch
        "novelty": 7000.0,
        "status": "approved",
    }
    
    node.evaluate_pod(result2['submission_hash'], evaluation2)
    allocation2 = node.allocate_tokens(result2['submission_hash'])
    if allocation2['success']:
        print(f"Allocated: {allocation2['allocation']['reward']:,.2f} SYNTH")
        print(f"Epoch: {allocation2['allocation']['epoch']}")
        print(f"Tier: {allocation2['allocation']['tier']}")
    
    # Example 3: Alignment Contribution (Copper Tier) - Community Epoch
    print("\n=== Example 3: Alignment Contribution (Copper Tier) - Community Epoch ===")
    alignment_submission = {
        "title": "AI Safety Framework",
        "description": "Framework for ensuring AI alignment with human values",
        "category": "alignment",
        "contributor": "safety-researcher-001",
        "evidence": "Safety analysis and framework documentation",
    }
    
    result3 = node.submit_pod(alignment_submission)
    print(f"Submitted POD: {result3['submission_hash']}")
    
    evaluation3 = {
        "coherence": 7000.0,
        "density": 4500.0,  # Qualifies for Community epoch
        "novelty": 6500.0,
        "status": "approved",
    }
    
    node.evaluate_pod(result3['submission_hash'], evaluation3)
    allocation3 = node.allocate_tokens(result3['submission_hash'])
    if allocation3['success']:
        print(f"Allocated: {allocation3['allocation']['reward']:,.2f} SYNTH")
        print(f"Epoch: {allocation3['allocation']['epoch']}")
        print(f"Tier: {allocation3['allocation']['tier']}")
    else:
        print(f"Allocation failed: {allocation3.get('reason', 'Unknown error')}")
    
    # Example 4: Copper Tier in Founder Epoch (should fail)
    print("\n=== Example 4: Copper Tier in Founder Epoch (Should Fail) ===")
    copper_founder_submission = {
        "title": "Early Alignment Research",
        "description": "Early alignment research",
        "category": "alignment",  # Copper tier
        "contributor": "early-researcher-001",
        "evidence": "Research documentation",
    }
    
    result4 = node.submit_pod(copper_founder_submission)
    print(f"Submitted POD: {result4['submission_hash']}")
    
    evaluation4 = {
        "coherence": 8500.0,
        "density": 9000.0,  # Qualifies for Founder epoch
        "novelty": 8000.0,
        "status": "approved",
    }
    
    node.evaluate_pod(result4['submission_hash'], evaluation4)
    allocation4 = node.allocate_tokens(result4['submission_hash'])
    if allocation4['success']:
        print(f"Allocated: {allocation4['allocation']['reward']:,.2f} SYNTH")
    else:
        print(f"Allocation failed (expected): {allocation4.get('reason', 'Unknown error')}")
        print("Copper tier is not available in Founder epoch")
    
    # Mine pending transactions
    print("\n=== Mining Block ===")
    block = node.mine_block(pod_score=7500.0)
    print(f"Mined block #{block.index}")
    print(f"Block hash: {block.hash[:16]}...")
    print(f"Transactions: {len(block.transactions)}")
    
    # Display tier availability by epoch
    print("\n=== Tier Availability by Epoch ===")
    from layer1.blockchain import Epoch, ContributionTier
    for epoch in Epoch:
        available_tiers = node.synth_token.get_available_tiers_for_epoch(epoch)
        tier_names = [tier.value for tier in available_tiers]
        print(f"{epoch.value}: {', '.join(tier_names) if tier_names else 'None'}")
    
    # Display epoch availability by tier
    print("\n=== Epoch Availability by Tier ===")
    for tier in ContributionTier:
        available_epochs = node.synth_token.get_available_epochs_for_tier(tier)
        epoch_names = [epoch.value for epoch in available_epochs]
        print(f"{tier.value}: {', '.join(epoch_names) if epoch_names else 'None'}")
    
    # Display final statistics
    print("\n=== Final Statistics ===")
    status = node.get_node_status()
    
    print(f"\nBlockchain:")
    print(f"  Chain Length: {status['blockchain']['chain_length']}")
    print(f"  Pending Transactions: {status['blockchain']['pending_transactions']}")
    print(f"  Valid: {status['blockchain']['is_valid']}")
    
    print(f"\nToken:")
    print(f"  Total Distributed: {status['token']['total_distributed']:,.2f} SYNTH")
    print(f"  Total Remaining: {status['token']['total_remaining']:,.2f} SYNTH")
    print(f"  Current Epoch: {status['token']['current_epoch']}")
    print(f"  Founder Halvings: {status['token']['founder_halving_count']}")
    
    print(f"\nEpoch Balances:")
    for epoch, balance in status['token']['epoch_balances'].items():
        print(f"  {epoch}: {balance:,.2f} SYNTH")
    
    print(f"\nPOD Statistics:")
    print(f"  Total Submissions: {status['pod']['total_submissions']}")
    print(f"  Approved: {status['pod']['approved_submissions']}")
    print(f"  Total Rewards: {status['pod']['total_rewards']}")
    
    print(f"\nEpoch Statistics by Tier:")
    epoch_stats = status['pod']['epoch_statistics']
    for epoch, tiers in epoch_stats.items():
        print(f"  {epoch}:")
        for tier, stats in tiers.items():
            if stats['count'] > 0:
                print(f"    {tier}: {stats['count']} submissions, "
                      f"{stats['total_rewards']:,.2f} SYNTH, "
                      f"avg PoD: {stats['avg_pod_score']:.2f}")
    
    # Display contributor balances
    print(f"\nContributor Balances:")
    for contributor, data in node.pod_contract.contributors.items():
        balance = node.synth_token.get_balance(contributor)
        print(f"  {contributor}: {balance:,.2f} SYNTH")
        print(f"    Submissions: {len(data['submissions'])}")
        print(f"    Tier Breakdown:")
        for tier, amount in data.get('tier_breakdown', {}).items():
            if amount > 0:
                print(f"      {tier}: {amount:,.2f} SYNTH")


if __name__ == "__main__":
    main()
