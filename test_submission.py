"""
Quick test script for PoD submission UI
Tests the submission system with a sample submission.
"""

import sys
import os
from pathlib import Path

# Add paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from layer1.node import SyntheverseNode
from layer2.pod_server import PODServer
from ui_pod_submission import PODSubmissionUI


def test_with_text_submission():
    """Test with a text-based submission (no PDF required)."""
    print("="*70)
    print("SYNTHVERSE PoD SUBMISSION TEST")
    print("="*70)
    
    # Initialize UI
    print("\n[1] Initializing PoD Submission UI...")
    ui = PODSubmissionUI()
    print("✓ UI initialized")
    
    # Display initial epoch status
    print("\n[2] Initial Epoch Status:")
    ui.display_epoch_status()
    
    # Create a test submission (text-based, no PDF)
    print("\n[3] Creating test submission...")
    test_submission = {
        "title": "Test Hydrogen-Holographic Fractal Research",
        "description": "A test submission for evaluating the PoD system",
        "category": "scientific",
        "contributor": "test-researcher-001",
        "evidence": "Test evidence content for evaluation",
    }
    
    # Submit to L1
    print("\n[4] Submitting to Layer 1...")
    result = ui.node.submit_pod(test_submission)
    submission_hash = result["submission_hash"]
    print(f"✓ Submission hash: {submission_hash}")
    
    # Evaluate with L2 (using text content)
    print("\n[5] Evaluating with Layer 2 PoD Server...")
    test_text = """
    This is a test research paper on Hydrogen-Holographic Fractal systems.
    It discusses the structural properties of fractal awareness and recursive coherence.
    The paper presents novel insights into the relationship between hydrogen geometry
    and cognitive patterns, demonstrating significant structural density and coherence.
    """
    
    eval_result = ui.pod_server.evaluate_submission(
        submission_hash=submission_hash,
        title=test_submission["title"],
        text_content=test_text,
        category="scientific"
    )
    
    if eval_result["success"]:
        evaluation = eval_result["report"]["evaluation"]
        print(f"✓ Evaluation complete")
        print(f"  Coherence: {evaluation['coherence']:.0f}")
        print(f"  Density: {evaluation['density']:.0f}")
        print(f"  Novelty: {evaluation['novelty']:.0f}")
        print(f"  Tier: {evaluation['tier']}")
        print(f"  Status: {evaluation['status']}")
        
        # Show allocation preview
        allocation = eval_result["report"].get("allocation")
        if allocation:
            if allocation.get("success"):
                print(f"\n  Allocation Preview:")
                print(f"    Epoch: {allocation['epoch']}")
                print(f"    Tier: {allocation['tier']}")
                print(f"    PoD Score: {allocation['pod_score']:.2f}")
                print(f"    Reward: {allocation['reward']:,.2f} SYNTH")
            else:
                print(f"\n  Allocation: {allocation.get('reason', 'Not available')}")
    else:
        print(f"✗ Evaluation failed: {eval_result.get('error', 'Unknown')}")
        return
    
    # Record evaluation in L1
    print("\n[6] Recording evaluation in Layer 1...")
    ui.node.evaluate_pod(submission_hash, {
        "coherence": evaluation["coherence"],
        "density": evaluation["density"],
        "novelty": evaluation["novelty"],
        "status": evaluation["status"],
    })
    print("✓ Evaluation recorded")
    
    # Allocate tokens if approved
    if evaluation["status"] == "approved":
        print("\n[7] Allocating SYNTH tokens...")
        allocation_result = ui.node.allocate_tokens(submission_hash)
        
        if allocation_result["success"]:
            alloc = allocation_result["allocation"]
            print(f"✓ Tokens allocated!")
            print(f"  Epoch: {alloc['epoch']}")
            print(f"  Tier: {alloc['tier']}")
            print(f"  PoD Score: {alloc['pod_score']:.2f}")
            print(f"  SYNTH Allocated: {alloc['reward']:,.2f}")
            
            # Record in L2
            ui.pod_server.record_allocation(
                submission_hash=submission_hash,
                contributor=test_submission["contributor"],
                coherence=evaluation["coherence"]
            )
            
            # Sync L2 with L1
            l1_stats = ui.node.get_token_statistics()
            ui.pod_server.sync_from_l1(l1_stats)
        else:
            print(f"✗ Allocation failed: {allocation_result.get('reason', 'Unknown')}")
    
    # Mine block
    print("\n[8] Mining block...")
    block = ui.node.mine_block(pod_score=evaluation.get("density", 0))
    print(f"✓ Block #{block.index} mined")
    print(f"  Transactions: {len(block.transactions)}")
    
    # Display final status
    print("\n[9] Final Status:")
    ui.display_epoch_status()
    
    # Display PoD list
    print("\n[10] PoD Submissions:")
    ui.display_pod_list()
    
    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70)
    print("\nCheck test_outputs/ for:")
    print("  - blockchain/ - L1 blockchain state")
    print("  - pod_reports/ - PoD evaluation reports")
    print("  - l2_tokenomics_state.json - L2 tokenomics state")
    print("  - submissions_history.json - Submission history")


if __name__ == "__main__":
    try:
        test_with_text_submission()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\nError during test: {e}")
        import traceback
        traceback.print_exc()
