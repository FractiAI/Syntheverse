"""
Syntheverse PoD Submission UI
Simple console-based UI for submitting PDF papers for PoD evaluation.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Add paths for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from layer1.node import SyntheverseNode
from layer2.pod_server import PODServer


class PODSubmissionUI:
    """
    Console UI for PoD submissions.
    """
    
    def __init__(
        self,
        node: Optional[SyntheverseNode] = None,
        pod_server: Optional[PODServer] = None,
        output_dir: str = "test_outputs"
    ):
        """
        Initialize submission UI.
        
        Args:
            node: L1 blockchain node
            pod_server: L2 PoD evaluation server
            output_dir: Output directory for reports
        """
        self.node = node or SyntheverseNode(
            node_id="submission-node",
            data_dir=f"{output_dir}/blockchain"
        )
        self.pod_server = pod_server or PODServer(
            output_dir=f"{output_dir}/pod_reports"
        )
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Submission history
        self.submissions_file = self.output_dir / "submissions_history.json"
        self.submissions = self._load_submissions()
    
    def _load_submissions(self) -> List[Dict]:
        """Load submission history."""
        if self.submissions_file.exists():
            with open(self.submissions_file, "r") as f:
                return json.load(f)
        return []
    
    def _save_submissions(self):
        """Save submission history."""
        with open(self.submissions_file, "w") as f:
            json.dump(self.submissions, f, indent=2)
    
    def display_epoch_status(self):
        """Display current epoch status and token balances."""
        # Get L1 status
        l1_status = self.node.get_epoch_info()
        l1_token_stats = self.node.get_token_statistics()
        
        # Get L2 tokenomics status
        l2_epoch_info = self.pod_server.get_epoch_info()
        l2_token_stats = self.pod_server.get_tokenomics_statistics()
        
        print("\n" + "="*70)
        print("EPOCH STATUS & TOKEN BALANCES")
        print("="*70)
        
        current_epoch = l1_status["current_epoch"]
        print(f"\nCurrent Active Epoch: {current_epoch.upper()}")
        print(f"Total Coherence Density: {l2_token_stats['total_coherence_density']:,.2f}")
        print(f"Founder Halving Count: {l2_token_stats['founder_halving_count']}")
        
        print("\nEpoch Details (L2 Tokenomics State):")
        print("-" * 70)
        for epoch_name, epoch_info in l2_epoch_info["epochs"].items():
            balance = epoch_info["balance"]
            threshold = epoch_info["threshold"]
            available_tiers = ", ".join(epoch_info["available_tiers"])
            
            print(f"\n{epoch_name.upper()}")
            print(f"  Remaining Tokens: {balance:,.2f} SYNTH")
            print(f"  Distribution: {epoch_info['distribution_percent']:.1f}%")
            print(f"  Threshold: Density ≥ {threshold}")
            print(f"  Available Tiers: {available_tiers}")
        
        print(f"\nTokenomics Summary:")
        print(f"  Total Supply: {l2_token_stats['total_supply']:,.0f} SYNTH")
        print(f"  Total Distributed: {l2_token_stats['total_distributed']:,.2f} SYNTH")
        print(f"  Total Remaining: {l2_token_stats['total_remaining']:,.2f} SYNTH")
        print(f"  Total Holders: {l2_token_stats['total_holders']}")
        print(f"  Total Allocations: {l2_token_stats['total_allocations']}")
        
        print("\n" + "="*70)
    
    def display_pod_list(self):
        """Display all PoD submissions."""
        print("\n" + "="*70)
        print("PROOF-OF-DISCOVERY SUBMISSIONS")
        print("="*70)
        
        if not self.submissions:
            print("\nNo submissions yet.")
            return
        
        print(f"\nTotal Submissions: {len(self.submissions)}")
        print("-" * 70)
        
        for i, sub in enumerate(self.submissions, 1):
            print(f"\n[{i}] {sub.get('title', 'Untitled')}")
            print(f"    Hash: {sub.get('submission_hash', 'N/A')[:16]}...")
            print(f"    Category: {sub.get('category', 'N/A')}")
            print(f"    Status: {sub.get('status', 'pending')}")
            
            if sub.get('evaluation'):
                eval_data = sub['evaluation']
                print(f"    Coherence: {eval_data.get('coherence', 0):.0f}")
                print(f"    Density: {eval_data.get('density', 0):.0f}")
                print(f"    Novelty: {eval_data.get('novelty', 0):.0f}")
                print(f"    PoD Score: {sub.get('pod_score', 0):.2f}")
            
            if sub.get('allocation'):
                alloc = sub['allocation']
                print(f"    Epoch: {alloc.get('epoch', 'N/A')}")
                print(f"    Tier: {alloc.get('tier', 'N/A')}")
                print(f"    SYNTH Allocated: {alloc.get('reward', 0):,.2f}")
            else:
                print(f"    SYNTH Allocated: 0 (not allocated)")
        
        print("\n" + "="*70)
    
    def submit_pdf(self, pdf_path: str, contributor: str, category: Optional[str] = None):
        """
        Submit a PDF paper for PoD evaluation.
        
        Args:
            pdf_path: Path to PDF file
            contributor: Contributor identifier
            category: Submission category (scientific/tech/alignment)
        """
        if not os.path.exists(pdf_path):
            print(f"Error: PDF file not found: {pdf_path}")
            return
        
        # Extract title from filename
        title = Path(pdf_path).stem.replace("_", " ").title()
        
        print(f"\nSubmitting PDF: {pdf_path}")
        print(f"Title: {title}")
        print(f"Contributor: {contributor}")
        
        # Step 1: Submit to L1
        print("\n[Step 1] Submitting to Layer 1 blockchain...")
        submission_data = {
            "title": title,
            "description": f"PDF submission: {Path(pdf_path).name}",
            "category": category or "scientific",
            "contributor": contributor,
            "evidence": pdf_path,
        }
        
        result = self.node.submit_pod(submission_data)
        submission_hash = result["submission_hash"]
        print(f"✓ Submission hash: {submission_hash}")
        
        # Step 2: Evaluate with L2 PoD server
        print("\n[Step 2] Evaluating with Layer 2 PoD server...")
        
        # Progress callback function - try to get from global scope or module
        progress_callback = None
        try:
            # Method 1: Try importing from ui_web.app directly
            try:
                from ui_web.app import submission_progress
                progress_dict = submission_progress
            except ImportError:
                # Method 2: Try to get from sys.modules if already loaded
                import sys
                if 'ui_web.app' in sys.modules:
                    app_module = sys.modules['ui_web.app']
                    progress_dict = getattr(app_module, 'submission_progress', None)
                else:
                    progress_dict = None
            
            if progress_dict is not None:
                # Initialize progress if not already set
                if submission_hash not in progress_dict:
                    progress_dict[submission_hash] = {
                        "status": "processing",
                        "message": "Starting evaluation...",
                        "stage": "submitted",
                        "timestamp": datetime.now().isoformat()
                    }
                
                def update_progress(stage, message):
                    """Update progress for this submission."""
                    if submission_hash in progress_dict:
                        progress_dict[submission_hash].update({
                            "stage": stage,
                            "message": message,
                            "timestamp": datetime.now().isoformat()
                        })
                    print(f"[Progress] {stage}: {message}")
                
                progress_callback = update_progress
                print(f"Progress tracking enabled for submission: {submission_hash[:16]}...")
        except Exception as e:
            # If running outside web context, no progress tracking
            print(f"Progress tracking not available: {e}")
            pass
        
        eval_result = self.pod_server.evaluate_submission(
            submission_hash=submission_hash,
            title=title,
            pdf_path=pdf_path,
            category=category or "scientific",
            progress_callback=progress_callback
        )
        
        if not eval_result["success"]:
            error_msg = eval_result.get('error', 'Unknown error')
            error_type = eval_result.get('error_type', 'evaluation_error')
            print(f"✗ Evaluation failed: {error_msg}")
            
            # Check if it's a duplicate/redundant submission
            if eval_result.get('duplicate_info'):
                dup_info = eval_result['duplicate_info']
                print(f"  Reason: {dup_info.get('reason', 'Duplicate submission')}")
                if dup_info.get('first_submission'):
                    print(f"  First registered: {dup_info['first_submission'][:16]}...")
            
            if eval_result.get('redundancy_info'):
                red_info = eval_result['redundancy_info']
                print(f"  Reason: {red_info.get('reason', 'Redundant submission')}")
                print(f"  Similarity: {red_info.get('similarity_score', 0):.2%}")
            
            # Store error in submission record
            submission_record = {
                "submission_hash": submission_hash,
                "title": title,
                "contributor": contributor,
                "category": category or "scientific",
                "timestamp": datetime.now().isoformat(),
                "status": "evaluation_failed",
                "error": error_msg,
                "error_type": error_type,
                "eval_result": eval_result
            }
            self.submissions.append(submission_record)
            return
        
        evaluation = eval_result["report"]["evaluation"]
        print(f"✓ Evaluation complete")
        print(f"  Coherence: {evaluation['coherence']:.0f}")
        print(f"  Density: {evaluation['density']:.0f}")
        print(f"  Novelty: {evaluation['novelty']:.0f}")
        print(f"  Tier: {evaluation['tier']}")
        print(f"  Status: {evaluation['status']}")
        
        # Step 3: Check for duplicate/redundancy
        duplicate_check = eval_result["report"].get("duplicate_check", {})
        if duplicate_check:
            is_first = duplicate_check.get("is_first_registered", False)
            if is_first:
                print("\n[Step 3] Duplicate Check:")
                print(f"  ✓ First registered submission - eligible for tokens")
            else:
                print("\n[Step 3] Duplicate Check:")
                print(f"  ✗ Duplicate submission - tokens awarded to first registered")
                print(f"  This submission will not receive tokens")
        
        # Step 4: Check allocation availability from L2 tokenomics
        allocation_info = eval_result["report"].get("allocation")
        if allocation_info:
            print("\n[Step 4] Allocation Preview (from L2 tokenomics):")
            if allocation_info.get("success"):
                print(f"  ✓ Allocation available")
                print(f"  Epoch: {allocation_info['epoch']}")
                print(f"  Tier: {allocation_info['tier']}")
                print(f"  PoD Score: {allocation_info['pod_score']:.2f}")
                print(f"  Base Reward: {allocation_info['base_reward']:,.2f}")
                print(f"  Tier Multiplier: {allocation_info['tier_multiplier']}x")
                print(f"  Total Reward: {allocation_info['reward']:,.2f} SYNTH")
                print(f"  Epoch Balance Before: {allocation_info['epoch_balance_before']:,.2f}")
                print(f"  Epoch Balance After: {allocation_info['epoch_balance_after']:,.2f}")
            else:
                print(f"  ✗ Allocation not available: {allocation_info.get('reason', 'Unknown')}")
        
        # Step 5: Record evaluation in L1
        print("\n[Step 5] Recording evaluation in Layer 1...")
        self.node.evaluate_pod(submission_hash, {
            "coherence": evaluation["coherence"],
            "density": evaluation["density"],
            "novelty": evaluation["novelty"],
            "status": evaluation["status"],
        })
        print("✓ Evaluation recorded")
        
        # Step 6: Allocate tokens if approved
        allocation_result = None
        if evaluation["status"] == "approved":
            print("\n[Step 6] Allocating SYNTH tokens in Layer 1...")
            allocation_result = self.node.allocate_tokens(submission_hash)
            
            if allocation_result["success"]:
                alloc = allocation_result["allocation"]
                print(f"✓ Tokens allocated in L1!")
                print(f"  Epoch: {alloc['epoch']}")
                print(f"  Tier: {alloc['tier']}")
                print(f"  PoD Score: {alloc['pod_score']:.2f}")
                print(f"  SYNTH Allocated: {alloc['reward']:,.2f}")
                
                # Record allocation in L2 tokenomics
                self.pod_server.record_allocation(
                    submission_hash=submission_hash,
                    contributor=contributor,
                    coherence=evaluation["coherence"]
                )
                
                # Sync L2 state with L1
                l1_stats = self.node.get_token_statistics()
                self.pod_server.sync_from_l1(l1_stats)
            else:
                print(f"✗ Allocation failed: {allocation_result.get('reason', 'Unknown error')}")
        else:
            print("\n[Step 5] Submission rejected - no tokens allocated")
        
        # Step 7: Mine block
        print("\n[Step 7] Mining block...")
        block = self.node.mine_block(pod_score=evaluation.get("density", 0))
        print(f"✓ Block #{block.index} mined")
        print(f"  Block hash: {block.hash[:16]}...")
        print(f"  Transactions: {len(block.transactions)}")
        
        # Save submission record
        submission_record = {
            "submission_hash": submission_hash,
            "title": title,
            "pdf_path": pdf_path,
            "contributor": contributor,
            "category": category or "scientific",
            "timestamp": datetime.now().isoformat(),
            "evaluation": evaluation,
            "pod_score": self.node.pod_contract.submissions.get(submission_hash, {}).get("pod_score"),
            "allocation": allocation_result["allocation"] if allocation_result and allocation_result.get("success") else None,
            "status": evaluation["status"],
        }
        
        self.submissions.append(submission_record)
        self._save_submissions()
        
        # Generate PoD report
        self._generate_pod_report(submission_record)
        
        print("\n" + "="*70)
        print("SUBMISSION COMPLETE")
        print("="*70)
    
    def _generate_pod_report(self, submission: Dict):
        """Generate comprehensive PoD report."""
        report_dir = self.output_dir / "pod_reports"
        report_dir.mkdir(parents=True, exist_ok=True)
        
        report = {
            "submission": {
                "hash": submission["submission_hash"],
                "title": submission["title"],
                "contributor": submission["contributor"],
                "category": submission["category"],
                "timestamp": submission["timestamp"],
            },
            "evaluation": submission["evaluation"],
            "pod_score": submission.get("pod_score", 0),
            "allocation": submission.get("allocation"),
            "status": submission["status"],
            "blockchain": {
                "chain_length": self.node.blockchain.get_chain_length(),
                "latest_block": self.node.blockchain.get_latest_block().index,
            },
            "epoch_status": self.node.get_epoch_info(),
            "token_stats": self.node.get_token_statistics(),
        }
        
        filename = f"{submission['submission_hash']}_report.json"
        filepath = report_dir / filename
        
        with open(filepath, "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"\nPoD Report saved: {filepath}")
    
    def run_interactive(self):
        """Run interactive console UI."""
        print("\n" + "="*70)
        print("SYNTHVERSE PROOF-OF-DISCOVERY SUBMISSION CONSOLE")
        print("="*70)
        
        while True:
            print("\nOptions:")
            print("  1. Submit PDF paper")
            print("  2. View epoch status")
            print("  3. List all PoD submissions")
            print("  4. Exit")
            
            choice = input("\nSelect option (1-4): ").strip()
            
            if choice == "1":
                pdf_path = input("Enter PDF file path: ").strip()
                contributor = input("Enter contributor ID: ").strip()
                category = input("Enter category (scientific/tech/alignment) [scientific]: ").strip() or "scientific"
                self.submit_pdf(pdf_path, contributor, category)
            
            elif choice == "2":
                self.display_epoch_status()
            
            elif choice == "3":
                self.display_pod_list()
            
            elif choice == "4":
                print("\nExiting...")
                break
            
            else:
                print("Invalid option. Please try again.")


if __name__ == "__main__":
    ui = PODSubmissionUI()
    ui.run_interactive()

