#!/usr/bin/env python3
"""
Clear all persistent memory files from Syntheverse system.

This script removes:
- L2 tokenomics state
- L2 submissions registry
- L1 blockchain state files
- PoD evaluation reports
- Any cached data
"""

import os
import shutil
from pathlib import Path

def clear_persistent_memory():
    """Clear all persistent memory files."""
    
    base_dir = Path(__file__).parent
    files_to_remove = []
    dirs_to_clear = []
    
    # L2 State Files
    l2_state_file = base_dir / "test_outputs" / "l2_tokenomics_state.json"
    l2_registry_file = base_dir / "test_outputs" / "l2_submissions_registry.json"
    
    # L1 State Files
    l1_data_dir = base_dir / "test_outputs" / "blockchain"
    l1_blockchain_file = l1_data_dir / "blockchain.json"
    l1_token_file = l1_data_dir / "synth_token.json"
    l1_pod_file = l1_data_dir / "pod_contract.json"
    
    # UI Web State Files
    ui_data_dir = base_dir / "ui_web" / "test_outputs" / "blockchain"
    ui_blockchain_file = ui_data_dir / "blockchain.json"
    ui_token_file = ui_data_dir / "synth_token.json"
    ui_pod_file = ui_data_dir / "pod_contract.json"
    
    # UI Submission History Files
    ui_submissions_history = base_dir / "ui_web" / "test_outputs" / "submissions_history.json"
    ui_l2_registry = base_dir / "ui_web" / "test_outputs" / "l2_submissions_registry.json"
    test_submissions_history = base_dir / "test_outputs" / "submissions_history.json"
    
    # PoD Reports Directories
    pod_reports_dir = base_dir / "test_outputs" / "pod_reports"
    ui_pod_reports_dir = base_dir / "ui_web" / "test_outputs" / "pod_reports"
    
    # Collect all files to remove
    files_to_remove.extend([
        l2_state_file,
        l2_registry_file,
        l1_blockchain_file,
        l1_token_file,
        l1_pod_file,
        ui_blockchain_file,
        ui_token_file,
        ui_pod_file,
        ui_submissions_history,
        ui_l2_registry,
        test_submissions_history,
    ])
    
    # Collect directories to clear
    dirs_to_clear.extend([
        pod_reports_dir,
        ui_pod_reports_dir,
    ])
    
    print("Clearing persistent memory files...")
    print("=" * 60)
    
    # Remove files
    removed_count = 0
    for file_path in files_to_remove:
        if file_path.exists():
            try:
                file_path.unlink()
                print(f"✓ Removed: {file_path.relative_to(base_dir)}")
                removed_count += 1
            except Exception as e:
                print(f"✗ Failed to remove {file_path.relative_to(base_dir)}: {e}")
        else:
            print(f"○ Not found: {file_path.relative_to(base_dir)}")
    
    # Clear directories (but keep the directory structure)
    for dir_path in dirs_to_clear:
        if dir_path.exists():
            try:
                # Remove all files in directory but keep the directory
                for file_path in dir_path.glob("*"):
                    if file_path.is_file():
                        file_path.unlink()
                        print(f"✓ Removed: {file_path.relative_to(base_dir)}")
                        removed_count += 1
                    elif file_path.is_dir():
                        shutil.rmtree(file_path)
                        print(f"✓ Removed directory: {file_path.relative_to(base_dir)}")
                print(f"✓ Cleared directory: {dir_path.relative_to(base_dir)}")
            except Exception as e:
                print(f"✗ Failed to clear {dir_path.relative_to(base_dir)}: {e}")
        else:
            print(f"○ Directory not found: {dir_path.relative_to(base_dir)}")
    
    print("=" * 60)
    print(f"✓ Cleared {removed_count} file(s)")
    print("\nPersistent memory cleared! The system will start fresh on next run.")
    print("\nNote: This does NOT clear:")
    print("  - RAG API embeddings/chunks (stored separately)")
    print("  - Configuration files")
    print("  - Log files")

if __name__ == "__main__":
    clear_persistent_memory()
