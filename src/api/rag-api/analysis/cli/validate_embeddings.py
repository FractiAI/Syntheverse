#!/usr/bin/env python3
"""
CLI tool for validating embedding quality and consistency.

Checks embedding format, dimensions, norms, and data quality.
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from analysis import (
    EmbeddingValidator, load_embeddings_from_dir, ensure_output_dirs, setup_analysis_logging
)


def main():
    parser = argparse.ArgumentParser(
        description="Validate embedding quality and consistency",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full validation
  python validate_embeddings.py --embeddings-dir ./embeddings --output-file ./output/analysis/validation_report.json

  # Quick format check only
  python validate_embeddings.py --embeddings-dir ./embeddings --checks format --output-file ./validation.json

  # Detailed validation with custom thresholds
  python validate_embeddings.py --embeddings-dir ./embeddings --norm-threshold 0.1 --similarity-threshold 0.9 --output-file ./validation.json
        """
    )

    parser.add_argument(
        '--embeddings-dir',
        required=True,
        help='Directory containing embedding JSON files'
    )

    parser.add_argument(
        '--output-file',
        required=True,
        help='Path to save validation report'
    )

    parser.add_argument(
        '--checks',
        choices=['all', 'format', 'dimensions', 'norms', 'similarity', 'metadata', 'outliers'],
        default='all',
        help='Type of validation checks to perform'
    )

    parser.add_argument(
        '--norm-threshold',
        type=float,
        default=0.1,
        help='Threshold for norm validation (max deviation from 1.0)'
    )

    parser.add_argument(
        '--similarity-threshold',
        type=float,
        default=0.95,
        help='Threshold for detecting duplicate embeddings'
    )

    parser.add_argument(
        '--max-samples',
        type=int,
        default=10000,
        help='Maximum number of embeddings to validate'
    )

    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level'
    )

    args = parser.parse_args()

    # Setup logging
    logger = setup_analysis_logging(log_level=args.log_level)
    logger.info("Starting embedding validation")

    # Ensure output directory exists
    output_path = Path(args.output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        # Load embeddings
        print("Loading embeddings...")
        embeddings_data = load_embeddings_from_dir(args.embeddings_dir, max_files=None)

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
        validator = EmbeddingValidator(logger=logger)

        # Configure validation checks
        validation_config = {
            'norm_threshold': args.norm_threshold,
            'similarity_threshold': args.similarity_threshold
        }

        print(f"\nRunning validation checks: {args.checks}")

        # Perform validation
        if args.checks == 'all':
            validation_report = validator.generate_validation_report(
                embeddings_data, **validation_config
            )
        else:
            # Run specific check
            if args.checks == 'format':
                is_valid, errors = validator.validate_format(embeddings_data)
                validation_report = {
                    'overall_status': 'PASS' if is_valid else 'FAIL',
                    'checks_run': ['format'],
                    'format_check': {'valid': is_valid, 'errors': errors}
                }
            elif args.checks == 'dimensions':
                dim_report = validator.validate_dimensions(embeddings_data)
                validation_report = {
                    'overall_status': 'PASS' if dim_report['consistent'] else 'FAIL',
                    'checks_run': ['dimensions'],
                    'dimensions_check': dim_report
                }
            elif args.checks == 'norms':
                norm_report = validator.validate_norms(embeddings_data, args.norm_threshold)
                validation_report = {
                    'overall_status': 'PASS' if norm_report['normalized'] else 'WARNING',
                    'checks_run': ['norms'],
                    'norms_check': norm_report
                }
            elif args.checks == 'similarity':
                sim_report = validator.validate_similarity_range(embeddings_data)
                validation_report = {
                    'overall_status': 'PASS',
                    'checks_run': ['similarity'],
                    'similarity_check': sim_report
                }
            elif args.checks == 'metadata':
                meta_report = validator.validate_metadata(embeddings_data)
                validation_report = {
                    'overall_status': 'PASS' if meta_report['complete'] else 'WARNING',
                    'checks_run': ['metadata'],
                    'metadata_check': meta_report
                }
            elif args.checks == 'outliers':
                outlier_report = validator.detect_outliers(embeddings_data)
                validation_report = {
                    'overall_status': 'PASS' if outlier_report['outlier_percentage'] < 0.05 else 'WARNING',
                    'checks_run': ['outliers'],
                    'outliers_check': outlier_report
                }

        # Save validation report
        import json
        with open(args.output_file, 'w') as f:
            json.dump(validation_report, f, indent=2, default=str)

        # Print summary
        status = validation_report.get('overall_status', 'UNKNOWN')
        checks_run = validation_report.get('checks_run', [])

        print(f"\n✅ Validation completed!")
        print(f"📊 Status: {status}")
        print(f"🔍 Checks performed: {', '.join(checks_run)}")
        print(f"💾 Report saved to: {args.output_file}")

        # Print key findings
        if status == 'PASS':
            print("✅ All validation checks passed")
        elif status == 'WARNING':
            print("⚠️  Validation completed with warnings - check report for details")
        else:
            print("❌ Validation failed - check report for critical issues")

        return 0

    except Exception as e:
        logger.error(f"❌ Validation failed: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main())