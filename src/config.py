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
# Generous limit to allow detailed feedback and violation lists
MAX_TOKENS = 1000  # Configurable

# API retry configuration
MAX_RETRIES = 3  # Number of retry attempts for failed API calls
RETRY_DELAY = 2  # Initial delay in seconds (exponential backoff)

# ============================================================================
# RATE LIMITING CONFIGURATION (Tier 1)
# ============================================================================

# Tier 1 Rate Limits (as per Claude API docs)
RPM_LIMIT = 50  # Requests per minute
ITPM_LIMIT = 30000  # Input tokens per minute
OTPM_LIMIT = 8000  # Output tokens per minute

# Conservative rate limiting for parallel execution
# We're making 18 parallel calls, so we limit to batches
MAX_CONCURRENT_REQUESTS = 10  # Process in batches to avoid hitting RPM
REQUEST_DELAY = 1.2  # Delay between batches in seconds (conservative)

# ============================================================================
# SCORING WEIGHTS: 19 SUB-PARAMETERS
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
# P2: BRAND HYGIENE & COMPLIANCE (20% Total)
# ----------------------------------------------------------------------------
WEIGHTS_P2 = {
    "2A_Mechanical": 0.05,  # Mechanical Compliance (Layer 1 Regex)
    "2B_Contextual": 0.10,  # Contextual Terminology (Tool Paradox Logic)
    "2C_Persona": 0.05,  # Persona & Lexicon
}
# Verify: 0.05 + 0.10 + 0.05 = 0.20 ✓

# ----------------------------------------------------------------------------
# P3: STRUCTURAL INTEGRITY & CLARITY (25% Total)
# ----------------------------------------------------------------------------
WEIGHTS_P3 = {
    "3A_BLUF": 0.10,  # Bottom Line Up Front (CRITICAL)
    "3B_Scannability": 0.03,  # Scannability & Hierarchy
    "3C_Conciseness": 0.05,  # Conciseness (Fluff-Free Mandate)
    "3D_Specificity": 0.02,  # Specificity
    "3E_Human_Language": 0.05,  # Human Language/No Jargon
}
# Verify: 0.10 + 0.03 + 0.05 + 0.02 + 0.05 = 0.25 ✓

# ----------------------------------------------------------------------------
# P4: STRATEGIC VALUE & DEPTH (15% Total)
# ----------------------------------------------------------------------------
WEIGHTS_P4 = {
    "4A_Audience": 0.03,  # Audience Alignment (Sales Leaders/CRM)
    "4B_Actionability": 0.05,  # Actionability (Clear Takeaway/CTA)
    "4C_Evidence": 0.02,  # Evidence & Examples
    "4D_Originality": 0.05,  # Originality & AI Detection
}
# Verify: 0.03 + 0.05 + 0.02 + 0.05 = 0.15 ✓

# ----------------------------------------------------------------------------
# P5: ENGAGEMENT & DISCOVERABILITY (10% Total)
# ----------------------------------------------------------------------------
WEIGHTS_P5 = {
    "5A_Headline": 0.05,  # Headline & Hook (Attention Capture)
    "5B_SEO": 0.03,  # SEO Alignment
    "5C_Shareability": 0.02,  # Shareability
}
# Verify: 0.05 + 0.03 + 0.02 = 0.10 ✓

# ----------------------------------------------------------------------------
# PARAMETER-LEVEL WEIGHTS (Second Level Aggregation)
# ----------------------------------------------------------------------------
WEIGHTS_PARAMETERS = {
    "P1_Challenger_Tone": 0.30,
    "P2_Brand_Hygiene": 0.20,
    "P3_Structural_Clarity": 0.25,
    "P4_Strategic_Value": 0.15,
    "P5_Engagement": 0.10,
}
# Verify: 0.30 + 0.20 + 0.25 + 0.15 + 0.10 = 1.00 ✓

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
        "name": "Conciseness",
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
    "3E_Human_Language": {
        "name": "Human Language/No Jargon",
        "parameter": "P3_Structural_Clarity",
        "weight": WEIGHTS_P3["3E_Human_Language"],
        "prompt_file": "3E_Human_Language.txt",
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
        "name": "SEO Alignment",
        "parameter": "P5_Engagement",
        "weight": WEIGHTS_P5["5B_SEO"],
        "prompt_file": "5B_SEO.txt",
        "requires_llm": True,
    },
    "5C_Shareability": {
        "name": "Shareability",
        "parameter": "P5_Engagement",
        "weight": WEIGHTS_P5["5C_Shareability"],
        "prompt_file": "5C_Shareability.txt",
        "requires_llm": True,
    },
}

# ============================================================================
# SCORING THRESHOLDS (3-GATE SYSTEM)
# ============================================================================
# NOTE: These thresholds will be determined after calibration with golden/poison sets
# Placeholder values provided for initial testing

# Gate 1: Overall weighted score threshold
GATE_1_THRESHOLD = None  # TBD after calibration (initial hypothesis: 3.2)

# Gate 2: Tone minimum threshold (The "Boredom Veto")
GATE_2_TONE_MINIMUM = None  # TBD after calibration (initial hypothesis: 3.0)

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
