"""
Orchestrator: Coordinates the entire content analysis pipeline.
Executes Layer 1 → Layer 2 → Scorer and manages state/retries.
"""

import json
import time
from pathlib import Path
from typing import Dict, Optional, Tuple

from config import REPORTS_DIR, DELAY_BETWEEN_FILES
from regex_checker import run_layer_1_checks
from llm_client import run_layer_2_analysis, retry_failed
from scorer import generate_report


# ============================================================================
# MAIN ANALYSIS PIPELINE
# ============================================================================


def analyze_content(
    content: str, content_id: str, save_report: bool = True, subfolder: str = None
) -> Tuple[Dict, str]:
    """
    Execute the complete content analysis pipeline.

    Pipeline:
    1. Layer 1: Regex checks (deterministic)
    2. Layer 2: Parallel LLM agent execution (16 agents)
    3. Scorer: Two-level aggregation and 3-Gate evaluation
    4. Save JSON report

    Args:
        content: The draft content to analyze
        content_id: Identifier for the content (used in report filename)
        save_report: Whether to save the report to disk
        subfolder: Optional subfolder within reports directory (e.g., "golden_set", "poison_set")

    Returns:
        Tuple of (report_dict, report_path)
    """
    print("\n" + "=" * 70)
    print(f"STARTING ANALYSIS: {content_id}")
    print("=" * 70)

    # ========================================================================
    # LAYER 1: REGEX CHECKS (The Hard Gate)
    # ========================================================================
    print("\n[LAYER 1] Running deterministic regex checks...")
    layer_1_flags = run_layer_1_checks(content)

    if layer_1_flags:
        print(f"  ⚠️  Found {len(layer_1_flags)} violation(s)")
        critical_count = sum(1 for f in layer_1_flags if f["severity"] == "Critical")
        if critical_count > 0:
            print(f"  🚫 {critical_count} CRITICAL violation(s) found (Gate 3 will fail)")
    else:
        print("  ✓ Layer 1 passed: No violations found")

    # ========================================================================
    # LAYER 2: LLM AGENT EXECUTION (The Soft Gate)
    # ========================================================================
    print("\n[LAYER 2] Executing 16 parallel LLM agents...")
    print("  (This may take 30-60 seconds depending on API response times)")

    layer_2_results = run_layer_2_analysis(content)

    # Check for failures
    failed_agents = [
        agent_id
        for agent_id, result in layer_2_results.items()
        if not result.get("success", False)
    ]

    if failed_agents:
        print(f"\n  ⚠️  {len(failed_agents)} agent(s) failed:")
        for agent_id in failed_agents:
            error = layer_2_results[agent_id].get("error", "Unknown error")
            print(f"    - {agent_id}: {error}")
    else:
        print("  ✓ All 16 agents completed successfully")

    # ========================================================================
    # SCORER: AGGREGATION AND REPORT GENERATION
    # ========================================================================
    print("\n[SCORER] Generating comprehensive report...")
    report = generate_report(content_id, layer_1_flags, layer_2_results)

    # Display summary
    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)
    print(f"Overall Score: {report['results']['overall_score']}")
    print(f"Status: {report['results']['status']}")
    print(f"Publish-Ready: {report['results']['publish_ready']}")
    print("\nGate Status:")
    print(f"  Gate 1 (Overall Threshold): {_format_gate_status(report['gates_status']['gate_1_overall_threshold_met'])}")
    print(f"  Gate 2 (Tone Minimum): {_format_gate_status(report['gates_status']['gate_2_tone_veto_passed'])}")
    print(f"  Gate 3 (Brand Compliance): {_format_gate_status(report['gates_status']['gate_3_brand_veto_passed'])}")
    print("=" * 70 + "\n")

    # ========================================================================
    # SAVE REPORT
    # ========================================================================
    if save_report:
        report_path = save_report_to_file(report, content_id, subfolder=subfolder)
        print(f"Report saved to: {report_path}")
    else:
        report_path = None

    return report, report_path


def save_report_to_file(report: Dict, content_id: str, subfolder: str = None) -> str:
    """
    Save the analysis report as a JSON file.

    Args:
        report: The complete report dictionary
        content_id: Content identifier for filename
        subfolder: Optional subfolder within reports directory (e.g., "golden_set", "poison_set")

    Returns:
        Path to saved report file
    """
    # Create safe filename from content_id
    safe_filename = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in content_id)
    filename = f"{safe_filename}_report.json"

    # Determine target directory
    if subfolder:
        target_dir = REPORTS_DIR / subfolder
    else:
        target_dir = REPORTS_DIR

    filepath = target_dir / filename

    # Ensure target directory exists
    target_dir.mkdir(parents=True, exist_ok=True)

    # Save with pretty formatting
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    return str(filepath)


def _format_gate_status(status: Optional[bool]) -> str:
    """Format gate status for display."""
    if status is None:
        return "❓ Cannot Determine (Threshold TBD)"
    elif status:
        return "✓ PASS"
    else:
        return "✗ FAIL"


# ============================================================================
# RETRY/CONTINUE FUNCTIONALITY
# ============================================================================


def continue_analysis(
    content: str,
    content_id: str,
    previous_report_path: str,
    save_report: bool = True,
) -> Tuple[Dict, str]:
    """
    Continue a previous analysis by retrying failed agents only.
    Useful for recovering from temporary API errors.

    Args:
        content: The draft content (same as original)
        content_id: Content identifier
        previous_report_path: Path to the previous report JSON
        save_report: Whether to save the updated report

    Returns:
        Tuple of (updated_report_dict, report_path)
    """
    print("\n" + "=" * 70)
    print(f"CONTINUING ANALYSIS: {content_id}")
    print("=" * 70)

    # Load previous report
    print(f"\nLoading previous report from: {previous_report_path}")
    with open(previous_report_path, "r", encoding="utf-8") as f:
        previous_report = json.load(f)

    # Extract Layer 1 flags from previous report
    layer_1_flags = []
    # Layer 1 flags are stored in 2A_Mechanical sub-parameter
    mechanical_flags = (
        previous_report.get("parameters", {})
        .get("P2_Brand_Hygiene", {})
        .get("sub_parameters", {})
        .get("2A_Mechanical", {})
        .get("flags", [])
    )
    if mechanical_flags:
        layer_1_flags = mechanical_flags

    # Reconstruct Layer 2 results from report
    # This is a bit complex as we need to reverse-engineer the structure
    print("\n[RETRY] Identifying failed agents from previous run...")
    layer_2_results = {}

    for param_id, param_data in previous_report.get("parameters", {}).items():
        for agent_id, sub_data in param_data.get("sub_parameters", {}).items():
            if agent_id == "2A_Mechanical":
                # Skip Layer 1 results
                continue

            # Check if this agent had an error
            feedback = sub_data.get("feedback", "")
            if feedback.startswith("ERROR:"):
                # Failed agent
                layer_2_results[agent_id] = {
                    "agent_id": agent_id,
                    "success": False,
                    "error": feedback.replace("ERROR: ", ""),
                }
            else:
                # Successful agent - preserve original result
                layer_2_results[agent_id] = {
                    "agent_id": agent_id,
                    "success": True,
                    "score": sub_data.get("score"),
                    "feedback": sub_data.get("feedback", ""),
                    "flags": sub_data.get("flags", []),
                }

    # Retry failed agents
    retry_results = retry_failed(content, layer_2_results)

    # Merge retry results back into layer_2_results
    layer_2_results.update(retry_results)

    # ========================================================================
    # SCORER: REGENERATE REPORT
    # ========================================================================
    print("\n[SCORER] Regenerating report with updated results...")
    updated_report = generate_report(content_id, layer_1_flags, layer_2_results)

    # Display summary
    print("\n" + "=" * 70)
    print("RETRY COMPLETE")
    print("=" * 70)
    print(f"Overall Score: {updated_report['results']['overall_score']}")
    print(f"Status: {updated_report['results']['status']}")
    print(f"Publish-Ready: {updated_report['results']['publish_ready']}")
    print("=" * 70 + "\n")

    # Save updated report
    if save_report:
        report_path = save_report_to_file(updated_report, content_id)
        print(f"Updated report saved to: {report_path}")
    else:
        report_path = None

    return updated_report, report_path


# ============================================================================
# BATCH PROCESSING
# ============================================================================


def analyze_batch(content_dir: Path) -> Dict[str, str]:
    """
    Analyze multiple content files in a directory.

    Args:
        content_dir: Directory containing content files (.txt or .md)

    Returns:
        Dictionary mapping content_id to report_path
    """
    # Find all text files
    files = list(content_dir.glob("*.txt")) + list(content_dir.glob("*.md"))

    if not files:
        print(f"No content files found in {content_dir}")
        return {}

    # Detect subfolder from source directory name
    subfolder = None
    dir_name = content_dir.name
    if "golden" in dir_name.lower():
        subfolder = "golden_set"
    elif "poison" in dir_name.lower():
        subfolder = "poison_set"

    print(f"\n{'=' * 70}")
    print(f"BATCH ANALYSIS: {len(files)} file(s)")
    if subfolder:
        print(f"Reports will be saved to: reports/{subfolder}/")
    print(f"{'=' * 70}\n")

    results = {}

    for i, filepath in enumerate(files, 1):
        content_id = filepath.stem
        print(f"\n[{i}/{len(files)}] Processing: {content_id}")

        try:
            # Load content
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            # Analyze with subfolder parameter
            report, report_path = analyze_content(content, content_id, save_report=True, subfolder=subfolder)
            results[content_id] = report_path

            # Add delay between files (except after last file)
            if i < len(files):
                print(f"\n  Waiting {DELAY_BETWEEN_FILES}s before next file...")
                time.sleep(DELAY_BETWEEN_FILES)

        except Exception as e:
            print(f"  ✗ Error processing {content_id}: {e}")
            results[content_id] = None

            # Still add delay even after errors (for rate limit safety)
            if i < len(files):
                print(f"\n  Waiting {DELAY_BETWEEN_FILES}s before next file...")
                time.sleep(DELAY_BETWEEN_FILES)

    print(f"\n{'=' * 70}")
    print(f"BATCH COMPLETE: {len(results)} file(s) processed")
    print(f"{'=' * 70}\n")

    return results
