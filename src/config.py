"""
Configuration file for the AI Content Scoring Agent.
Contains all weights, thresholds, and API settings.
"""

import os
from pathlib import Path

# ============================================================================
# PROJECT PATHS
# ============================================================================

# Get the root directory (parent of src/)
ROOT_DIR = Path(__file__).parent.parent

# Data directories
DATA_DIR = ROOT_DIR / "data"
INPUT_DIR = DATA_DIR / "input"
REPORTS_DIR = DATA_DIR / "reports"
CALIBRATION_DIR = DATA_DIR / "calibration"
GOLDEN_SET_DIR = CALIBRATION_DIR / "golden_set"
POISON_SET_DIR = CALIBRATION_DIR / "poison_set"

# Prompts directory
PROMPTS_DIR = ROOT_DIR / "prompts"

# Ensure directories exist
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================================
# CLAUDE API CONFIGURATION
# ============================================================================

# Model configuration
MODEL_NAME = "claude-sonnet-4-5-20250929"  # Claude Sonnet 4.5

# Temperature setting (range: 0.0 to 1.0)
# 0.0 = Maximum determinism (recommended for evaluation tasks)
# 1.0 = Maximum creativity
TEMPERATURE = 0.0  # Configurable for testing

# Max tokens for LLM responses
# Generous limit to allow detailed feedback, thinking, and violation lists
MAX_TOKENS = 2000  # Configurable

# API retry configuration
MAX_RETRIES = 3  # Number of retry attempts for failed API calls
RETRY_DELAY = 2  # Initial delay in seconds (exponential backoff)

# ============================================================================
# RATE LIMITING CONFIGURATION (Sequential Execution)
# ============================================================================

# Tier 1 Rate Limits (as per Claude API docs)
RPM_LIMIT = 50  # Requests per minute
ITPM_LIMIT = 30000  # Input tokens per minute
OTPM_LIMIT = 8000  # Output tokens per minute

# Sequential execution settings (safer for rate limits)
DELAY_BETWEEN_AGENT_CALLS = 2.0  # 2 seconds between each of 16 agent API calls
DELAY_BETWEEN_FILES = 5.0        # 5 seconds between each file in batch processing
RATE_LIMIT_BACKOFF = 60.0        # 60 seconds wait if rate limit error detected

# ============================================================================
# SCORING WEIGHTS: 17 SUB-PARAMETERS (v6.0)
# ============================================================================
# All weights are expressed as decimals (0.10 = 10%)
# Total weights per parameter must sum to the parameter's total weight

# ----------------------------------------------------------------------------
# P1: CHALLENGER TONE & VOICE (30% Total)
# ----------------------------------------------------------------------------
WEIGHTS_P1 = {
    "1A_Positive": 0.05,  # Positive & Solution-Focused
    "1B_Direct": 0.10,  # Direct with Personality (CORE)
    "1C_Trustworthy": 0.05,  # Trustworthy & Authentic
    "1D_Sharp_Wit": 0.10,  # Sharp Wit & Confidence (SPICY FACTOR)
}
# Verify: 0.05 + 0.10 + 0.05 + 0.10 = 0.30 ✓

# ----------------------------------------------------------------------------
# P2: BRAND HYGIENE & COMPLIANCE (5% Total)
# ----------------------------------------------------------------------------
WEIGHTS_P2 = {
    "2A_Mechanical": 0.02,  # Mechanical Compliance (Layer 1 Regex)
    "2B_Contextual": 0.02,  # Contextual Terminology (Referent Analysis)
    "2C_Persona": 0.01,  # Persona & Lexicon (Customers/Managers/Ad Hominem)
}
# Verify: 0.02 + 0.02 + 0.01 = 0.05 ✓

# ----------------------------------------------------------------------------
# P3: STRUCTURAL INTEGRITY & CLARITY (25% Total)
# ----------------------------------------------------------------------------
WEIGHTS_P3 = {
    "3A_BLUF": 0.10,  # Bottom Line Up Front (CRITICAL)
    "3B_Scannability": 0.05,  # Scannability & Hierarchy
    "3C_Conciseness": 0.05,  # Conciseness & Human Language (combined)
    "3D_Specificity": 0.05,  # Specificity
}
# Verify: 0.10 + 0.05 + 0.05 + 0.05 = 0.25 ✓

# ----------------------------------------------------------------------------
# P4: STRATEGIC VALUE & DEPTH (30% Total - DOUBLED)
# ----------------------------------------------------------------------------
WEIGHTS_P4 = {
    "4A_Audience": 0.10,  # Audience Alignment (Sales Leaders/CRM)
    "4B_Actionability": 0.10,  # Actionability (Clear Takeaway/CTA)
    "4C_Evidence": 0.05,  # Evidence & Examples
    "4D_Originality": 0.05,  # Originality & AI Detection
}
# Verify: 0.10 + 0.10 + 0.05 + 0.05 = 0.30 ✓

# ----------------------------------------------------------------------------
# P5: ENGAGEMENT & DISCOVERABILITY (10% Total)
# ----------------------------------------------------------------------------
WEIGHTS_P5 = {
    "5A_Headline": 0.05,  # Headline & Hook (Attention Capture)
    "5B_SEO": 0.05,  # SEO & Shareability (combined)
}
# Verify: 0.05 + 0.05 = 0.10 ✓

# ----------------------------------------------------------------------------
# PARAMETER-LEVEL WEIGHTS (Second Level Aggregation - v6.0)
# ----------------------------------------------------------------------------
WEIGHTS_PARAMETERS = {
    "P1_Challenger_Tone": 0.30,
    "P2_Brand_Hygiene": 0.05,      # Reduced but retains Gate 3 veto power
    "P3_Structural_Clarity": 0.25,
    "P4_Strategic_Value": 0.30,    # Doubled - Substance = Style
    "P5_Engagement": 0.10,
}
# Verify: 0.30 + 0.05 + 0.25 + 0.30 + 0.10 = 1.00 ✓

# ============================================================================
# COMPLETE SUB-PARAMETER REGISTRY
# ============================================================================
# Maps agent IDs to their metadata for orchestration
SUB_PARAMETERS = {
    # P1: Challenger Tone & Voice
    "1A_Positive": {
        "name": "Positive & Solution-Focused",
        "parameter": "P1_Challenger_Tone",
        "weight": WEIGHTS_P1["1A_Positive"],
        "prompt_file": "1A_Positive.txt",
        "requires_llm": True,
    },
    "1B_Direct": {
        "name": "Direct with Personality",
        "parameter": "P1_Challenger_Tone",
        "weight": WEIGHTS_P1["1B_Direct"],
        "prompt_file": "1B_Direct.txt",
        "requires_llm": True,
    },
    "1C_Trustworthy": {
        "name": "Trustworthy & Authentic",
        "parameter": "P1_Challenger_Tone",
        "weight": WEIGHTS_P1["1C_Trustworthy"],
        "prompt_file": "1C_Trustworthy.txt",
        "requires_llm": True,
    },
    "1D_Sharp_Wit": {
        "name": "Sharp Wit & Confidence",
        "parameter": "P1_Challenger_Tone",
        "weight": WEIGHTS_P1["1D_Sharp_Wit"],
        "prompt_file": "1D_Sharp_Wit.txt",
        "requires_llm": True,
    },
    # P2: Brand Hygiene & Compliance
    "2A_Mechanical": {
        "name": "Mechanical Compliance",
        "parameter": "P2_Brand_Hygiene",
        "weight": WEIGHTS_P2["2A_Mechanical"],
        "prompt_file": None,  # Uses Layer 1 Regex
        "requires_llm": False,
    },
    "2B_Contextual": {
        "name": "Contextual Terminology",
        "parameter": "P2_Brand_Hygiene",
        "weight": WEIGHTS_P2["2B_Contextual"],
        "prompt_file": "2B_Contextual_Terminology.txt",
        "requires_llm": True,
    },
    "2C_Persona": {
        "name": "Persona & Lexicon",
        "parameter": "P2_Brand_Hygiene",
        "weight": WEIGHTS_P2["2C_Persona"],
        "prompt_file": "2C_Persona_Lexicon.txt",
        "requires_llm": True,
    },
    # P3: Structural Integrity & Clarity
    "3A_BLUF": {
        "name": "Bottom Line Up Front",
        "parameter": "P3_Structural_Clarity",
        "weight": WEIGHTS_P3["3A_BLUF"],
        "prompt_file": "3A_BLUF.txt",
        "requires_llm": True,
    },
    "3B_Scannability": {
        "name": "Scannability & Hierarchy",
        "parameter": "P3_Structural_Clarity",
        "weight": WEIGHTS_P3["3B_Scannability"],
        "prompt_file": "3B_Scannability.txt",
        "requires_llm": True,
    },
    "3C_Conciseness": {
        "name": "Conciseness & Human Language",
        "parameter": "P3_Structural_Clarity",
        "weight": WEIGHTS_P3["3C_Conciseness"],
        "prompt_file": "3C_Conciseness.txt",
        "requires_llm": True,
    },
    "3D_Specificity": {
        "name": "Specificity",
        "parameter": "P3_Structural_Clarity",
        "weight": WEIGHTS_P3["3D_Specificity"],
        "prompt_file": "3D_Specificity.txt",
        "requires_llm": True,
    },
    # P4: Strategic Value & Depth
    "4A_Audience": {
        "name": "Audience Alignment",
        "parameter": "P4_Strategic_Value",
        "weight": WEIGHTS_P4["4A_Audience"],
        "prompt_file": "4A_Audience_Alignment.txt",
        "requires_llm": True,
    },
    "4B_Actionability": {
        "name": "Actionability",
        "parameter": "P4_Strategic_Value",
        "weight": WEIGHTS_P4["4B_Actionability"],
        "prompt_file": "4B_Actionability.txt",
        "requires_llm": True,
    },
    "4C_Evidence": {
        "name": "Evidence & Examples",
        "parameter": "P4_Strategic_Value",
        "weight": WEIGHTS_P4["4C_Evidence"],
        "prompt_file": "4C_Evidence.txt",
        "requires_llm": True,
    },
    "4D_Originality": {
        "name": "Originality & AI Detection",
        "parameter": "P4_Strategic_Value",
        "weight": WEIGHTS_P4["4D_Originality"],
        "prompt_file": "4D_Originality.txt",
        "requires_llm": True,
    },
    # P5: Engagement & Discoverability
    "5A_Headline": {
        "name": "Headline & Hook",
        "parameter": "P5_Engagement",
        "weight": WEIGHTS_P5["5A_Headline"],
        "prompt_file": "5A_Headline_Hook.txt",
        "requires_llm": True,
    },
    "5B_SEO": {
        "name": "SEO & Shareability",
        "parameter": "P5_Engagement",
        "weight": WEIGHTS_P5["5B_SEO"],
        "prompt_file": "5B_SEO.txt",
        "requires_llm": True,
    },
}

# ============================================================================
# SCORING THRESHOLDS (3-GATE SYSTEM)
# ============================================================================
# NOTE: These thresholds are calibrated based on scoring good content

# Gate 1: Overall weighted score threshold
GATE_1_THRESHOLD = 2.36  # Calibrated based on scoring good content

# Gate 2: Tone minimum threshold (The "Boredom Veto")
GATE_2_TONE_MINIMUM = 2.51  # Calibrated based on scoring good content

# Gate 3: Zero critical violations (enforced programmatically, no threshold)
# Any critical violation from Layer 1 or Agent 2B = automatic failure

# ============================================================================
# SCORING SCALE DEFINITIONS
# ============================================================================
SCORE_SCALE = {
    1: {
        "label": "Critical Fail",
        "description": "Active brand violation, toxic tone, or factually incorrect.",
    },
    2: {
        "label": "Generic (Mediocre)",
        "description": "Grammatically correct but boring. Lacks challenger voice.",
    },
    3: {
        "label": "Publishable Standard",
        "description": "Clear, helpful, professional. Meets the human standard.",
    },
    4: {
        "label": "Challenger Status",
        "description": "Exceptional. Unique insight, witty, distinct voice, zero fluff.",
    },
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def get_llm_agents():
    """Return list of agent IDs that require LLM calls."""
    return [
        agent_id
        for agent_id, meta in SUB_PARAMETERS.items()
        if meta["requires_llm"]
    ]


def get_agent_metadata(agent_id):
    """Get metadata for a specific agent."""
    return SUB_PARAMETERS.get(agent_id)


def get_parameter_agents(parameter_id):
    """Get all agent IDs belonging to a specific parameter."""
    return [
        agent_id
        for agent_id, meta in SUB_PARAMETERS.items()
        if meta["parameter"] == parameter_id
    ]


# Validation: Ensure all weights sum correctly
def validate_weights():
    """Validate that all weight configurations are correct."""
    errors = []

    # Check sub-parameter weights sum to parameter totals
    for param_id, param_weight in WEIGHTS_PARAMETERS.items():
        agents = get_parameter_agents(param_id)
        total = sum(SUB_PARAMETERS[agent]["weight"] for agent in agents)
        if abs(total - param_weight) > 0.001:  # Allow for floating point errors
            errors.append(
                f"{param_id}: Sub-parameters sum to {total}, expected {param_weight}"
            )

    # Check parameter weights sum to 1.0
    param_total = sum(WEIGHTS_PARAMETERS.values())
    if abs(param_total - 1.0) > 0.001:
        errors.append(f"Parameter weights sum to {param_total}, expected 1.0")

    if errors:
        raise ValueError(f"Weight validation failed:\n" + "\n".join(errors))

    return True


# Run validation on import
validate_weights()
