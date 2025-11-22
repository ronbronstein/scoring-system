#!/usr/bin/env python3
"""
AI Content Scoring Agent - CLI Entry Point

Usage:
    python src/main.py analyze <file_path>              # Analyze a single file
    python src/main.py batch <directory>                # Analyze all files in directory
    python src/main.py continue <file> <report>         # Retry failed agents from previous run
    python src/main.py test-layer1 <file>               # Test Layer 1 only (regex)
"""

import argparse
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import INPUT_DIR, CALIBRATION_DIR
from orchestrator import analyze_content, continue_analysis, analyze_batch
from regex_checker import run_layer_1_checks
import json


def cmd_analyze(args):
    """Analyze a single content file."""
    filepath = Path(args.file)

    if not filepath.exists():
        print(f"Error: File not found: {filepath}")
        return 1

    # Load content
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return 1

    # Determine content_id (use filename without extension)
    content_id = filepath.stem

    # Run analysis
    try:
        report, report_path = analyze_content(content, content_id, save_report=True)
        print(f"\n✓ Analysis complete!")
        print(f"Report saved to: {report_path}")

        # Optionally display JSON output
        if args.json:
            print("\nFull JSON Report:")
            print(json.dumps(report, indent=2))

        return 0
    except Exception as e:
        print(f"\n✗ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


def cmd_batch(args):
    """Analyze all files in a directory."""
    directory = Path(args.directory)

    if not directory.exists():
        print(f"Error: Directory not found: {directory}")
        return 1

    if not directory.is_dir():
        print(f"Error: Not a directory: {directory}")
        return 1

    # Run batch analysis
    try:
        results = analyze_batch(directory)

        # Summary
        successful = sum(1 for path in results.values() if path is not None)
        print(f"\nSummary: {successful}/{len(results)} successful")

        return 0 if successful == len(results) else 1
    except Exception as e:
        print(f"\n✗ Batch analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


def cmd_continue(args):
    """Continue a previous analysis by retrying failed agents."""
    filepath = Path(args.file)
    report_path = Path(args.report)

    if not filepath.exists():
        print(f"Error: Content file not found: {filepath}")
        return 1

    if not report_path.exists():
        print(f"Error: Report file not found: {report_path}")
        return 1

    # Load content
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading content file: {e}")
        return 1

    # Determine content_id
    content_id = filepath.stem

    # Continue analysis
    try:
        report, new_report_path = continue_analysis(
            content, content_id, str(report_path), save_report=True
        )
        print(f"\n✓ Retry complete!")
        print(f"Updated report saved to: {new_report_path}")

        return 0
    except Exception as e:
        print(f"\n✗ Retry failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


def cmd_test_layer1(args):
    """Test Layer 1 (regex) checks only on a file."""
    filepath = Path(args.file)

    if not filepath.exists():
        print(f"Error: File not found: {filepath}")
        return 1

    # Load content
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return 1

    # Run Layer 1 checks
    print("\n" + "=" * 70)
    print("LAYER 1 (REGEX) TEST")
    print("=" * 70 + "\n")

    flags = run_layer_1_checks(content)

    if not flags:
        print("✓ No violations found! Layer 1 passed.")
        return 0
    else:
        print(f"⚠️  Found {len(flags)} violation(s):\n")

        # Group by severity
        by_severity = {}
        for flag in flags:
            severity = flag["severity"]
            if severity not in by_severity:
                by_severity[severity] = []
            by_severity[severity].append(flag)

        # Display by severity
        for severity in ["Critical", "High", "Medium", "Low"]:
            if severity in by_severity:
                print(f"\n{severity} ({len(by_severity[severity])}):")
                print("-" * 70)
                for flag in by_severity[severity]:
                    print(f"\n  Rule: {flag['rule_id']}")
                    print(f"  Message: {flag['message']}")
                    print(f"  Violation: \"{flag['violation']}\"")
                    print(f"  Context: {flag['context']}")

        return 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="AI Content Scoring Agent - Evaluate content against monday.com brand standards",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Analyze command
    parser_analyze = subparsers.add_parser(
        "analyze", help="Analyze a single content file"
    )
    parser_analyze.add_argument("file", help="Path to content file (.txt or .md)")
    parser_analyze.add_argument(
        "--json", action="store_true", help="Display full JSON report"
    )
    parser_analyze.set_defaults(func=cmd_analyze)

    # Batch command
    parser_batch = subparsers.add_parser(
        "batch", help="Analyze all files in a directory"
    )
    parser_batch.add_argument("directory", help="Path to directory containing content files")
    parser_batch.set_defaults(func=cmd_batch)

    # Continue command
    parser_continue = subparsers.add_parser(
        "continue", help="Retry failed agents from a previous analysis"
    )
    parser_continue.add_argument("file", help="Path to original content file")
    parser_continue.add_argument("report", help="Path to previous report JSON")
    parser_continue.set_defaults(func=cmd_continue)

    # Test Layer 1 command
    parser_test = subparsers.add_parser(
        "test-layer1", help="Test Layer 1 (regex) checks only"
    )
    parser_test.add_argument("file", help="Path to content file")
    parser_test.set_defaults(func=cmd_test_layer1)

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Execute command
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
