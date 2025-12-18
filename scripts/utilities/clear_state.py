#!/usr/bin/env python3
"""
Clear Syntheverse system state files.

This script removes persistent state files to reset the system.
Supports selective clearing and backup options.
"""

import os
import shutil
import argparse
import json
from pathlib import Path
from datetime import datetime
from typing import List, Set, Optional

def backup_state_files(project_root: Path, backup_dir: Path, files_to_backup: List[Path]) -> bool:
    """Create backup of state files before clearing."""
    try:
        backup_dir.mkdir(parents=True, exist_ok=True)

        backed_up = 0
        for file_path in files_to_backup:
            if file_path.exists():
                # Create relative path for backup
                relative_path = file_path.relative_to(project_root)
                backup_path = backup_dir / relative_path

                # Ensure backup directory exists
                backup_path.parent.mkdir(parents=True, exist_ok=True)

                # Copy file
                shutil.copy2(file_path, backup_path)
                print(f"✓ Backed up: {relative_path}")
                backed_up += 1

        if backed_up > 0:
            print(f"✓ Created backup with {backed_up} file(s) in {backup_dir.relative_to(project_root)}")
        else:
            print("○ No files to backup")

        return True

    except Exception as e:
        print(f"✗ Backup failed: {e}")
        return False

def clear_state_files(targets: Set[str], backup: bool = False):
    """Clear system state files based on specified targets."""

    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent

    files_to_remove = []
    dirs_to_clear = []
    files_to_backup = []

    # Define file groups based on targets
    if 'l2' in targets or 'all' in targets:
        # L2 State Files
        l2_state_file = project_root / "test_outputs" / "l2_tokenomics_state.json"
        l2_registry_file = project_root / "test_outputs" / "l2_submissions_registry.json"
        poc_archive_file = project_root / "test_outputs" / "poc_archive.json"

        files_to_remove.extend([l2_state_file, l2_registry_file, poc_archive_file])
        files_to_backup.extend([l2_state_file, l2_registry_file, poc_archive_file])

    if 'l1' in targets or 'all' in targets:
        # L1 State Files
        l1_data_dir = project_root / "test_outputs" / "blockchain"
        l1_blockchain_file = l1_data_dir / "blockchain.json"
        l1_token_file = l1_data_dir / "synth_token.json"
        l1_pod_file = l1_data_dir / "pod_contract.json"

        files_to_remove.extend([l1_blockchain_file, l1_token_file, l1_pod_file])
        files_to_backup.extend([l1_blockchain_file, l1_token_file, l1_pod_file])

    if 'reports' in targets or 'all' in targets:
        # PoD/PoC Reports Directories
        pod_reports_dir = project_root / "test_outputs" / "pod_reports"
        poc_reports_dir = project_root / "test_outputs" / "poc_reports"

        dirs_to_clear.extend([pod_reports_dir, poc_reports_dir])

    # Submission history files (always included with l2)
    if 'l2' in targets or 'all' in targets:
        test_submissions_history = project_root / "test_outputs" / "submissions_history.json"

        files_to_remove.extend([
            test_submissions_history,
        ])
        files_to_backup.extend([
            test_submissions_history,
        ])

    print(f"Clearing system state (targets: {', '.join(sorted(targets))})...")
    print("=" * 60)

    # Create backup if requested
    if backup and (files_to_backup or dirs_to_clear):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = project_root / "backups" / f"state_backup_{timestamp}"

        print("\n📦 Creating backup...")
        if not backup_state_files(project_root, backup_dir, files_to_backup):
            print("⚠️  Continuing without backup due to error")
        print()

    # Remove files
    removed_count = 0

    if files_to_remove:
        print("🗂️  Removing files...")
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

    # Clear directories
    if dirs_to_clear:
        print("\n📁 Clearing directories...")
        for dir_path in dirs_to_clear:
            if dir_path.exists():
                try:
                    # Remove all files in directory but keep the directory
                    dir_removed = 0
                    for file_path in dir_path.glob("*"):
                        if file_path.is_file():
                            file_path.unlink()
                            print(f"✓ Removed: {file_path.relative_to(project_root)}")
                            removed_count += 1
                            dir_removed += 1
                        elif file_path.is_dir():
                            shutil.rmtree(file_path)
                            print(f"✓ Removed directory: {file_path.relative_to(project_root)}")
                            dir_removed += 1

                    if dir_removed > 0:
                        print(f"✓ Cleared directory: {dir_path.relative_to(project_root)} ({dir_removed} items)")
                    else:
                        print(f"○ Directory empty: {dir_path.relative_to(project_root)}")

                except Exception as e:
                    print(f"✗ Failed to clear {dir_path.relative_to(project_root)}: {e}")
            else:
                print(f"○ Directory not found: {dir_path.relative_to(project_root)}")

    print("=" * 60)
    print(f"✓ Cleared {removed_count} item(s)")

    if removed_count > 0:
        print("\nSystem state cleared! The system will start fresh on next run.")
    else:
        print("\nNo items to clear.")

    print("\nNote: This does NOT clear:")
    print("  - RAG API embeddings/chunks (stored separately)")
    print("  - Configuration files")
    print("  - Log files")

    if backup and removed_count > 0:
        print(f"  - Backup created in: backups/state_backup_{timestamp}")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Clear Syntheverse system state files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Clear all state files
  python clear_state.py --target all

  # Clear only L2 tokenomics state
  python clear_state.py --target l2

  # Clear reports with backup
  python clear_state.py --target reports --backup

  # Clear multiple targets
  python clear_state.py --target l1 l2 --backup
        """
    )

    parser.add_argument(
        '--target',
        nargs='+',
        choices=['all', 'l1', 'l2', 'reports'],
        default=['all'],
        help='State components to clear (default: all)'
    )

    parser.add_argument(
        '--backup',
        action='store_true',
        help='Create backup before clearing'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be cleared without actually doing it'
    )

    args = parser.parse_args()

    # Convert target list to set for easier processing
    targets = set(args.target)

    # Handle 'all' target
    if 'all' in targets:
        targets = {'all'}

    if args.dry_run:
        print("DRY RUN - Would clear the following targets:")
        for target in sorted(targets):
            print(f"  - {target}")
        print("\nRun without --dry-run to actually clear files.")
        return

    try:
        clear_state_files(targets, args.backup)
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
