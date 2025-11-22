"""
Scorer Module: Two-level aggregation and 3-Gate decision logic.
Combines Layer 1 (Regex) and Layer 2 (LLM) results into final report.
"""

from datetime import datetime
from typing import Dict, List, Optional

from config import (
    SUB_PARAMETERS,
    WEIGHTS_PARAMETERS,
    GATE_1_THRESHOLD,
    GATE_2_TONE_MINIMUM,
    SCORE_SCALE,
    get_parameter_agents,
)


# ============================================================================
# TWO-LEVEL AGGREGATION
# ============================================================================


def calculate_parameter_score(
    parameter_id: str, sub_results: Dict[str, Dict]
) -> Dict:
    """
    Calculate the aggregated score for a single parameter (P1-P5)
    based on its sub-parameter results.

    Args:
        parameter_id: Parameter identifier (e.g., "P1_Challenger_Tone")
        sub_results: Dictionary of all sub-parameter results

    Returns:
        Dictionary with parameter score and sub-parameter breakdown
    """
    agent_ids = get_parameter_agents(parameter_id)

    sub_parameter_scores = {}
    total_weighted_score = 0.0
    total_weight = 0.0
    has_failures = False

    for agent_id in agent_ids:
        metadata = SUB_PARAMETERS[agent_id]
        weight = metadata["weight"]

        # Get result for this agent
        if agent_id in sub_results:
            result = sub_results[agent_id]

            if result.get("success", False):
                # Successful LLM call
                score = result["score"]
                feedback = result["feedback"]
                flags = result.get("flags", [])
            else:
                # Failed agent - mark as failed
                score = None
                feedback = f"ERROR: {result.get('error', 'Unknown error')}"
                flags = []
                has_failures = True
        else:
            # Missing result (shouldn't happen, but handle gracefully)
            score = None
            feedback = "ERROR: No result found for this agent"
            flags = []
            has_failures = True

        # Add to sub-parameter breakdown
        sub_parameter_scores[agent_id] = {
            "name": metadata["name"],
            "score": score,
            "weight": weight,
            "feedback": feedback,
            "flags": flags,
        }

        # Include in weighted calculation only if score exists
        if score is not None:
            total_weighted_score += score * weight
            total_weight += weight

    # Calculate parameter score (weighted average of successful sub-parameters)
    if total_weight > 0:
        parameter_score = total_weighted_score / total_weight
    else:
        # All agents failed - no valid score
        parameter_score = None

    return {
        "parameter_score": parameter_score,
        "weight": WEIGHTS_PARAMETERS[parameter_id],
        "sub_parameters": sub_parameter_scores,
        "has_failures": has_failures,
    }


def calculate_overall_score(parameter_scores: Dict[str, Dict]) -> Optional[float]:
    """
    Calculate the final overall score based on parameter-level scores.

    Args:
        parameter_scores: Dictionary of parameter results

    Returns:
        Overall weighted score, or None if calculation impossible
    """
    total_weighted_score = 0.0
    total_weight = 0.0

    for param_id, param_data in parameter_scores.items():
        score = param_data["parameter_score"]
        weight = param_data["weight"]

        if score is not None:
            total_weighted_score += score * weight
            total_weight += weight

    if total_weight > 0:
        return total_weighted_score / total_weight
    else:
        return None


# ============================================================================
# 3-GATE DECISION LOGIC
# ============================================================================


def evaluate_gates(
    overall_score: Optional[float],
    parameter_scores: Dict[str, Dict],
    layer_1_flags: List[Dict],
) -> Dict:
    """
    Apply the 3-Gate system to determine publish-ready status.

    Args:
        overall_score: Final aggregated score
        parameter_scores: Parameter-level results
        layer_1_flags: Layer 1 (Regex) violation flags

    Returns:
        Dictionary with gate status and publish-ready decision
    """
    # Gate 1: Overall threshold
    if GATE_1_THRESHOLD is not None and overall_score is not None:
        gate_1_pass = overall_score >= GATE_1_THRESHOLD
    else:
        # Threshold not set (TBD after calibration) - cannot evaluate
        gate_1_pass = None

    # Gate 2: Tone minimum (Boredom Veto)
    tone_score = parameter_scores.get("P1_Challenger_Tone", {}).get("parameter_score")
    if GATE_2_TONE_MINIMUM is not None and tone_score is not None:
        gate_2_pass = tone_score >= GATE_2_TONE_MINIMUM
    else:
        # Threshold not set or tone score missing - cannot evaluate
        gate_2_pass = None

    # Gate 3: Brand Veto (Zero critical violations)
    # Check Layer 1 flags
    layer_1_critical = [f for f in layer_1_flags if f["severity"] == "Critical"]

    # Check Layer 2 Agent 2B (Contextual Terminology) for critical flags
    agent_2b_result = parameter_scores.get("P2_Brand_Hygiene", {}).get(
        "sub_parameters", {}
    ).get("2B_Contextual", {})
    agent_2b_flags = agent_2b_result.get("flags", [])
    agent_2b_critical = [f for f in agent_2b_flags if isinstance(f, dict) and f.get("severity") == "Critical"]

    gate_3_pass = len(layer_1_critical) == 0 and len(agent_2b_critical) == 0

    # Determine publish-ready status
    # Can only be True if ALL gates pass
    if gate_1_pass is True and gate_2_pass is True and gate_3_pass is True:
        publish_ready = True
        status = "Publish-Ready"
    elif gate_1_pass is False or gate_2_pass is False or gate_3_pass is False:
        publish_ready = False
        # Determine specific failure reason
        if not gate_3_pass:
            status = "Critical Violations (Brand Veto)"
        elif gate_2_pass is False:
            status = "Tone Too Generic (Boredom Veto)"
        elif gate_1_pass is False:
            status = "Below Quality Threshold"
        else:
            status = "Failed Gates"
    else:
        # At least one gate is None (thresholds not set)
        publish_ready = None
        status = "Cannot Determine (Thresholds TBD)"

    return {
        "gate_1_overall_threshold_met": gate_1_pass,
        "gate_2_tone_veto_passed": gate_2_pass,
        "gate_3_brand_veto_passed": gate_3_pass,
        "publish_ready": publish_ready,
        "status": status,
        "critical_violations_count": len(layer_1_critical) + len(agent_2b_critical),
    }


# ============================================================================
# COMPREHENSIVE JSON REPORT GENERATION
# ============================================================================


def generate_report(
    content_id: str,
    layer_1_flags: List[Dict],
    layer_2_results: Dict[str, Dict],
) -> Dict:
    """
    Generate the complete JSON report combining all analysis results.

    Args:
        content_id: Identifier for the content (e.g., filename)
        layer_1_flags: Violation flags from regex checks
        layer_2_results: Results from all LLM agents

    Returns:
        Complete report dictionary (ready for JSON serialization)
    """
    # Combine Layer 1 results with Layer 2 results
    # Layer 1 contributes to 2A_Mechanical
    all_results = dict(layer_2_results)  # Copy Layer 2 results

    # Add Layer 1 as 2A_Mechanical result
    all_results["2A_Mechanical"] = {
        "agent_id": "2A_Mechanical",
        "success": True,
        "score": 4 if len(layer_1_flags) == 0 else 1,  # Perfect or fail
        "feedback": (
            "No mechanical violations found."
            if len(layer_1_flags) == 0
            else f"Found {len(layer_1_flags)} mechanical violation(s)."
        ),
        "flags": layer_1_flags,
    }

    # Calculate parameter-level scores
    parameter_scores = {}
    for param_id in WEIGHTS_PARAMETERS.keys():
        parameter_scores[param_id] = calculate_parameter_score(param_id, all_results)

    # Calculate overall score
    overall_score = calculate_overall_score(parameter_scores)

    # Evaluate 3-Gate system
    gates_result = evaluate_gates(overall_score, parameter_scores, layer_1_flags)

    # Build parameter breakdown for report
    parameters_report = {}
    for param_id, param_data in parameter_scores.items():
        # Calculate contribution to overall score
        if param_data["parameter_score"] is not None and overall_score is not None:
            contribution = param_data["parameter_score"] * param_data["weight"]
        else:
            contribution = None

        # Build sub-parameters section
        sub_params_report = {}
        for agent_id, sub_data in param_data["sub_parameters"].items():
            sub_params_report[agent_id] = {
                "name": sub_data["name"],
                "score": sub_data["score"],
                "weight": sub_data["weight"],
                "feedback": sub_data["feedback"],
            }
            # Only include flags if they exist and are non-empty
            if sub_data["flags"]:
                sub_params_report[agent_id]["flags"] = sub_data["flags"]

        parameters_report[param_id] = {
            "parameter_score": param_data["parameter_score"],
            "weight": param_data["weight"],
            "contribution": contribution,
            "sub_parameters": sub_params_report,
        }

    # Build complete report
    report = {
        "metadata": {
            "content_id": content_id,
            "timestamp": datetime.now().isoformat(),
            "model_used": "claude-sonnet-4-5-20250929",
            "threshold_gate_1": GATE_1_THRESHOLD,
            "threshold_gate_2_tone": GATE_2_TONE_MINIMUM,
        },
        "results": {
            "overall_score": round(overall_score, 2) if overall_score is not None else None,
            "publish_ready": gates_result["publish_ready"],
            "status": gates_result["status"],
        },
        "gates_status": {
            "gate_1_overall_threshold_met": gates_result["gate_1_overall_threshold_met"],
            "gate_2_tone_veto_passed": gates_result["gate_2_tone_veto_passed"],
            "gate_3_brand_veto_passed": gates_result["gate_3_brand_veto_passed"],
            "critical_violations_count": gates_result["critical_violations_count"],
        },
        "parameters": parameters_report,
    }

    return report


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def format_score_label(score: Optional[int]) -> str:
    """Get the human-readable label for a score."""
    if score is None:
        return "N/A"
    return SCORE_SCALE.get(score, {}).get("label", "Unknown")


def count_violations_by_severity(flags: List[Dict]) -> Dict[str, int]:
    """Count violations by severity level."""
    counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    for flag in flags:
        severity = flag.get("severity", "Unknown")
        if severity in counts:
            counts[severity] += 1
    return counts
