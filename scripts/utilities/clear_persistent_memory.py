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
    
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    
    files_to_remove = []
    dirs_to_clear = []
    
    # L2 State Files
    l2_state_file = project_root / "test_outputs" / "l2_tokenomics_state.json"
    l2_registry_file = project_root / "test_outputs" / "l2_submissions_registry.json"
    
    # L1 State Files
    l1_data_dir = project_root / "test_outputs" / "blockchain"
    l1_blockchain_file = l1_data_dir / "blockchain.json"
    l1_token_file = l1_data_dir / "synth_token.json"
    l1_pod_file = l1_data_dir / "pod_contract.json"
    
    # Legacy Web State Files (web-legacy)
    web_legacy_data_dir = project_root / "src" / "frontend" / "web-legacy" / "test_outputs" / "blockchain"
    web_legacy_blockchain_file = web_legacy_data_dir / "blockchain.json"
    web_legacy_token_file = web_legacy_data_dir / "synth_token.json"
    web_legacy_pod_file = web_legacy_data_dir / "pod_contract.json"
    
    # Legacy Submission History Files
    web_legacy_submissions_history = project_root / "src" / "frontend" / "web-legacy" / "test_outputs" / "submissions_history.json"
    web_legacy_l2_registry = project_root / "src" / "frontend" / "web-legacy" / "test_outputs" / "l2_submissions_registry.json"
    test_submissions_history = project_root / "test_outputs" / "submissions_history.json"
    
    # PoD/PoC Reports Directories
    pod_reports_dir = project_root / "test_outputs" / "pod_reports"
    poc_reports_dir = project_root / "test_outputs" / "poc_reports"
    web_legacy_pod_reports_dir = project_root / "src" / "frontend" / "web-legacy" / "test_outputs" / "pod_reports"
    
    # Collect all files to remove
    files_to_remove.extend([
        l2_state_file,
        l2_registry_file,
        l1_blockchain_file,
        l1_token_file,
        l1_pod_file,
        web_legacy_blockchain_file,
        web_legacy_token_file,
        web_legacy_pod_file,
        web_legacy_submissions_history,
        web_legacy_l2_registry,
        test_submissions_history,
    ])
    
    # Collect directories to clear
    dirs_to_clear.extend([
        pod_reports_dir,
        poc_reports_dir,
        web_legacy_pod_reports_dir,
    ])
    
    print("Clearing persistent memory files...")
    print("=" * 60)
    
    # Remove files
    removed_count = 0
    for file_path in files_to_remove:
        if file_path.exists():
            try:
                file_path.unlink()
                print(f"✓ Removed: {file_path.relative_to(project_root)}")
                removed_count += 1
            except Exception as e:
                print(f"✗ Failed to remove {file_path.relative_to(project_root)}: {e}")
        else:
            print(f"○ Not found: {file_path.relative_to(project_root)}")
    
    # Clear directories (but keep the directory structure)
    for dir_path in dirs_to_clear:
        if dir_path.exists():
            try:
                # Remove all files in directory but keep the directory
                for file_path in dir_path.glob("*"):
                    if file_path.is_file():
                        file_path.unlink()
                        print(f"✓ Removed: {file_path.relative_to(project_root)}")
                        removed_count += 1
                    elif file_path.is_dir():
                        shutil.rmtree(file_path)
                        print(f"✓ Removed directory: {file_path.relative_to(project_root)}")
                print(f"✓ Cleared directory: {dir_path.relative_to(project_root)}")
            except Exception as e:
                print(f"✗ Failed to clear {dir_path.relative_to(project_root)}: {e}")
        else:
            print(f"○ Directory not found: {dir_path.relative_to(project_root)}")
    
    print("=" * 60)
    print(f"✓ Cleared {removed_count} file(s)")
    print("\nPersistent memory cleared! The system will start fresh on next run.")
    print("\nNote: This does NOT clear:")
    print("  - RAG API embeddings/chunks (stored separately)")
    print("  - Configuration files")
    print("  - Log files")

if __name__ == "__main__":
    clear_persistent_memory()
