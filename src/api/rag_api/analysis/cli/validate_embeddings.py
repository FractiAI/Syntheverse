#!/usr/bin/env python3
"""
CLI tool for validating embeddings.

Runs comprehensive validation checks on embedding quality, consistency,
and structural integrity with detailed reporting.
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from analysis import EmbeddingValidator
from analysis.utils import load_embeddings_from_dir
from analysis.logger import setup_analysis_logging


def main():
    parser = argparse.ArgumentParser(
        description="Validate embeddings for quality and consistency",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic validation
  python validate_embeddings.py --embeddings-dir ./embeddings --output-file validation_report.json

  # Strict validation with detailed logging
  python validate_embeddings.py --embeddings-dir ./embeddings --output-file report.json --strict --verbose

  # Quick validation without file output
  python validate_embeddings.py --embeddings-dir ./embeddings
        """
    )

    parser.add_argument(
        '--embeddings-dir',
        required=True,
        help='Directory containing embedding JSON files'
    )

    parser.add_argument(
        '--output-file',
        help='Path to save validation report (JSON format)'
    )

    parser.add_argument(
        '--strict',
        action='store_true',
        help='Use strict validation mode (warnings become errors)'
    )

    parser.add_argument(
        '--max-samples',
        type=int,
        default=10000,
        help='Maximum number of embeddings to validate (default: 10000)'
    )

    parser.add_argument(
        '--log-file',
        help='Optional log file path'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    # Setup logging
    log_level = 'DEBUG' if args.verbose else 'INFO'
    setup_analysis_logging(log_file=args.log_file, level=log_level)

    print("=" * 80)
    print("Embedding Validation Tool")
    print("=" * 80)
    print(f"Embeddings directory: {args.embeddings_dir}")
    if args.output_file:
        print(f"Output file: {args.output_file}")
    print(f"Strict mode: {args.strict}")
    print(f"Max samples: {args.max_samples}")
    print()

    try:
        # Load embeddings
        print("Loading embeddings...")
        embeddings_data = load_embeddings_from_dir(args.embeddings_dir)

        if not embeddings_data:
            print("❌ No embeddings found in the specified directory")
            return 1

        print(f"✓ Loaded {len(embeddings_data)} embeddings")

        # Sample if needed
        if len(embeddings_data) > args.max_samples:
            from analysis.utils import sample_embeddings
            embeddings_data = sample_embeddings(embeddings_data, args.max_samples, random_state=42)
            print(f"✓ Sampled to {len(embeddings_data)} embeddings for validation")

        # Initialize validator
        validator = EmbeddingValidator(strict_mode=args.strict)

        # Run validation
        print("\nRunning validation checks...")
        report = validator.generate_validation_report_from_data(embeddings_data)

        # Save report if requested
        if args.output_file:
            output_path = Path(args.output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            import json
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            print(f"✓ Validation report saved to {output_path}")

        # Print summary
        print("\n" + "=" * 80)
        print("VALIDATION RESULTS")
        print("=" * 80)

        overall_valid = report.get('overall_valid', False)
        status = "✅ PASS" if overall_valid else "❌ FAIL"
        print(f"Overall Status: {status}")

        summary = report.get('summary', {})
        print(f"Total embeddings validated: {summary.get('total_embeddings', 'N/A')}")
        print(f"Checks run: {summary.get('checks_run', 'N/A')}")
        print(f"Failed checks: {summary.get('failed_checks', 'N/A')}")
        print(f"Warnings as errors: {summary.get('warnings_as_errors', 'N/A')}")

        # Detailed check results
        checks = report.get('checks', {})
        print("\nDetailed Check Results:")
        print("-" * 40)

        for check_name, check_result in checks.items():
            if isinstance(check_result, dict):
                valid = check_result.get('valid', False)
                status_icon = "✅" if valid else "❌"
                details = check_result.get('details', 'No details')
                print(f"{status_icon} {check_name}: {details}")

        # Issues and recommendations
        issues = report.get('recommendations', [])
        if issues:
            print("\nRecommendations:")
            print("-" * 20)
            for issue in issues:
                print(f"• {issue}")

        print("=" * 80)

        # Return appropriate exit code
        return 0 if overall_valid else 1

    except Exception as e:
        print(f"❌ Validation failed: {e}")
        import traceback
        if args.verbose:
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
