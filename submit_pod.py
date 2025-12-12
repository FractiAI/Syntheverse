#!/usr/bin/env python3
"""
Command-line PoD Submission Tool
Submit a document for PoD scoring directly from command line.
"""

import sys
import os
import argparse
from pathlib import Path

# Add paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from layer1.node import SyntheverseNode
from layer2.pod_server import PODServer
from ui_pod_submission import PODSubmissionUI


def submit_document(pdf_path: str, contributor: str, category: str = "scientific"):
    """
    Submit a document for PoD scoring.
    
    Args:
        pdf_path: Path to PDF file
        contributor: Contributor ID
        category: Submission category (scientific/tech/alignment)
    """
    print("="*70)
    print("SYNTHVERSE PROOF-OF-DISCOVERY SUBMISSION")
    print("="*70)
    
    # Check if file exists
    if not os.path.exists(pdf_path):
        print(f"\n❌ Error: File not found: {pdf_path}")
        return
    
    print(f"\n📄 Document: {pdf_path}")
    print(f"👤 Contributor: {contributor}")
    print(f"📂 Category: {category}")
    
    # Initialize UI
    print("\n[1/6] Initializing system...")
    ui = PODSubmissionUI()
    print("✓ System initialized")
    
    # Submit PDF
    print(f"\n[2/6] Submitting document...")
    try:
        ui.submit_pdf(pdf_path, contributor, category)
        print("\n" + "="*70)
        print("✅ SUBMISSION COMPLETE")
        print("="*70)
        
        # Show summary
        print("\n📊 Summary:")
        print(f"  - Check reports in: test_outputs/pod_reports/")
        print(f"  - Blockchain state: test_outputs/blockchain/")
        print(f"  - Tokenomics state: test_outputs/l2_tokenomics_state.json")
        print(f"  - Submission history: test_outputs/submissions_history.json")
        
    except Exception as e:
        print(f"\n❌ Error during submission: {e}")
        import traceback
        traceback.print_exc()


def view_status():
    """View epoch status and token balances."""
    print("="*70)
    print("SYNTHVERSE EPOCH STATUS")
    print("="*70)
    
    ui = PODSubmissionUI()
    ui.display_epoch_status()


def list_submissions():
    """List all PoD submissions."""
    print("="*70)
    print("SYNTHVERSE PoD SUBMISSIONS")
    print("="*70)
    
    ui = PODSubmissionUI()
    ui.display_pod_list()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Syntheverse PoD Submission Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Submit a PDF paper
  python submit_pod.py --submit paper.pdf --contributor researcher-001 --category scientific
  
  # View epoch status
  python submit_pod.py --status
  
  # List all submissions
  python submit_pod.py --list
        """
    )
    
    parser.add_argument(
        "--submit",
        type=str,
        help="Path to PDF file to submit"
    )
    
    parser.add_argument(
        "--contributor",
        type=str,
        help="Contributor ID (required with --submit)"
    )
    
    parser.add_argument(
        "--category",
        type=str,
        choices=["scientific", "tech", "alignment"],
        default="scientific",
        help="Submission category (default: scientific)"
    )
    
    parser.add_argument(
        "--status",
        action="store_true",
        help="View epoch status and token balances"
    )
    
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all PoD submissions"
    )
    
    args = parser.parse_args()
    
    if args.submit:
        if not args.contributor:
            print("❌ Error: --contributor is required when using --submit")
            sys.exit(1)
        submit_document(args.submit, args.contributor, args.category)
    elif args.status:
        view_status()
    elif args.list:
        list_submissions()
    else:
        parser.print_help()
        print("\n💡 Tip: Use --submit to submit a document, --status to view epoch status, or --list to see all submissions")


if __name__ == "__main__":
    main()
